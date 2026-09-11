# Hermes workshop: teach it once, make it repeat

**What you leave with:** a skill you taught by correcting it, plus a scheduled job that runs that skill and messages your phone.

Everything below is either verbatim from the official docs or checked against a running install. Where something is unverified, it says so. If a step does not match what is on your screen, stop and say so in the room rather than guessing.

---

# Part 0. Before you arrive

Budget 20 minutes. Do this at home. Setup in the room will overrun and this is how you avoid being the person it overruns for.

## 0.1 What you need

- A laptop. macOS, Linux, or Windows with WSL2. Native Windows works but uses a different installer.
- **Git installed.** On non-Windows this is the only prerequisite. Check with `git --version`.
- On Linux also: `sudo apt install curl xz-utils`
- A phone with Discord on it.
- A Discord account, and a Discord server **you own** (you need the `Manage Server` permission to invite a bot). Making a new private server takes ten seconds.

The installer pulls in everything else on its own: `uv`, Python 3.11, Node.js v26, `ripgrep`, `ffmpeg`.

## 0.2 Install Hermes

macOS, Linux, WSL2:

```sh
curl -fsSL https://hermes-agent.nousresearch.com/install.sh | bash
```

Windows, in PowerShell:

```powershell
iex (irm https://hermes-agent.nousresearch.com/install.ps1)
```

Then reload your shell:

```sh
source ~/.zshrc     # or ~/.bashrc
```

Check it worked:

```sh
hermes doctor
```

**Where things land.** Code goes in `~/.hermes/hermes-agent/`. The `hermes` command is a symlink at `~/.local/bin/hermes`. Your data lives in `~/.hermes/`.

> If you ever see `ModuleNotFoundError: No module named 'dotenv'`, you ran the repo source file with system Python instead of the launcher. Use `hermes`, not `~/.hermes/hermes-agent/hermes`.

## 0.3 Give it a model

Run the wizard. This is the only path that can add a provider or prompt for a key. The in-chat `/model` command cannot.

```sh
hermes model
```

Pick **one** of these three.

### Option A. The workshop key (fastest)

In the `hermes model` wizard pick provider **`opencode-go`**, then paste:

```
sk-REPLACED-SEE-SCREENSHARE
```

Then pick the model **`glm-5.3-flash`**. Verified working on this key during preflight, including tool calling.

`opencode-go` has its own 37-model catalog and it is **not** the same as OpenCode Zen. There is no Claude and no GPT on it. If you pick a model that is not on the Go list you get `Model ... is not supported`, which reads like a broken key but is not.

| Pick | Why |
|---|---|
| `glm-5.3-flash` | Default. Fastest of the three, tool calling confirmed |
| `qwen3.8-flash` | Fallback, tool calling confirmed |
| `minimax-m2.5` | Second fallback, tool calling confirmed |
| ~~`deepseek-v4-flash`~~ | Avoid. Returns `RegionError`, the current version is China-hosted only |

This key is rotated the day of the workshop, so it is useless to anyone afterwards, including you. Have Option B or C ready for tonight.

### Option B. No key, no account

```
/model free
```

The provider is `opencode-free` (aliases `free`, `opencode_free`). Requests are sent anonymously. Free tiers rotate and their data terms differ from paid ones. **Not rehearsed for this workshop.** If it works for you, good, but do not rely on it as your only path.

### Option C. Your own OpenRouter account

Provider `openrouter`, model id `openrouter/free`. Checked live during preparation: 200,000 token context, prompt and completion both priced at zero, `tools` and `tool_choice` both supported.

Accounts that have never bought credits are capped at **50 requests per day and 20 per minute**. One agent turn can spend several requests. Do not sit in a retry loop.

### The one rule that catches people

**Hermes rejects any model under 64,000 tokens of context at startup.** All three options above clear that. If you point it at a local model, you must raise the context yourself:

- Ollama: `OLLAMA_CONTEXT_LENGTH=64000 ollama serve`. You cannot set this through the OpenAI-compatible API.
- llama.cpp: `--ctx-size 65536`, and `--jinja` is **required** for tool calling. Without it, llama-server ignores the `tools` parameter entirely.

Also check your fallback routes are free too. A free primary model with a paid fallback is not a free setup.

## 0.4 Create your Discord bot

Eight steps. The labels in backticks are what is actually on the screen.

