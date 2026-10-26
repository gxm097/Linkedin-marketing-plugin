#!/usr/bin/env bash
# Tells Claude when the weekly LinkedIn carousel is due.
#
# Runs on every session start, in every project, so the first thing it does is
# work out whether this is even a marketing project and go quiet if it isn't.
# Anything printed on stdout is injected into the conversation, so silence here
# matters more than any other behaviour in this plugin.

set -uo pipefail

project="${CLAUDE_PROJECT_DIR:-$PWD}"

# Not a marketing project -> say nothing at all.
[ -f "$project/marketing-config.md" ] || exit 0

posts_dir="${CLAUDE_PLUGIN_OPTION_POSTS_DIR:-posts/}"
cadence="${CLAUDE_PLUGIN_OPTION_CADENCE_DAYS:-7}"
auto_start="${CLAUDE_PLUGIN_OPTION_AUTO_START:-false}"

case "$cadence" in
  ''|*[!0-9]*) cadence=7 ;;
esac

# Last post date comes from the newest posts/YYYY-MM-DD-<slug>/ folder rather
# than a stamp file: it cannot drift out of sync with the actual output, and it
# stays per-project, so one marketer running several clients in several folders
# gets the right answer for each.
#
# A folder only counts as a finished week if the deliverable is actually in it.
# A run that got as far as the copy but never produced a graphic (Canva down, or
# interrupted) leaves a dated folder behind, and counting that as done would
# silence the reminder for a week that never shipped.
last=""
unfinished=""
posts_path="$project/${posts_dir%/}"
if [ -d "$posts_path" ]; then
  for d in "$posts_path"/*/; do
    [ -d "$d" ] || continue
    name=$(basename "$d")
    case "$name" in
      [0-9][0-9][0-9][0-9]-[0-9][0-9]-[0-9][0-9]*) ;;
      *) continue ;;
    esac
    day="${name:0:10}"
    if [ -f "$d/carousel.pdf" ] || [ -f "$d/image.png" ]; then
      [ "$day" \> "$last" ] && last="$day"
    else
      [ "$day" \> "$unfinished" ] && unfinished="$day"
    fi
  done
fi

today_s=$(date +%s)
if [ -n "$last" ]; then
  last_s=$(date -d "$last" +%s 2>/dev/null) || exit 0
  days=$(( (today_s - last_s) / 86400 ))
  [ "$days" -ge "$cadence" ] || exit 0
  when="The last one went out ${days} days ago (${last})."
else
  days=""
  if [ -n "$unfinished" ]; then
    when="The last attempt (${unfinished}) never produced a finished graphic, so this week has not shipped."
  else
    when="No post has been made in this project yet."
  fi
fi

if [ "$auto_start" = "true" ] || [ "$auto_start" = "1" ]; then
  # Begin the flow directly. initialUserMessage is a documented SessionStart
  # output field; if a future build stops honouring it the additionalContext
  # branch below still reaches the user, so this fails soft.
  printf '{"hookSpecificOutput":{"hookEventName":"SessionStart","initialUserMessage":"The weekly LinkedIn carousel is due. %s Run /linkedin-marketing:weekly-carousel now."}}\n' "$when"
else
  printf 'The weekly LinkedIn carousel for this project is due. %s Early in your reply, tell the user it is due and offer to run /linkedin-marketing:weekly-carousel — do not start it without their go-ahead.\n' "$when"
fi

exit 0
