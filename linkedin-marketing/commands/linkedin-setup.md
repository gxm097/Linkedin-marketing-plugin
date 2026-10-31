---
description: Set up this project for LinkedIn marketing — write marketing-config.md and check the Canva connection
allowed-tools: Read, Write, Edit, Glob, Bash, WebFetch, Skill, mcp__canva__list-brand-kits, mcp__canva__search-brand-templates, mcp__linkedin__get_my_profile, mcp__linkedin-dev__get_my_profile
---

Set up the LinkedIn marketing plugin for this project.

## 0. Check `uv` is there

`uv` is the plugin's only prerequisite. It runs the session-start reminders and
the carousel's PDF step, and it supplies Python itself, so nothing else has to
be installed. It also runs the LinkedIn server, if I have added one.

Run `uv --version`. If it is missing, stop and give me the line for my platform:

- **Windows** (PowerShell): `irm https://astral.sh/uv/install.ps1 | iex`
- **macOS / Linux**: `curl -LsSf https://astral.sh/uv/install.sh | sh`

Tell me to restart the session afterwards, because the hooks are launched when
the session starts and will not find `uv` until then.
Don't run the install for me — it writes to my PATH.

If it is there, say so in one line and carry on. Also mention, once, that the
first carousel is slow: `uv` builds the server and then downloads a ~187 MB
browser. It only happens once, and it is not a hang.

## 1. Don't clobber existing work

Check whether `marketing-config.md` already exists in the project root. If it
does, do **not** overwrite it. Tell me it exists and show which important fields
are still blank (company name, website, audience, content pillars), then offer to
fill just those in.

## 2. Start from what I typed at install

The install dialog already collected some of this. Read it so you don't ask me
twice: open `~/.claude/settings.json` with the Read tool and look under
`pluginConfigs` for the key containing `linkedin-marketing`. Its values are the
company name, website, audience, cadence, Canva mode, and the mention settings.

Read the file rather than shelling out to parse it. There may be no shell to
shell out *to*: Git for Windows is optional for Claude Code, and without it
there is no `bash`, only PowerShell. If the file or the key is absent, that just
means the dialog was skipped — carry on and ask me.

Use whatever you find as the starting values. Anything it didn't give you, ask
me for: company name, website, and who our audience is. Then, if I say so, fetch
the website to suggest the industry, what we do, differentiators, voice, and 3
content pillars.

## 3. Check the Canva connection

Call `list-brand-kits`.

- **It worked** → the user is on Canva Pro or above. Call `search-brand-templates`
  for a square (1080×1080) template. If you find one, record its ID as the
  **Brand template ID** and set **Canva mode** to `brand-template`. Tell me which
  template you picked.
- **No square template** → set Canva mode to `brand-template` only if I say I'll
  make one; otherwise `generate`. Explain that a Brand Template gives much more
  consistent slides, and that its text fields must be tagged in Canva under
  **Apps → Bulk Create → Labels** before autofill can work.
- **It failed** → either Canva isn't connected or the plan is Free. Set Canva mode
  to `generate`, which works on Canva Free. If it looks like an auth problem, tell
  me Canva still needs connecting and point me at the README's **Connect Canva**
  step — it needs a Canva app's own client ID and secret through `claude mcp add`,
  then `/mcp` → `canva` → sign in. Don't tell me to authorise
  `plugin:linkedin-marketing:canva`; that server has no credentials and fails with
  "does not support dynamic client registration".

Either way, don't stop setup over Canva. `generate` mode works for everyone.

## 4. Write the config

Write `marketing-config.md` to the **project root** using exactly the template
below, filled in with what I gave you and what you found. Leave anything unknown
blank. It lives in my project, not in the plugin, so a plugin update never
overwrites it.

## 5. Mentions, only if I asked for them

If the install dialog set **Watch for mentions** on, fill the Mentions section
in: `yes`, plus any extra terms, the check cadence, and the comment cap it gave
you. Otherwise leave **Watch for mentions** as `no` and say one line about what
it would do — don't talk me into it.

## 6. Sign me in to LinkedIn now

Do this even if mentions are off; the carousel's research does not need
LinkedIn, but everything else does, and it is better to get it over with here
than halfway through a carousel.

Call `get_my_profile` on the `linkedin` server. It is read-only. One of three
things happens:

