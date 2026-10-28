---
description: Find recent LinkedIn posts that mention the company, verify each one, and comment on the ones I approve
allowed-tools: Read, Write, Edit, Glob, Bash, Task, mcp__linkedin-dev__comment_on_post, mcp__linkedin-dev__search_posts, mcp__linkedin-dev__get_company_posts, mcp__plugin_linkedin-mcp-server_linkedin__comment_on_post, mcp__plugin_linkedin-mcp-server_linkedin__search_posts, mcp__plugin_linkedin-mcp-server_linkedin__get_company_posts
---

Find posts mentioning the company and comment on the ones I approve.

## 0. Check the comment tool is actually there

`comment_on_post` is **not** in the published `mcp-server-linkedin` package. It
exists only in the local clone, so the tool is named for whichever server is
wired up — `mcp__linkedin-dev__comment_on_post` if the clone is registered as
`linkedin-dev`, or `mcp__plugin_linkedin-mcp-server_linkedin__comment_on_post`
once the clone is what the plugin runs.

If neither is available, stop. Tell me the clone is not wired into this session
and give me the command to add it:

```
claude mcp add linkedin-dev -- uv run --directory <path-to>/linkedin-mcp-server mcp-server-linkedin --transport stdio
```

Then tell me the session has to restart before its tools appear. Do not fall
back to any other browser tool to post a comment.

Use whichever one you found for every call below, and say which one you are
using.

## 1. Find the candidates

Launch the `mention-finder` agent. It reads `marketing-config.md`, searches, and
comes back with ranked candidates, a quoted match phrase for each, and the
permalinks the search returned.

Pass along any direction I gave you with the command — a term to watch, a
tighter window, a cap on how many to post.

If it found nothing, tell me what it searched and stop. Do not widen the search
on your own.

## 2. Verify every permalink before writing anything

This is the step that keeps a comment off the wrong post, so do not skip it or
reorder it.

`search_posts` does not align permalinks to result order, so the agent's
pairings are guesses. For each permalink it returned, in order:

1. Call `comment_on_post` with **`confirm_comment: false`** and the drafted
   comment text. Nothing is typed; this is a read.
2. Read `excerpt` back. That is the post's own text, from the page a real
   comment would land on.
3. Match it against the candidates' quoted phrases. The permalink belongs to
   whichever candidate's phrase appears in the excerpt.

   **Read the excerpt's shape before matching.** It is the post's card, so
   after the body it carries the reaction counts and then LinkedIn's canned
   reply suggestions — short lines, often just emoji, sometimes naming the
   author ("Well deserved, Caitlyn"). Those are buttons, not words the post
   said. They are fine for telling one post from another, which is all step 3
   needs. But if the **only** place the company is named is down in that tail,
   the post did not mention the company — drop the candidate and say why.
   - **No candidate's phrase appears** → this permalink is not one of ours.
     Drop it. Do not comment.
   - **`excerpt` is null** → the text could not be read. Drop it; an unverified
     permalink is not worth a comment.
   - **`excerpt_truncated` is true** and the phrase is absent → inconclusive,
     not a mismatch. Drop it, and say it was inconclusive rather than wrong.
   - **A phrase matches more than one candidate** → the phrases are not
     distinctive enough. Drop both and say so.
4. Note the status. Anything other than `dry_run` means no comment is possible
   there: `comments_unavailable` (the author restricted replies),
   `post_unavailable` (deleted, or not visible to this account),
   `editor_occupied` (something is already typed in that box — leave it alone).

Keep only candidates whose permalink you matched to their own phrase.

A candidate the agent ranked first is not exempt from any of this.

## 3. Show me what you have, and wait

Before posting anything, show me a table: author, the gist, the verified
permalink, the excerpt you matched on, and the draft comment in full.

Call out separately:
- candidates dropped in step 2, and why
- anything the agent flagged as **needs a human** or critical of us
- the total number of comments you are proposing

Then **stop and ask which ones to post.** Do not post any comment I have not
approved, and do not treat "looks good" about the drafts as approval to post
them — ask for the numbers.

I may edit a comment's text. Re-run step 2's dry run for anything I edit, since
the text is part of what the call submits.

## 4. Post the approved ones

For each approved candidate, one at a time:

1. Call `comment_on_post` with `confirm_comment: true`.
2. Read the result before moving on:
   - **`posted: true`** → done. Report it.
   - **`status: "outcome_unknown"`** → the click happened, the comment was not
     seen. **Do not retry.** `retry_safe` is false and a retry can comment
     twice. Give me the URL and tell me to check the post myself.
   - **`submit_not_ready` / `submit_failed` / `editor_changed`** → nothing was
     submitted and `retry_safe` is true. Retry **once**, then stop and report.
3. Wait a few seconds between comments.

Hard limits, whatever I approved:
- **No more than the config's `Max comments per run`** (default 3).
- Stop everything on a rate-limit or challenge message, report it, and do not
  call the tool again this session.
- One comment per post. Never comment twice on the same permalink.

Volume commenting is what gets LinkedIn accounts restricted. Each of these is a
deliberate act I asked for, not a loop over a list — if that stops being true,
stop.

## 5. Write down what went out

Append to `mentions-log.md` in the project root (create it if absent), newest
last:

```markdown
## <YYYY-MM-DD>
- **<author>** — <permalink>
  - Comment: <the comment as posted>
  - Status: posted | outcome_unknown
```

This file is how the next run knows not to comment on the same post twice.
**Read it in step 2** and drop any permalink already in it.

Then tell me what posted, what was dropped and why, and what needs my eyes.
