# /capture — Fast Inbox Drop

Get a thought out of the user's head and into the vault. Nothing else.

## Speed Is the Whole Point

**No routing questions. No follow-ups. No template.** The user is mid-thought and will not tolerate a conversation.

If you find yourself about to ask "which Area should this go in?" — you've broken the command. That decision belongs to weekly review. Capture beats organize, every time, because the alternative to a messy Inbox isn't a tidy vault; it's a lost thought.

## Step 1: Triage in One Beat

Look at what they said and pick one destination. Don't ask — decide.

**It's a task** (has a verb and an implied owner: "follow up with Dana", "send the deck"):
```bash
bd q "<the thing>"        # quick capture, returns just an ID
```

**It's a durable fact** (a stable truth about how the world works: "Dana owns billing", "fiscal year starts in April"):
```bash
bd remember "<the fact>" --key <short-key>
python3 .claude/scripts/memory_meta.py confirm <short-key>   # --kind person for facts about people
```

**It's anything else** — an idea, an observation, a half-formed thought → append to `Inbox/Quick Captures.md`.

**Genuinely unsure?** Inbox. Always. Inbox is the safe default and the entire reason it exists.

## Step 2: Write It

For the Inbox, append under the capture marker, matching the file's existing style:

```markdown
- **HH:MM** — [content]
```

Preserve their words. Don't clean up phrasing, expand shorthand, or make it a proper sentence — the raw phrasing carries context that a tidied version loses.

If the file doesn't exist, create it with a `## Quick Captures` heading.

## Step 3: Confirm in One Line

```
✅ Inbox (7 items)
```
```
✅ cab-42 — follow up with Dana on billing scope
```
```
✅ Remembered: dana-billing
```

That's the entire response. No summary, no "let me know if you'd like me to...", no offer to elaborate.

Only exception: if the Inbox passes 10 items, add one line — *"Inbox is at 12 — worth a `/weekly-review`."* Once. Not every time.

## If `bd` Isn't Installed

Everything goes to the Inbox, including tasks. Note it once per session at most.

## Judgment

**Multiple things in one capture?** Split them. Three thoughts get three entries — a blob is unprocessable later.

**Obviously belongs somewhere specific?** Capture it to Inbox anyway, then add one line: *"This looks like it belongs in Areas/Pricing — want me to file it?"* Capture first, always. Never turn a ten-second action into a decision.

**Sounds urgent?** Make it a bead with a priority rather than an Inbox line. `bd q` then `bd priority <id> 1`.

## Examples

> "users over 70 struggle with the multi-step wizard"
→ Inbox. It's an observation, not a task.

> "ask Chris about scope before Tuesday"
→ `bd q`. Verb, owner, deadline.

> "Priya is the actual decision maker on renewals, not Marcus"
→ `bd remember`. Durable fact, will matter in every future session.

> "what if checklist completion had streak tracking"
→ Inbox. Idea.

## Begin

Capture it. Fast.
