# /// script
# requires-python = ">=3.11"
# dependencies = ["pytest"]
# ///
"""Exercises hooks/nudge.py.

    uv run --script tests/test_nudge.py

Both checks run on **every** session start in **every** project on the machine,
so staying silent when they are not wanted matters more than anything else they
do. Most of these cases assert silence.

The config fixture is cut out of ``commands/linkedin-setup.md`` rather than
typed in here. That is deliberate: a hand-written fixture is a claim about the
template, and the two drifted once already -- the template emits
``**Watch for mentions:** yes (yes / no)`` and the hook was comparing the whole
string, hint included, against ``yes``, so every config read as switched off
while the test passed. Keep the fixture derived.

Each case shells out through ``uv run --script``, the way the hook itself is
invoked, so a mistake in the PEP 723 header or in argument handling fails here
rather than in a client's session.
"""

import re
import subprocess
import sys
import time
from datetime import date, timedelta
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent
NUDGE = ROOT / "linkedin-marketing" / "hooks" / "nudge.py"
SETUP = ROOT / "linkedin-marketing" / "commands" / "linkedin-setup.md"


def days_ago(n: int) -> str:
    return (date.today() - timedelta(days=n)).isoformat()


def run(which: str, project: Path, **options: str) -> str:
    """Run the hook the way hooks.json runs it, and return only its stdout.

    uv keeps its own progress chatter on stderr. Only stdout reaches the
    conversation, so only stdout is asserted on.
    """
    env = {
        "PATH": __import__("os").environ["PATH"],
        "HOME": __import__("os").environ.get("HOME", str(Path.home())),
        "CLAUDE_PROJECT_DIR": str(project),
    }
    env.update({f"CLAUDE_PLUGIN_OPTION_{k}": v for k, v in options.items()})
    done = subprocess.run(
        ["uv", "run", "--script", str(NUDGE), which],
        capture_output=True,
        text=True,
        env=env,
        timeout=120,
    )
    assert done.returncode == 0, f"exit {done.returncode}: {done.stderr}"
    return done.stdout.strip()


# --- fixtures cut from the template the setup command actually writes ---------


def template_mentions() -> str:
    """The Mentions block exactly as setup writes it."""
    text = SETUP.read_text(encoding="utf-8")
    found = re.search(
        r"^## Mentions$.*?^- \*\*Comment length.*?$", text, re.MULTILINE | re.DOTALL
    )
    assert found, "no Mentions block in the setup template"
    return found.group(0)


def test_the_template_still_has_a_mentions_block():
    block = template_mentions()
    assert "**Watch for mentions:**" in block
    # The parenthetical is the whole reason the hook strips one. If setup stops
    # writing it, the stripping is still correct but this fixture stops
    # exercising it, and that should be a visible change rather than a quiet one.
    assert "no (yes / no)" in block


@pytest.fixture
def project(tmp_path: Path) -> Path:
    return tmp_path


def write_config(project: Path, watch: str | None) -> None:
    """Write a config whose Mentions section is the template's own.

    ``watch`` is the value to substitute, or None to omit the section entirely.
    """
    head = "# Marketing Config\n\n## Company\n- **Name:** Cloud Range\n\n"
    body = ""
    if watch is not None:
        body = re.sub(
            r"^(- \*\*Watch for mentions:\*\*).*$",
            lambda m: f"{m.group(1)} {watch}".rstrip(),
            template_mentions(),
            flags=re.MULTILINE,
        )
    (project / "marketing-config.md").write_text(head + body, encoding="utf-8")


def write_log(project: Path, *dates: str) -> None:
    (project / "mentions-log.md").write_text(
        "".join(f"## {d}\n- commented on something\n" for d in dates), encoding="utf-8"
    )


def write_post(project: Path, day: str, graphic: str | None, posts: str = "posts") -> None:
    folder = project / posts / f"{day}-some-slug"
    folder.mkdir(parents=True)
    (folder / "post.md").write_text("copy", encoding="utf-8")
    if graphic:
        (folder / graphic).write_bytes(b"not really a graphic")


# --- mentions ----------------------------------------------------------------


def test_no_config_at_all_is_silent(project):
    assert run("mentions", project) == ""


def test_config_without_a_mentions_section_is_silent(project):
    write_config(project, None)
    assert run("mentions", project) == ""


def test_template_default_no_is_silent(project):
    write_config(project, "no (yes / no)")
    assert run("mentions", project) == ""


def test_blank_value_is_silent(project):
    write_config(project, "")
    assert run("mentions", project) == ""


def test_template_value_with_its_hint_attached_is_due(project):
    """The regression: setup writes "yes (yes / no)", not "yes"."""
    write_config(project, "yes (yes / no)")
    assert "No mention check has run" in run("mentions", project)


@pytest.mark.parametrize("value", ["yes", "Yes", "YES", "true", "on", "yes (yes / no)"])
def test_every_accepted_spelling_switches_it_on(project, value):
    write_config(project, value)
    assert "mention check" in run("mentions", project)


