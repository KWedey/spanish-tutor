# Your Spanish Learning Program

Welcome! This is your personal Spanish tutoring system. Here's everything you need to know about how it works, what to expect, and how to get the most out of it.

## How It Works

You have an AI tutor that meets with you daily through the terminal. It tracks everything — what you've learned, where you struggle, what homework you've done — and picks up exactly where you left off every session. No two sessions are the same because the tutor adapts to your progress, energy, and goals.

Between sessions, you do homework using a handful of external tools (flashcards, videos, reading). The tutor assigns specific tasks each day based on what you need.

## A Typical Day

**Before your session** (~15-30 min):
- Review your Anki flashcard deck (10-15 min daily — this is the non-negotiable habit)
- Watch a Dreaming Spanish video or listen to a podcast episode
- Optional: write a journal entry in Spanish (starts around session 10+)

**Your tutoring session** (~30-45 min):
1. Quick check-in — how's your energy? How much time do you have?
2. Homework review — what did you do? The tutor will naturally verify
3. Main lesson — new concept, practice, or consolidation depending on where you are
4. Conversation practice — you try using what you learned in a real conversation
5. Checkout — new homework assigned, quick reflection

**After your session**:
- Do the assigned homework before tomorrow
- Drop any questions or things you encountered in the parking lot (see below)

## Your Tools

These are introduced gradually — you won't set them all up on day 1.

| Tool | What it does | When you start |
|------|-------------|---------------|
| **Anki** | Flashcard app with spaced repetition — you review daily and the app knows what you're about to forget | Session 1 |
| **Dreaming Spanish** | YouTube videos in Spanish at your level — just watch, don't pause, don't look things up | Session 3 |
| **SpanishDict** | Online dictionary and conjugation reference — bookmark it | Session 3 |
| **Language Transfer** | Free audio course that builds grammar intuition | Session 5 |
| **Graded readers** | Short stories written at controlled difficulty levels | Session 5 |
| **Speechling** | You record yourself speaking, a real human gives pronunciation feedback | Sessions 7-8 |

