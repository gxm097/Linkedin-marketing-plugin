# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///
"""Tells Claude when the weekly carousel, or a mention check, is due.

Run as ``uv run --locked --script nudge.py carousel`` or ``... mentions``.

This replaces two bash scripts, and the reason is Windows. The hooks ran as
``"command": "bash"`` with ``args``, which is the exec form, and the hooks
reference says exec form on Windows needs ``command`` to resolve to a real
executable -- while ``shell`` is "Ignored when ``args`` is set", so there is no
``"shell": "powershell"`` escape. Git for Windows is optional for Claude Code,
so ``bash`` may not exist at all; where it does, the recommended installer puts
only ``Git\\cmd`` on PATH and ``bash.exe`` lives in ``Git\\bin``. The failure is
a silent exit 127 -- no nudge, ever, with nothing printed to say so.

``uv`` is already required to run the LinkedIn MCP server, ``uv.exe`` is a real
PATH executable, and exec form hands the backslashed plugin path over as one
argv element that no shell tokenizes. So this file needs no interpreter the
client has to install and no shell at all.

Both checks run on **every** session start in **every** project on the machine,
so going quiet when they are not wanted matters more than anything else they
do. Anything on stdout is injected into the conversation; uv keeps its own
chatter on stderr, so stdout here is only ever what this script prints.

Neither check offers to post. The mention check stops and asks before any
comment is written, because a comment is a write to a real account.
"""

import json
import os
import re
import sys
import time
from datetime import datetime
from pathlib import Path

#: A ``posts/`` folder name, which must *start* with the date.
_DATE = re.compile(r"^(\d{4}-\d{2}-\d{2})")
#: A log's date heading. ``##`` then optional blanks then the date, so an h3
#: inside an entry cannot be mistaken for the heading of a later check.
_LOG_DATE = re.compile(r"^##[ \t]*(\d{4}-\d{2}-\d{2})")


def project_dir() -> Path:
    return Path(os.environ.get("CLAUDE_PROJECT_DIR") or os.getcwd())


def option(name: str, default: str) -> str:
    """Read a plugin option, treating an empty value as absent."""
    return os.environ.get(f"CLAUDE_PLUGIN_OPTION_{name}") or default


def cadence(name: str, default: int = 7) -> int:
    """A cadence option, falling back on anything that is not a whole number.

    A junk value must not silence the reminder: the bash versions matched
    ``*[!0-9]*`` and fell back to 7, and a config that cannot be parsed is
    still a config whose owner expects to be reminded.
    """
    raw = option(name, "")
    return int(raw) if raw.isdigit() else default


