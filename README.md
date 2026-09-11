# Hermes workshop: teach it once, make it repeat

Two-hour hands-on workshop. Attendees leave with a skill they taught by correcting it, plus a scheduled job that runs that skill and messages their phone.

| File | What it is |
|---|---|
| [`HANDOUT.html`](HANDOUT.html) | The handout. Self-contained, interactive checklists, copy buttons. Open in a browser. |
| `HANDOUT.md` | Source for the handout. |
| `build_handout.py` | Rebuilds `HANDOUT.html` from `HANDOUT.md`. |
| `hermes-personal-work.html` | The 31-slide deck. Arrows to navigate, `S` for speaker notes, `F` for clean projection. |

## Model access

The workshop API key is **not in this repo**. Use one of:

- `hermes model` -> provider `opencode-go` -> model `glm-5.3-flash` (key handed out live)
- `/model free` for the keyless `opencode-free` provider
- Your own OpenRouter account with model id `openrouter/free`

`opencode-go` has its own 37-model catalog with no Claude and no GPT on it. Picking a model that is not on that list returns `Model ... is not supported`, which looks like a bad key but is not. Verified working with tool calling: `glm-5.3-flash`, `qwen3.8-flash`, `minimax-m2.5`. Avoid `deepseek-v4-flash`, it is region locked.

## Verified against a running install

Rehearsed on a live Hermes 0.19.x gateway rather than taken from docs alone:

- A `SKILL.md` dropped on disk is picked up with no restart.
- A fresh session invoked by skill name only returns the skill's constrained output. This is the workshop's core mechanic.
- An agent-mode cron created paused, resumed, and run delivers to Discord and completes.
- `hermes cron run` **refuses** to fire a paused job (`Job is paused/disabled; resume it before running`), contrary to the published docs. Resume first.

## Credits

Maanav Dalal, Developer Relations at Black Forest Labs. [maanavdalal.com](https://www.maanavdalal.com/)
