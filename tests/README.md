# Hook tests

```bash
uv run --locked --script tests/test_nudge.py
```

No `pip install pytest` step: the test declares pytest in its own PEP 723
header, the same way the plugin's scripts declare theirs, so `uv` fetches it.
Pass pytest flags through — `uv run --locked --script tests/test_nudge.py -k mentions`.

`hooks/nudge.py` runs on **every** session start in **every** project on the
machine, so staying silent when it is not wanted matters more than anything
else it does. Most of these cases assert silence.

The config fixture is cut out of `commands/linkedin-setup.md` rather than typed
into the test. That is deliberate: a hand-written fixture is a claim about the
template, and the two drifted once already — the template emits
`**Watch for mentions:** yes (yes / no)` and the hook was comparing the whole
string, hint included, against `yes`, so every config read as switched off
while the test passed. Keep the fixture derived.

Each case shells out through `uv run --locked --script`, the way `hooks.json` invokes the
hook, so a mistake in the PEP 723 header or in argument handling fails here and
not in a client's session.

## Why this is Python and not bash

It was two bash scripts until the plugin had to install on Windows. The hooks
used the exec form — `"command": "bash"` with `args` — and on Windows exec form
needs `command` to resolve to a real executable, while `shell` is ignored
whenever `args` is set. Git for Windows is optional for Claude Code, so there
may be no `bash` at all; where there is, the recommended installer puts only
`Git\cmd` on PATH while `bash.exe` lives in `Git\bin`. The result was a silent
exit 127: no reminder, ever, and nothing printed to say why.

`uv` was already required for the LinkedIn MCP server, `uv.exe` is a real PATH
executable, and exec form passes the backslashed plugin path as one argv element
that no shell tokenizes. So the rule for this plugin is: **no bash scripts, no
bare `python3`, no bare `curl`.** Anything that needs to run, runs through
`uv run --locked --script`.