### Step 1. Create the application

1. Go to **https://discord.com/developers/applications**
2. Click `New Application`, top-right.
3. Give it a name, tick the box accepting the Developer Terms of Service, click `Create`.
4. You land on `General Information`. **Copy the `Application ID` from this page** and keep it somewhere. You need it in Step 5 if you take the manual route.

### Step 2. Set the authorization flow

1. Click `Bot` in the left sidebar. Your bot already exists: newly created apps have a bot user enabled by default, so there is no `Add Bot` button to look for.
2. Under `Authorization Flow`: set `Public Bot` to **ON**.
3. Leave `Require OAuth2 Code Grant` **OFF**.

### Step 3. Turn on the intents

Still on the `Bot` page, scroll to `Privileged Gateway Intents`. There are three:

| Toggle | What it does | You need it |
|---|---|---|
| `Presence Intent` | See online/offline status | No |
| `Server Members Intent` | Read the member list, resolve usernames | **Yes** |
| `Message Content Intent` | Read the actual text of messages | **Yes** |

Toggle the bottom two **ON**, then click `Save Changes`.

> This is the single most common failure. Without `Message Content Intent` your bot connects, appears online, receives messages, and sees an empty `content` field on every one of them. It will look alive and do nothing. If Hermes requests an intent you did not enable, Discord closes the connection with code `4014`.

Under 10,000 users you can toggle these freely with no application or review.

### Step 4. Get the token

1. On the `Bot` page, find the `Token` section.
2. Click `Reset Token`. Enter your 2FA code if you have 2FA on.
3. **Copy it now.** You cannot view it again. If you lose it or paste it wrong, your only option is to click `Reset Token` again, which invalidates the previous one.

**The token goes into the `hermes gateway setup` prompt and nowhere else.** Not into a chat message, not into a screenshot, not into a repo, not onto a slide.

### Step 5. Generate the invite link

Use the `Installation` page. This is the path Discord currently documents.

1. Click `Installation` in the left sidebar.
2. Under `Installation Contexts`, enable `Guild Install`.
3. Under `Install Link`, select `Discord Provided Link`.
4. Under `Default Install Settings for Guild Install`, set Scopes to `bot` and `applications.commands`.
5. Selecting `bot` reveals a permissions menu. Tick at minimum: `View Channels`, `Send Messages`, `Embed Links`, `Attach Files`, `Read Message History`. Also worth adding: `Send Messages in Threads`, `Add Reactions`.
6. Copy the URL shown in the `Install Link` section.

**Alternative, if your portal looks different.** Paste this into a browser and swap in your Application ID from Step 1:

```
https://discord.com/oauth2/authorize?client_id=YOUR_APP_ID&scope=bot+applications.commands&permissions=274878286912
```

`274878286912` is the recommended permission integer: everything in the list above including threads and reactions. The bare minimum integer is `117760` (View Channels, Send Messages, Read Message History, Attach Files).

### Step 6. Invite it

1. Open the link.
2. Pick your server from the `Add to Server` dropdown.
3. `Continue`, then `Authorize`, then the CAPTCHA.

You need `Manage Server` on the target server. Your own private server is the easy answer.

The bot will show as offline. That is correct and expected until the gateway is running.

### Step 7. Get your own user ID

1. Discord `Settings` → `Advanced` → toggle `Developer Mode` **ON**.
2. Right-click your own username, choose `Copy User ID`.

It looks like `284102345871466496`. You need it in the next step.

### Step 8. Connect Hermes

```sh
hermes gateway setup
```

Select Discord. Paste the bot token and your user ID when asked.

Or write it yourself into `~/.hermes/.env`:

```
DISCORD_BOT_TOKEN=your-bot-token
DISCORD_ALLOWED_USERS=284102345871466496
```

> **Set `DISCORD_ALLOWED_USERS`.** Without an allowlist the gateway denies everyone by default, and you will spend twenty minutes debugging a bot that is working exactly as designed. If you see this in `~/.hermes/logs/gateway.log`, this is why:
>
> `No Discord access policy configured; inbound Discord messages will be denied by default.`

## 0.5 Start the gateway

Foreground, keep the terminal open:

```sh
hermes gateway
```

Or let the OS keep it alive:

```sh
hermes gateway install
hermes gateway start
hermes gateway status
```

Do not run two gateways against the same profile.