@pytest.mark.parametrize("value", ["no", "off", "maybe", "0", "nope (yes / no)"])
def test_anything_else_leaves_it_off(project, value):
    write_config(project, value)
    assert run("mentions", project) == ""


def test_checked_today_is_silent(project):
    write_config(project, "yes (yes / no)")
    write_log(project, days_ago(0))
    assert run("mentions", project) == ""


def test_nine_days_ago_against_a_seven_day_cadence_is_due(project):
    write_config(project, "yes (yes / no)")
    write_log(project, days_ago(9))
    assert "9 days ago" in run("mentions", project)


def test_two_days_ago_is_silent(project):
    write_config(project, "yes (yes / no)")
    write_log(project, days_ago(2))
    assert run("mentions", project) == ""


def test_newest_of_several_headings_wins(project):
    write_config(project, "yes (yes / no)")
    write_log(project, days_ago(60), days_ago(1))
    assert run("mentions", project) == ""


def test_an_h3_date_inside_an_entry_is_not_a_check(project):
    """Only ``## <date>`` is a check. An h3 must not stand in for one."""
    write_config(project, "yes (yes / no)")
    (project / "mentions-log.md").write_text(
        f"## {days_ago(9)}\n### {days_ago(0)}\n- a note dated today\n", encoding="utf-8"
    )
    assert "9 days ago" in run("mentions", project)


def test_cadence_zero_switches_the_reminder_off(project):
    write_config(project, "yes (yes / no)")
    write_log(project, days_ago(11))
    assert run("mentions", project, MENTION_CHECK_DAYS="0") == ""


def test_junk_cadence_falls_back_to_seven(project):
    write_config(project, "yes (yes / no)")
    write_log(project, days_ago(11))
    assert "11 days ago" in run("mentions", project, MENTION_CHECK_DAYS="abc")


def test_a_longer_cadence_is_respected(project):
    write_config(project, "yes (yes / no)")
    write_log(project, days_ago(11))
    assert run("mentions", project, MENTION_CHECK_DAYS="30") == ""


def test_the_nudge_carries_the_approval_rule(project):
    write_config(project, "yes (yes / no)")
    out = run("mentions", project)
    assert "without their explicit approval" in out
    assert "do not start it without their go-ahead" in out


# --- carousel ----------------------------------------------------------------


def test_carousel_is_silent_without_a_config(project):
    assert run("carousel", project) == ""


def test_carousel_with_no_posts_folder_is_due(project):
    write_config(project, None)
    assert "No post has been made in this project yet" in run("carousel", project)


def test_a_finished_post_today_is_silent(project):
    write_config(project, None)
    write_post(project, days_ago(0), "carousel.pdf")
    assert run("carousel", project) == ""


def test_a_finished_post_nine_days_ago_is_due(project):
    write_config(project, None)
    write_post(project, days_ago(9), "carousel.pdf")
    assert "9 days ago" in run("carousel", project)


def test_an_image_post_counts_as_finished(project):
    write_config(project, None)
    write_post(project, days_ago(2), "image.png")
    assert run("carousel", project) == ""


def test_a_dated_folder_with_no_graphic_is_an_unfinished_week(project):
    write_config(project, None)
    write_post(project, days_ago(2), None)
    assert "never produced a finished graphic" in run("carousel", project)


def test_an_unfinished_week_does_not_hide_an_older_finished_one(project):
    """The newer folder is unfinished, so the cadence runs from the finished one."""
    write_config(project, None)
    write_post(project, days_ago(9), "carousel.pdf")
    write_post(project, days_ago(1), None)
    assert "9 days ago" in run("carousel", project)


def test_an_undated_folder_is_ignored(project):
    write_config(project, None)
    (project / "posts" / "drafts").mkdir(parents=True)
    assert "No post has been made" in run("carousel", project)


def test_a_custom_posts_folder_is_honoured(project):
    write_config(project, None)
    write_post(project, days_ago(0), "carousel.pdf", posts="content")
    # The default folder is posts/, which this project does not have, so the
    # finished post is invisible until the option points at it.
    assert "No post has been made" in run("carousel", project)
    assert run("carousel", project, POSTS_DIR="content/") == ""
    assert run("carousel", project, POSTS_DIR="content") == ""


def test_auto_start_emits_the_documented_session_start_field(project):
    import json

    write_config(project, None)
    out = run("carousel", project, AUTO_START="true")
    payload = json.loads(out)["hookSpecificOutput"]
    assert payload["hookEventName"] == "SessionStart"
    assert "weekly-carousel" in payload["initialUserMessage"]


def test_auto_start_off_is_plain_text_not_json(project):
    write_config(project, None)
    out = run("carousel", project, AUTO_START="false")
    assert not out.startswith("{")
    assert "do not start it without their go-ahead" in out


# --- the entry point itself --------------------------------------------------


def test_an_unknown_argument_says_nothing_on_stdout(project):
    write_config(project, "yes (yes / no)")
    assert run("sideways", project) == ""


if __name__ == "__main__":
    start = time.time()
    code = pytest.main([__file__, "-q"] + sys.argv[1:])
    print(f"({time.time() - start:.1f}s)")
    raise SystemExit(code)
