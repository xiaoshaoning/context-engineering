# context-engineering

Drew Breunig's AGNTCon talk *The State of Context Engineering* as an offline PDF, a pi skill
that condenses it into operating rules, and the A/B test that measures whether the skill
actually changes agent behaviour. Results and method: [REPORT.md](REPORT.md).

**Short version:** the skill does nothing on short tasks and a lot on long ones. With a
135k-token poisoned history, 2/8 vs 7/8 success, one-sided Fisher p = 0.020.

---

## What's here

```
ctx/         article -> LaTeX/PDF pipeline; 32-page PDF, 39 slides, 36 as real SVG
skilltest/   fixtures with a poisoned handover note + headless runner + raw results
REPORT.md    method, numbers, threats to validity
```

## Using the skill

Installed at `~/.pi/agent/skills/context-engineering/SKILL.md`. Pi advertises its name and
description at startup and loads the body only when the task matches — which, measured, is
0/8 times on a plain "fix this bug". So ask for it by name when you need it:

```
/skill:context-engineering continue from state.md and make the suite green
/skill:context-engineering the agent keeps retrying the same failed edit; what do I reset?
```

Headless / scripted:

```bash
pi -p --skill ~/.pi/agent/skills/context-engineering "…"          # advertised, model may read it
pi -p --no-skills --skill ~/.pi/agent/skills/context-engineering "…"   # only this skill
pi -p "/skill:context-engineering …"                               # body forced into the prompt
```

Use it when resuming from a handover note, when the context window is filling, when the
agent repeats an action that already failed, or when a notes/memory file contradicts the
code. Skip it for a one-shot task in a fresh session — it is token tax there.

Edit the skill, then `/reload` in a live session; a new session picks it up by itself.

## Rebuilding the PDF

```bash
cd ctx
bash build.sh figs     # re-trace slides (vtracer) + rebuild PDF
bash build.sh          # reuse figs/, rebuild PDF only
```

Needs `vtracer`, `Pillow`, `numpy`, `rsvg-convert`, pandoc, xelatex. The trace quality gate in
`ctx/build.py` keeps a slide as SVG only if re-rendering it lands within 6/255 mean pixel
error of the JPEG and under 1.2 MB; three photographic slides fail that and stay raster.

Output: `ctx/state-of-context-engineering.pdf`, vectors in `ctx/svg/`.

## Running the evaluation

```bash
cd skilltest
python run_experiment.py trap 3                     # short task: no difference
APPEND_SYSTEM=$PWD/bigctx/history.txt \
  CONDS=baseline,forced REP_START=1 \
  python run_experiment.py bigctx 8                 # the effect
```

Args: `<scenario> <reps> [model]`. Scenarios: `trap`, `bigrepo`, `stuck`, `bigctx`.
Conditions on any run: `CONDS=baseline,organic,forced`. Results append to
`results-<scenario>-<model>.json`; each run works in a throwaway copy under `runs/`.

Grading is mechanical — suite green, test files byte-identical, behaviour probe correct. No
LLM judge, so a run that "fixes" the test to match the bug counts as a failure.

## Source

Original talk: <https://www.dbreunig.com/2026/10/24/the-state-of-context-engineering.html>
(Drew Breunig, Cmpnd, October 2026). Slides and text belong to him; this repo is a reading
copy, not a redistribution license.