## 0.6 Preflight, before you close the laptop

- [ ] `hermes doctor` runs clean
- [ ] `hermes gateway status` says it is up
- [ ] Your bot shows online in your server
- [ ] You sent a message **from your phone** and got a reply
- [ ] That reply proves a tool ran, not just that chat works (see 1.1)

---

# Part 1. In the room

## 1.1 Checkpoint one: say hello

From **your phone**, not your laptop. In a channel you must mention the bot. In a DM you do not.

> @YourBot What files are in my home directory? List three.

We ask a filesystem question on purpose. A model with no working tools will cheerfully invent an answer, so "it replied" is not a pass. **The pass is a reply that could only be produced by looking at your actual machine.**

Useful commands once it is alive:

| Command | Does |
|---|---|
| `/status` | Session info |
| `/new` or `/reset` | Fresh conversation |
| `/stop` | Cancel what it is doing now |
| `/sethome` | Make this chat the delivery target |
| `/help` | Everything else |

**Nobody moves on until every person in the room, including remote, has a reply on their phone.**

## 1.2 Pick your routine

Pick something you already have opinions about. You have to be able to look at the output and know immediately that it is wrong. If you cannot judge it, you cannot correct it, and the rest of this does nothing.

- A training session ← the default, follow along exactly if nothing jumps out
- Tomorrow's meals
- A study block
- Practice for an instrument
- What to read next

Two minutes. Do not spend five.

## 1.3 Let it get it wrong

Ask for the thing with **no context at all**. From your phone.

> Plan tomorrow's session for me.

Resist writing a good prompt. A bad first answer is the material for everything that follows. It does not know your schedule, your equipment, your level, what you did yesterday, or the one thing you refuse to do.

## 1.4 Correct it, out loud

Now tell it. Push through three or four rounds, not one. You are onboarding, not prompting.

| Cover this | Example |
|---|---|
| **When** | "I train 6 to 7.30am on weekdays. Never weekends." |
| **With what** | "Barbell, rack, dumbbells to 30kg. No machines, no cables." |
| **Where you are** | "Intermediate. Yesterday was heavy squats." |
| **Never** | "I will not do burpees. Do not suggest them again." |
| **Shape** | "Give me a title, a time range, and 4 to 6 lines. Nothing else. I read this on a phone at 6am." |

The last row matters more than people expect. The output shape is what makes the scheduled version readable at six in the morning.

## 1.5 Write it down

Once you like the answer:

```
/learn
```

Then go and open what it actually wrote:

```
~/.hermes/skills/<your-skill-name>/SKILL.md
```

**Open the file.** `/learn` guesses, and it guesses well, and it still guesses.

- The frontmatter needs a `name` and a `description`. The description is how it decides whether to use the skill at all, so a vague one makes the skill invisible. Keep it under 60 characters.
- Usually needs deleting: one-off details from today's conversation that got written down as if they were rules.
- Usually needs adding: what to do when it cannot get the information it needs.

Once it exists, call it with `/<skill-name>`.

### Memory versus skills

Two different stores, and people jam the wrong thing into the wrong one.

| | Memory | Skills |
|---|---|---|
| Holds | Small durable facts about you | A procedure it follows on command |
| Lives at | `~/.hermes/memories/USER.md` and `MEMORY.md` | `~/.hermes/skills/<name>/SKILL.md` |
| Size cap | `USER.md` 1,375 chars, `MEMORY.md` 2,200 chars | No cap |
| When changes apply | **Next session.** Loaded as a snapshot at session start | Immediately on next invocation |

Preferences go in memory. Procedures go in skills. Memory does not auto-compact: a write that would blow the limit returns an **error** rather than silently dropping your older entries.

## 1.6 Checkpoint two: prove it stuck

1. Start a brand new thread, or `/new`.
2. Call your skill by name and say nothing else: `/your-skill-name`
3. Check it still knows the things you had to tell it.

The new thread has none of the conversation you just had. If it still behaves correctly, that behaviour is coming from a file you can read and edit.

**If something is missing, that is a good result.** It means the correction lived in the chat and never reached the skill. Go add it to the file by hand. That is the whole lesson.

## 1.7 Make it repeat

Create it **paused**. One command, no window where it can fire before you are ready.

```sh
hermes cron create "every day at 7am" "Run my routine skill and send me the plan." \
  --name "morning-routine" \
  --paused --paused-reason "workshop, not live yet"
```

