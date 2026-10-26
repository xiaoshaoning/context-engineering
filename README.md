# context-engineering

Source talk: **<https://www.dbreunig.com/2026/10/24/the-state-of-context-engineering.html>**
(*The State of Context Engineering*, Drew Breunig, AGNTCon, October 2026).

Drew Breunig's talk as an offline PDF, a pi skill that condenses it into operating rules,
and the A/B test that measures whether the skill actually changes agent behaviour.
Results and method: [REPORT.md](REPORT.md).

**Short version:** the skill does nothing on short tasks and a lot on long ones. With a
135k-token poisoned history, 2/8 vs 7/8 success, one-sided Fisher p = 0.020.

---

## What's here

```
article/     source markdown + PDF/LaTeX pipeline; 32-page PDF, 39 slides, 36 as real SVG
  build/     generated (git-ignored): traced figures, downloaded slides, .tex, logs
eval/        fixtures with a poisoned handover note, headless runner, results/
REPORT.md    method, numbers, threats to validity
```

## Using the skill

One `SKILL.md`, three harnesses. The repo copy is canonical; installing is a file copy, not a
build — every one of these tools reads `SKILL.md` from disk and loads the body on demand.

```bash
cd skill && ./install.sh          # every harness found on PATH
./install.sh --dir ~/.foo/skills  # somewhere else
```

| harness | location | pick-up |
|---|---|---|
| Codex | `~/.agents/skills/context-engineering/` | `/skills`, `$context-engineering`, or automatic |
| Claude Code | `~/.claude/skills/context-engineering/` | `/context-engineering`, or automatic |
| pi | `~/.pi/agent/skills/context-engineering/` (`~/.agents/skills` also works) | automatic, or `/skill:context-engineering` |
| any Agent Skills tool | `~/.agents/skills/` | per tool |

Verified against each tool's limits: name 19 chars (kebab), description 422 chars (Codex caps
500, Claude caps description + `when_to_use` at 1536), and the description states when *not*
to trigger, which Codex asks for. `install.sh` skips pi's own directory when
`~/.agents/skills` is already in place: two copies of one name is a duplicate, not a second
install.

pi advertises the name and description at startup and loads the body only when the task
matches — which, measured, is 0/8 times on a plain "fix this bug". So ask for it by name when
you need it:

```
/skill:context-engineering continue from state.md and make the suite green
/skill:context-engineering the agent keeps retrying the same failed edit; what do I reset?
```

Headless / scripted (pi):

```bash
pi -p --skill ~/.agents/skills/context-engineering "…"                 # advertised, model may read it
pi -p --no-skills --skill ~/.agents/skills/context-engineering "…"     # only this skill
pi -p "/skill:context-engineering …"                                   # body forced into the prompt
```

Use it when resuming from a handover note, when the context window is filling, when the
agent repeats an action that already failed, or when a notes/memory file contradicts the
code. Skip it for a one-shot task in a fresh session — it is token tax there.

Edit `skill/SKILL.md`, re-run `install.sh`, then `/reload` in a live pi session; Claude Code
and Codex pick it up on their next session.

## Rebuilding the PDF

```bash
cd article
bash build.sh          # rebuild the PDF (traces only missing slides)
python build.py --force   # re-trace every slide from the JPEGs
```

Needs `vtracer`, `Pillow`, `numpy`, `rsvg-convert`, pandoc, xelatex. `build.py` downloads the
slides to `build/img/`, traces them, and keeps a slide as vector PDF only if re-rendering it
lands within 6/255 mean pixel error of the JPEG and under 1.2 MB; three photographic slides
fail that and stay raster. Decisions are cached in `build/figs/`, so later builds are seconds.

Output: `article/state-of-context-engineering.pdf`, vectors in `article/svg/`.

## Running the evaluation

```bash
cd eval
python run_experiment.py trap 3                     # short task: no difference
APPEND_SYSTEM=$PWD/fixtures/bigctx/history.txt \
  CONDS=baseline,forced REP_START=1 \
  python run_experiment.py bigctx 8                 # the effect
```

Grader self-check (no framework, plain asserts):

```bash
python test_grader.py
```

Args: `<scenario> <reps> [model]`. Scenarios: `trap`, `bigrepo`, `stuck`, `bigctx`.
Conditions on any run: `CONDS=baseline,organic,forced`. Results append to
`results/<scenario>-<model>.json`; each run works in a throwaway copy under `runs/`.

Grading is mechanical — suite green, test files byte-identical, behaviour probe correct. No
LLM judge, so a run that "fixes" the test to match the bug counts as a failure.

## Source and rights

Slides and transcript belong to Drew Breunig (Cmpnd) — the URL is at the top of this README.
This repo is a reading copy plus my own tooling, not a redistribution license: the code
(`article/*.py`, `article/*.sh`, `eval/`) is MIT, see [LICENSE](LICENSE); the article text
and slide images keep their author's rights and are not covered by that license.
