# UX Writing

Button labels, error messages, empty states. UX copy is a UI element — it must be concrete, actionable, and honest, never decorative.

## Button labels

- Verbs, not nouns: "Save", "Delete", "Import" — never bare "OK"/"Confirm"
- Match the consequence: destructive actions say what they destroy ("Delete 3 items"), not "Proceed"
- One primary action per screen; secondary actions in plain style
- Convention wins over creativity (Jakob's law)

## Errors

| Rule | Example |
|---|---|
| Say what happened | "Connection timed out" — not "Error" |
| Say how to fix it | "Retry" / "Check your network" |
| Stay local | Inline next to the field, not a global modal |
| Don't punish | Never clear what the user typed |
| Color is not the only signal | Error icon + text, not red alone (WCAG 1.4.1) |
| No jargon | "Invalid response from server" beats "HTTP 500 upstream parse failure" in user-facing copy |

## Empty states

Never just "No data". The empty state is a three-part structure:
1. Icon (sets context)
2. One sentence: what this is / why it's empty
3. One action: create, refresh, or clear filters

| Situation | Copy pattern |
|---|---|
| First use | "Add your first project" + primary CTA |
| No results after filter | "No matches for these filters" + "Clear filters" |
| Genuinely empty | What it is + how to populate it |

Distinguish "no data exists" from "filters excluded everything" — they need different actions (NN/g empty states).

## Feedback messages

- Toast for lightweight success ("Saved") — but reversible operations need no toast; the state change is the feedback (Material snackbars)
- Loading >1s: show progress; >10s: allow cancel (NN/g progress indicators)
- Skeleton screens beat spinners when structure is known

## Anti-slop checklist

- ❌ "Something went wrong"
- ❌ "Are you sure?" when an undo exists — use undo, not confirmation (NN/g 2019)
- ❌ Placeholder text as the only label — labels must persist (NN/g 2014)
- ❌ Passive voice with no owner: "An error has occurred"
- ✅ Concrete, actionable, honest, specific

## Sources

- NN/g — placeholders harmful (2014), undo vs confirm (2019), empty states, progress indicators
- Nielsen heuristics #9 (error recovery), #1 (visibility)
- Material Design 3 — snackbars, text fields
- WCAG 2.2 — 1.4.1