Then:

```sh
hermes cron list
```

Note the job ID it printed. You need the real one, not the words `JOB_ID`.

```sh
hermes cron resume <job_id>
hermes cron pause <job_id>
hermes cron run <job_id>
```

Three things worth knowing before you use these:

- **`--paused-reason` requires `--paused`.** On its own it is rejected. Leave the reason off and it stores `"Created paused; awaiting operator approval."`
- **`run` will not fire a paused job.** It refuses with `Job is paused/disabled; resume it before running.` You must `resume` first. Once resumed, `run` executes immediately, it is not a dry run.
- **The scheduler ticks every 60 seconds.** Nothing happens the instant you type.

### The prompt has to stand alone

Cron jobs run in a **completely fresh agent session**. There is no conversation for it to look back on.

- Bad: `Do that again`
- Good: `Run the /morning-routine skill for tomorrow and send me the plan.`

## 1.8 Checkpoint three: let it come to you

1. `hermes cron resume <job_id>`, then `hermes cron run <job_id>`. Resume first: a paused job refuses to run.
2. **Put the laptop down. Look at your phone.**
3. `hermes cron pause <job_id>` before you leave the room.

Do not walk out with a live job you do not know how to stop.

## 1.9 Point it at something you care about

Four questions. There has never been a fifth.

1. What would I otherwise have to remember to check?
2. **How would I know the answer is wrong?**
3. Which part of this actually needs a model?
4. Where should it reach me, and when should it stay quiet?

Question three is where the money is. Most of what people reach for a model to do is a twenty-line script. The model earns its place on the ambiguous parts: reading unstructured text, making a judgement call, deciding what matters.

Question two is the one everyone skips. If you cannot say how you would spot a wrong answer, it is not ready to run on a timer.

---

# Part 2. Reference

## 2.1 Running a job with no model at all

Once a procedure is settled, a plain script can do the recurring work and cost nothing.

```sh
hermes cron create "every day at 7am" \
  --no-agent \
  --script morning-routine.py \
  --deliver discord:#home \
  --name "morning-routine"
```

**Rules, all of them enforced:**

- The script must live in **`~/.hermes/scripts/`**. Pass the bare filename. Absolute paths, `~/` expansion and `../` traversal are rejected.
- `--no-agent` requires `--script`. The script is the job.
- Interpreter is chosen by extension. `.sh` and `.bash` run under bash. **Everything else runs under Hermes' current Python.** Shebang lines are deliberately ignored.
- Cron scripts **do not inherit your provider credentials** from the Hermes environment.

**What your script's output does:**

| Script does | What happens |
|---|---|
| Exit 0, stdout has text | The text is delivered verbatim |
| Exit 0, stdout empty | Silent. Nothing is sent |
| Exit 0, last line is `{"wakeAgent": false}` | Silent |
| Non-zero exit | An error alert is delivered |
| Times out | An error alert is delivered |

Default script timeout is 3600 seconds.

Delivery targets:

```
--deliver discord:#ops
--deliver slack:#engineering
--deliver telegram
--deliver telegram:-1001234567890
--deliver signal:+15551234567
--deliver local                  # just writes to ~/.hermes/cron/output/
```

## 2.2 Schedule syntax

```
in 30m              run once, in 30 minutes
in 2h / in 1d       run once
30m                 every 30 minutes (a bare duration recurs)
every 30m / every 2h / every 1d / every hour
every day at 9am
every monday 9am
weekdays at 9am
weekends at 10am
daily at 7am
monday, wednesday at 9am
0 9 * * *           plain cron works too
0 9 * * MON-FRI
0 */6 * * *
2026-03-15T09:00:00 one-time
```

Times accept `9am`, `9:30pm`, `14:00`, `at 7`, `noon`, `midnight`.

## 2.3 Before you leave anything running

| | |
|---|---|
| **Silence** | Only speak when something changed. A job that reports every hour is a job you will mute, and then it may as well not exist. |
| **State** | It has to remember what it saw last time. That is your code's job, not the scheduler's. |
| **Failure** | A failed check is **not** a "no". Never let an error overwrite the last good answer. "Could not check" and "nothing there" are different answers. |
| **Duplicates** | Delivery is **at least once**. Recovered replies can arrive twice. Suppressing repeats is your logic, not a platform guarantee. |
| **First run** | Decide explicitly whether the very first observation should notify. Both answers are defensible. Write down which you picked. |
| **Sleep** | A closed laptop runs nothing. That is the entire argument for a small always-on box. |