def days_since(day: str) -> int | None:
    """Whole days from local midnight on ``day`` until now.

    ``time.mktime`` rather than a naive subtraction, to match what
    ``date -d`` computed: it resolves the date in local time, so a run that
    straddles a DST change counts the same days a calendar would.
    """
    try:
        parsed = datetime.strptime(day, "%Y-%m-%d")
    except ValueError:
        return None
    return int((time.time() - time.mktime(parsed.timetuple())) // 86400)


def newest_log_date(log: Path) -> str:
    """The newest ``## YYYY-MM-DD`` heading in a log, or "".

    The date comes from the log rather than a stamp file for the same reason
    the carousel reads the posts folder: the log is the actual record of what
    went out, so it cannot drift out of sync, and it stays per-project when one
    marketer runs several clients in several folders.
    """
    if not log.is_file():
        return ""
    dates = [
        found.group(1)
        for line in log.read_text(encoding="utf-8", errors="replace").splitlines()
        if (found := _LOG_DATE.match(line))
    ]
    return max(dates, default="")


def say(text: str) -> None:
    print(text)


def carousel(project: Path) -> None:
    posts = project / option("POSTS_DIR", "posts/").rstrip("/\\")

    # The last post date comes from the newest posts/YYYY-MM-DD-<slug>/ folder
    # rather than a stamp file: it cannot drift out of sync with the actual
    # output, and it stays per-project.
    #
    # A folder only counts as a finished week if the deliverable is in it. A run
    # that got as far as the copy but never produced a graphic (Canva down, or
    # interrupted) leaves a dated folder behind, and counting that as done would
    # silence the reminder for a week that never shipped.
    last = unfinished = ""
    if posts.is_dir():
        for entry in sorted(posts.iterdir()):
            if not entry.is_dir() or not _DATE.match(entry.name):
                continue
            day = entry.name[:10]
            if (entry / "carousel.pdf").is_file() or (entry / "image.png").is_file():
                last = max(last, day)
            else:
                unfinished = max(unfinished, day)

    if last:
        elapsed = days_since(last)
        if elapsed is None or elapsed < cadence("CADENCE_DAYS"):
            return
        when = f"The last one went out {elapsed} days ago ({last})."
    elif unfinished:
        when = (
            f"The last attempt ({unfinished}) never produced a finished graphic, "
            "so this week has not shipped."
        )
    else:
        when = "No post has been made in this project yet."

    if option("AUTO_START", "false").lower() in {"true", "1"}:
        # Begin the flow directly. initialUserMessage is a documented
        # SessionStart output field; if a future build stops honouring it the
        # plain-text branch still reaches the user, so this fails soft.
        say(
            json.dumps(
                {
                    "hookSpecificOutput": {
                        "hookEventName": "SessionStart",
                        "initialUserMessage": (
                            f"The weekly LinkedIn carousel is due. {when} Run "
                            "/linkedin-marketing:weekly-carousel now."
                        ),
                    }
                }
            )
        )
        return

    say(
        f"The weekly LinkedIn carousel for this project is due. {when} Early in "
        "your reply, tell the user it is due and offer to run "
        "/linkedin-marketing:weekly-carousel — do not start it without their "
        "go-ahead."
    )


_HEADING = re.compile(r"^##\s")
_MENTIONS_HEADING = re.compile(r"^##\s+Mentions\s*$", re.IGNORECASE)
_WATCH = re.compile(r"^-\s*\*\*Watch for mentions:\*\*\s*(.*)$", re.IGNORECASE)


def watching(config: Path) -> bool:
    """Whether the config switches mention watching on.

    Watching has to be switched on explicitly; a blank or "no" leaves it off.
    An existing config written before the feature existed has no Mentions
    section at all, and its owner never asked to be reminded about one.

    The parenthetical is dropped before the comparison. Setup writes the value
    with its own hint still attached -- ``yes (yes / no)`` -- so a parse that
    only trimmed whitespace compared ``yes(yes/no)`` against ``yes`` and read
    every config as switched off.
    """
    lines = config.read_text(encoding="utf-8", errors="replace").splitlines()
    start = next((i for i, line in enumerate(lines) if _MENTIONS_HEADING.match(line)), None)
    if start is None:
        return False
    for line in lines[start + 1 :]:
        if _HEADING.match(line):
            break
        if found := _WATCH.match(line):
            value = found.group(1).split("(")[0]
            return "".join(value.split()).lower() in {"yes", "true", "on"}
    return False


def mentions(project: Path) -> None:
    if not watching(project / "marketing-config.md"):
        return

    # 0 switches the reminder off, which plugin.json promises and the carousel
    # cadence deliberately does not offer.
    days = cadence("MENTION_CHECK_DAYS")
    if days <= 0:
        return

    # An absent log means no check has ever run here, which is itself due.
    last = newest_log_date(project / "mentions-log.md")
    if last:
        elapsed = days_since(last)
        if elapsed is None or elapsed < days:
            return
        when = f"The last check was {elapsed} days ago ({last})."
    else:
        when = "No mention check has run in this project yet."

    say(
        f"A LinkedIn mention check for this project is due. {when} Early in your "
        "reply, tell the user it is due and offer to run "
        "/linkedin-marketing:mention-comments — do not start it without their "
        "go-ahead, and never post a comment without their explicit approval of "
        "that comment."
    )


def main() -> int:
    which = sys.argv[1] if len(sys.argv) > 1 else ""
    project = project_dir()

    # Not a marketing project -> say nothing at all.
    if not (project / "marketing-config.md").is_file():
        return 0

    if which == "carousel":
        carousel(project)
    elif which == "mentions":
        mentions(project)
    else:
        # A hook misconfiguration. Report it on stderr, which is not injected
        # into the conversation, and exit clean so the session is unaffected.
        print(f"nudge.py: expected 'carousel' or 'mentions', got {which!r}", file=sys.stderr)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
