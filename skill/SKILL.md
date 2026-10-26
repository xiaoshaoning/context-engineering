---
name: context-engineering
description: Use when the run is long — the context window is filling, the agent repeats an action that already failed, loops on one subtask, drifts from the instructions, or a handover note / earlier session / memory file is being trusted without checking it against the files. Also for choosing what to compact, prune, offload, or split into a subagent. Skip it for short single-turn tasks; it costs tokens and changes nothing there.
---

# Context engineering

Output = weights × context. The weights are fixed; the context is the lever.

## Diagnose first

| Signal | Failure mode | Fix |
|---|---|---|
| A wrong fact or failed plan stays in history and is retried | poisoning | delete that turn; never leave a false item on a list |
| Instructions drift toward the style of the examples/history | distraction | reset or prune; do not add a stronger instruction |
| Unrelated facts shape the answer | confusion | quarantine: fresh context, task only |
| Two notes/tools/skills disagree | clash | remove one, don't merge |
| One hypothesis pursued long after it stopped paying | inertia | note what is true, clear context, restart from the files |
| A prompt repeats the same instruction 4+ times in caps | fighting the weights | symptom only; expected fragility |

## Fixes, cheapest first

1. **Reset** — keep artifacts on disk; the conversation is not the state.
2. **Offload** — write findings to a file, read back only what the next step needs.
3. **Prune** — drop turns and tool results the next request does not need.
4. **Compact** — summarize; filter for relevance *before* summarizing or the summary is noise.
5. **Quarantine** — hand the self-contained subtask to a fresh-context subagent; return the result only.
6. **Loadout** — filter tools/skills per task; hundreds loaded at startup degrade every call.
7. **Augment** — fetch the specific file or section, not the bulk.

## Numbers

- Past ~100k tokens long-horizon agents start replaying history instead of planning; ~200k is a reset point, not a limit.
- A few contradictory examples outweigh an explicit instruction, worse on small models. Few-shot history is a prompt.
- Periodic forgetting in long runs produces step-changes, not gradual gains.

## Rules

- Deterministic for anything that must always happen; probabilistic for judgment.
- Deletion beats addition. Memory that never prunes becomes noise.
- Fix the shared source of a repeated error, not the turn where it surfaced.
- Prior sessions and notes are claims, not facts: check them against the files before building on them.
- Handing off? One short note: what is true, what failed, what is next.