## 2.4 Where everything lives

```
~/.hermes/
├── config.yaml          settings
├── .env                 keys and tokens
├── SOUL.md              agent identity
├── memories/            MEMORY.md, USER.md
├── skills/              <name>/SKILL.md
├── scripts/             cron scripts must be here
├── cron/                jobs.json, output/, executions.db
├── sessions/
└── logs/                gateway.log, errors.log
```

Config precedence, highest first: **CLI arguments → `config.yaml` → `.env` → built-in defaults.**

## 2.5 What actually leaves your machine

Hermes running locally does **not** mean your data stays local.

| Stays on your disk | Leaves, every single turn |
|---|---|
| Your files | Everything you typed |
| Your tokens and keys | Everything a tool read back |
| Your skills and memory | Contents of files it opened |
| Session history | The output it is about to send you |

What self-hosting buys you is the **choice of where that goes**: a provider whose retention terms you accept, a local model, or no model at all for jobs that need none.

Free model tiers commonly permit using your content for model improvement. Assume the one you are using today does. **Use public or invented material in this workshop.**

On connectors, two rules that have never cost anything:

- **Read-only by default.** A Gmail connector does not read one email, it reads your mail. A Notion connector with write scope on a page you wanted it to *check* can *rewrite* that page.
- **A human approves anything that writes outward.** And a web page your agent reads can contain instructions, so never let untrusted text reach a tool that writes.

## 2.6 Troubleshooting

| Symptom | First thing to check |
|---|---|
| Bot offline | Is the gateway running? `hermes gateway status`. Read its error locally. |
| Online but silent in a channel | Did you mention it? `DISCORD_REQUIRE_MENTION` defaults to true in channels, false in threads. |
| Online but silent everywhere | `Message Content Intent`. Then `DISCORD_ALLOWED_USERS`. Then channel permissions. |
| Connection drops immediately | Close code `4014`: you requested an intent that is not toggled on in the portal. |
| Replies but invents file contents | Tools are not working. A chat relay is not a working agent. |
| Model quota or error | Stop retrying. Switch provider. Free tier caps are per day and per minute. |
| Rejected at startup | Model context under 64,000 tokens. Pick a different model. |
| `Model ... is not supported` | You picked a model that is not on your provider's catalog. On `opencode-go` use `glm-5.3-flash`. |
| `RegionError` | That model is region locked. Switch models, it is not your key. |
| Skill not found | Check the exact name and that you are on the same Hermes profile. |
| Skill ignores what you taught it | Read `SKILL.md`. The correction probably never left the chat. |
| New session forgot a preference | Memory applies **next** session. Start a fresh one. |
| Job never fires | Is it paused? Check `hermes cron list`. Scheduler ticks every 60s. Is the laptop awake? |
| Job fires, nothing arrives | Check `/sethome` and the `--deliver` target. Empty stdout sends nothing by design. |
| Need to stop it right now | `/stop` cancels current work. It does **not** cancel scheduled jobs. |
| `run` says paused/disabled | That is correct behaviour. `resume` first, then `run`. |

## 2.7 Leave with these ticked

- [ ] My bot replied to something I sent from my phone
- [ ] That reply proved a tool ran
- [ ] I can say which work runs locally and what reaches the provider
- [ ] I corrected it at least three times
- [ ] I opened my `SKILL.md` and edited at least one line
- [ ] My skill worked in a fresh thread
- [ ] My job is **paused**, and I know its ID and how to stop it
- [ ] I know the workshop key dies today and what I am using tonight

---

**Maanav Dalal** · Developer Relations, Black Forest Labs
[maanavdalal.com](https://www.maanavdalal.com/) · maanav@blackforestlabs.ai

Docs: [hermes-agent.nousresearch.com/docs](https://hermes-agent.nousresearch.com/docs) · [cron](https://hermes-agent.nousresearch.com/docs/user-guide/features/cron) · [script-only cron](https://hermes-agent.nousresearch.com/docs/guides/cron-script-only) · [Discord setup](https://hermes-agent.nousresearch.com/docs/user-guide/messaging/discord)