- **It returns a profile** → say whose account it is, in one line. Done.
- **A browser window opens** → tell me to sign in there, and that LinkedIn may
  ask me to confirm in its mobile app or solve a captcha. Both are mine to do in
  that window. Wait for me.
- **The tool is not there at all** → the LinkedIn server has not been added.
  This plugin does not ship it. Point me at the README's **Add the LinkedIn
  server** step, exactly as you would for Canva, and give me the line to run in
  my own terminal:
  `claude mcp add linkedin --scope user -e UV_HTTP_TIMEOUT=300 -- uvx --from git+https://github.com/gxm097/linkedin-mcp-server@v4.28.0-comment.1 mcp-server-linkedin --transport stdio`
  If it is added but the tool is missing, check `uv --version`, restart Claude
  Code if `uv` arrived after this session began, and remember the first run
  builds the server from source and takes minutes — tell me to check `/mcp`.

Never offer to work around this with another browser tool.

## 7. Tell me what's next

Show me the filled-in file. Tell me to run `/linkedin-marketing:weekly-carousel`
when I'm ready, and that I'll get a reminder here whenever the next one is due.

**If mentions are on, offer to run the first check now** —
`/linkedin-marketing:mention-comments` — and wait for me to say yes. Offer it;
do not start it. Two reasons it is an offer and not a step:

- The config you just wrote is the input to that search. I have not read it yet,
  and the watch terms and the **Never comment on** list are the two fields most
  likely to be wrong on a first pass.
- A comment is a public write to a real account. Every comment needs my explicit
  approval whenever the check runs, and that does not change because setup is
  the thing that launched it.

If I say yes, run it. If I don't, say the reminder will offer again when it is
due.

---

Template:

````markdown
# Marketing Config

Used by the marketing-researcher, carousel-writer, and linkedin-post-creator
agents and the /weekly-carousel command.
Fill in what you know; leave anything blank you don't. This file overrides
anything the agents find on the web, and anything set in the install dialog.

## Company
- **Name:** 
- **Website:** 
- **LinkedIn page:** 
- **Industry:** 
- **What we do (1–2 sentences):** 
- **Key products/services:** 
- **Differentiators:** 
- **Competitors (for context only, never mention by name):** 

## Audience
- **Who we're talking to:** (e.g., HR directors at mid-size companies)
- **Their pain points:** 
- **Audience time zone:** America/Chicago

## Voice
- **Tone:** (e.g., confident, friendly, practical, no hype)
- **Point of view:** (company "we" or personal "I")
- **Words/phrases to avoid:** synergy, game-changer, "excited to announce"
- **Emoji use:** none / light / moderate

## Content pillars
Topics we post about. When no topic is given, the agents pick from these based
on current trends.
1. 
2. 
3. 

## Post defaults
- **Platform:** LinkedIn
- **Goal:** engagement (awareness / engagement / leads / hiring)
- **Default call to action:** Ask a question to drive comments
- **Post length:** 150–250 words
- **Hashtags:** 3–5
- **Always-include hashtags:** 
- **Posts per week:** 1

## Carousel
LinkedIn carousels are document posts — one multi-page PDF, one page per slide.
- **Slides per carousel:** 7 (6–10)
- **Slide size:** 1080x1080
- **Canva mode:** auto (auto / brand-template / generate)
- **Brand template ID:** 
- **Slide headline max words:** 15

## Image
- **Image skill:** canva-carousel
- **Single-image size:** 1200x627
- **Style:** (e.g., clean modern illustration, flat colors)
- **Brand colors:** (e.g., #1A73E8, #FFFFFF, #202124)
- **Fonts / overlay text style:** 
- **Avoid in images:** real people's faces, fake logos, small text

## Research settings
- **Trend window:** last 30 days
- **Preferred sources:** (industry sites, publications you trust)
- **Sources to avoid:** 

## Mentions
Used by /mention-comments and the mention-finder agent. Leave **Watch for
mentions** as `no` and nothing here runs — no searching, no reminder.
Comments are never posted without you approving each one.
- **Watch for mentions:** no (yes / no)
- **Watch terms:** (comma-separated; the company name is always included)
- **Look back:** last 7 days
- **Max candidates per check:** 5
- **Max comments per run:** 3
- **Never comment on:** (handles or companies to leave alone — competitors, press)
- **Comment length:** 1–3 sentences

## Output
- **Save posts to:** posts/
````