Optional tools (the tutor will suggest these when you're ready):
- **italki** — video calls with native Spanish speakers for real conversation practice
- **Tandem** — language exchange app for text and voice chat
- **Language Reactor** — dual subtitles on Netflix for watching shows in Spanish
- **News in Slow Spanish** — podcast at slower-than-normal speed

## Your Study Companion (Obsidian Vault)

After your first session, you'll set up **Obsidian** — a note-taking app that shows you a visual dashboard of your progress. With the optional **Terminal** plugin, you can also run your tutoring sessions inside Obsidian — your vault notes on one side, your tutor conversation on the other, all in one window. You can also run sessions in your regular terminal.

**Important: don't put the vault inside a cloud-synced folder** -- iCloud, Dropbox, OneDrive, and Google Drive all run sync processes that race with Obsidian's writes and can corrupt `.md` files when two devices write simultaneously. You'll see the damage in the vault's `.trash/` folder. Store the vault in a folder that isn't synced: on macOS, use `~/Documents/language-vault` (iCloud Desktop & Documents sync is opt-in and off by default); on Windows, use `%USERPROFILE%\Documents\language-vault` (OneDrive Documents redirection is a separate configuration toggle, also off by default). If you must use a cloud-synced location, pause sync while Obsidian is open.

Open Obsidian and you'll see:

- **Home** — your dashboard with active concepts and today's homework
- **Roadmap** — a visual map of everything you'll learn, with flowcharts showing how concepts connect
- **Grammar/Vocabulary/Pronunciation notes** — one page per concept you can browse anytime
- **Progress tracking** — tables showing what you've mastered, what you're working on, and what's ahead

You don't need to edit anything in the vault — it updates automatically after each session. But you can browse it anytime to see where you are.

## The Parking Lot

There's a file called `parking-lot.md` in your project folder. This is yours to edit anytime between sessions. Use it to jot down:

- Words or phrases you heard and want to learn
- Questions about Spanish ("What's the difference between por and para?")
- Real-world situations where you got stuck ("I couldn't order at the restaurant")
- Anything you want your tutor to address

Your tutor checks this at the start of every session and works relevant items into the lesson.

## The Journal

Starting after onboarding (around session 11+), your tutor will assign daily journal entries. You write 3-7 sentences in Spanish in the `journal/` folder. Your tutor reviews them at the start of the next session — correcting errors, noting improvement, and using what you write to assess your progress.

The journal is one of the highest-value tools in the system: because you have time to think while writing, your errors reveal genuine gaps rather than performance pressure mistakes.

## Giving Feedback

There's a `feedback/` folder for anything you want the tutor to know about the *experience* — pacing, what's clicking, what isn't, how you're feeling about the program. Your tutor reads this at the start of every session.

Drop a file named `YYYY-MM-DD-short-title.md` with whatever's on your mind. There's a `TEMPLATE.md` in the folder with prompts if you're not sure what to write. Even one sentence is useful — "this feels too slow" is real signal.

Feedback about the program goes here. Spanish questions still go in `parking-lot.md`.

## Pausing and Resuming

You can quit a session any time — just close the terminal or Ctrl-C. Next time you run `claude`, the tutor picks up where you left off. If you miss a day, a week, or longer, the tutor notices and adjusts — you don't have to apologize for breaks. Nothing is lost.

## When Something Goes Wrong

Occasionally the tutor might do something you don't agree with — mark a concept as "acquired" when you don't feel you've got it, assign homework you already did, or write something weird into your state files. Everything is recoverable.

**If a session goes sideways:** tell the tutor directly. Say "I don't think I've actually acquired ser vs estar" or "that wasn't what happened in our last session." The tutor will defer to your assessment and adjust.

**If you want to undo the last session entirely:** ask the tutor to roll back. Say "please roll back the state changes from this session" — the tutor will run `python3 scripts/snapshot-state.py rollback` and restore the previous state. Your session log stays (for transparency), but skill-map, schedule, and profile return to how they were before.

**If the tutor seems confused or contradicts itself:** drop a note in `feedback/` and start a fresh session. The tutor re-reads all state at the start of every session, so most confusion resolves itself with a restart.

You can't break anything permanently. Every state change is snapshotted automatically before writes.

## What to Expect Over Time

### Phase A — Foundation (weeks 1-6)
You're building the basics: present tense, describing things, asking questions. Sessions are mostly in English with Spanish practice segments. Homework is light. You're setting up tools and building habits.

### Phase B — Conversational (weeks 7-16)
You can talk about the past and future. Sessions shift to 50/50 English and Spanish. You start the journal, get a conversation partner, and begin consuming real Spanish content. This is where it starts to feel real.

### Phase C — Intermediate (weeks 17-30)
You can express opinions, hypotheticals, and complex ideas. Sessions are mostly in Spanish. You're reading authentic content, watching TV shows, and having real conversations. The tutor corrects less and challenges more.

### Phase D — Advanced (weeks 31+)
You're refining. Sessions are almost entirely in Spanish. The focus shifts from accuracy to fluency — speaking naturally, using idioms, shifting registers. The tutor gradually hands control to you.

*These timelines are approximate — some learners move faster or slower depending on practice frequency and prior language experience.*

### Graduation
The system defines "done" based on your personal goals. When you consistently operate at your target level with minimal tutor intervention, sessions become weekly, then monthly, then on-demand.

## Tips for Success

- **Show up daily.** Even 10 minutes is better than skipping. The tutor adjusts to your energy.
- **Do your Anki.** This is the single most impactful daily habit. 10 minutes, every day.
- **Don't fear mistakes.** Your tutor tracks errors as data, not failures. Every mistake is a learning signal.
- **Use the parking lot.** The more you engage between sessions, the more the tutor can help.
- **Trust the process.** There will be plateaus. The system is designed for them — it'll change approach when something isn't working.
- **Be honest.** If something's boring, say so. If you didn't do homework, say so. The tutor adapts — but only if it knows the truth.
- **Set calendar reminders.** Especially once you reach maintenance mode (weekly or biweekly sessions), a recurring calendar reminder helps you keep the habit alive. Daily Anki review benefits from a reminder too.

## Your Data

Everything is stored locally on your machine in this project folder. You can inspect any file at any time — there are no black boxes. Your progress, your errors, your homework history — it's all in readable YAML files. You own all of it.

## Getting Help

Hit a bug or have feedback? Open an issue at https://github.com/KWedey/spanish-tutor/issues, or drop a note in `feedback/` and mention it at the start of your next session.
