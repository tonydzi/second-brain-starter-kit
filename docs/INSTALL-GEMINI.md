# Install the Second Brain kit with Gemini CLI — step by step

For people who work in Gemini, not Claude. No engineering background needed.
**Time:** ~30 minutes. **Cost:** free with a Google account (a paid Gemini plan gives higher limits).
Everything runs locally on your computer; your notes stay yours.

The kit was written for Claude Code. It works with Gemini CLI too — the only
difference is the memory file: where the kit says `CLAUDE.md`, Gemini uses
`GEMINI.md` (`~/.gemini/GEMINI.md`).

---

## Step 1 — Install Node.js (5 min, one time)
Gemini's command-line app needs it.
- **Mac:** download the "LTS" installer from https://nodejs.org → open it → Next, Next, Install.
- **Windows:** same — https://nodejs.org → LTS → run the installer with default options.

✅ **Check:** open **Terminal** (Mac: `Cmd + Space` → type Terminal) or **PowerShell**
(Windows: Start → type PowerShell) and type:
```
node -v
```
You should see a version like `v22.x`. Any number = good.

## Step 2 — Install Gemini CLI (3 min)
In the same Terminal / PowerShell window paste:
```
npm install -g @google/gemini-cli
```
Then start it:
```
gemini
```
Choose **Login with Google** and sign in with the Google account you use for Gemini.

✅ **Check:** you see the Gemini prompt where you can type. Type `hi` — it answers.
Type `/quit` to exit for now.

## Step 3 — Install Obsidian, the "eyes" of your second brain (3 min)
Download it from https://obsidian.md and install. Nothing to set up yet.

## Step 4 — Download the kit (3 min)
1. Open https://github.com/tonydzi/second-brain-starter-kit
2. Green **Code** button → **Download ZIP**.
3. Unzip it into your **Documents** folder. You get a folder named
   `second-brain-starter-kit-master` (the exact name may differ slightly — use whatever you see).

## Step 5 — Add the skills to Gemini (3 min)
In Terminal / PowerShell:
```
cd ~/Documents/second-brain-starter-kit-master
npx skills add tonydzi/second-brain-starter-kit -g
```
It asks **which agent** to install into → pick **Gemini CLI** in the list
(space to select, Enter to confirm). If it asks which skills → choose all.
The skills land in `~/.gemini/skills`.

✅ **Check:** the command ends with a list of installed skills and no red errors.

## Step 6 — First session: let Gemini set everything up (15–20 min)
1. Open [`SEED.en.md`](../SEED.en.md) from the kit folder.
2. Replace `[NAME]` with your name and adjust the "My goals" and "About me" blocks.
3. Still inside the kit folder, run `gemini` and paste the whole message
   (everything below the `---` line) as your **first message**.

The message already tells Gemini to use `~/.gemini/GEMINI.md` wherever the kit says `CLAUDE.md`.
Gemini will ask you questions, create your vault and tell you where it lives.
Then open Obsidian → **Open folder as vault** → choose that folder.

✅ **Final check (the receipt):** tell Gemini
*"Save this: today I met Alex from a partner company, we agreed to talk again next week."*
It must answer with a **receipt** ("recorded → note X"). Open that note in Obsidian.
If you see it — your second brain is alive.

## Step 7 — Daily use
| Say | What happens |
|---|---|
| "Save this: …" | anything worth remembering goes into your vault, linked |
| "What do I know about <person/project>?" | answers from your own notes, with the note name |
| "Import this" + a file / article / chat export | turns it into linked notes |
| "Wrap up the session" | files what you did and learned today |
| "Leave a handoff for tomorrow" | tomorrow's session continues where you stopped |

**Sharing with your team:** send them this same page. Each person installs it on
their own computer — their notes stay theirs.

## If something breaks
- `npm` / `node` not found → reinstall Node.js (Step 1), then close and reopen the terminal.
- `gemini` not found → close and reopen the terminal; still broken → repeat Step 2.
- Permission error on Mac during `npm install -g` → run `sudo npm install -g @google/gemini-cli`
  and type your Mac password.
- `cd` says "no such file or directory" → the unzipped folder has a different name;
  type `cd ~/Documents/second` and press Tab to auto-complete it.
- Gemini CLI is not in the agent list of `npx skills add` → start `gemini` once
  (Step 2) so the `~/.gemini` folder exists, then run Step 5 again.
- Gemini keeps writing to `CLAUDE.md` → remind it: "use ~/.gemini/GEMINI.md instead of CLAUDE.md".
- Anything else → open an issue at https://github.com/tonydzi/second-brain-starter-kit/issues
  with a screenshot of the error. Every error you report makes it easier for the next person.

---

## Prefer Claude Code?
Follow the Quick start in the [README](../README.md) and use [`SEED.en.md`](../SEED.en.md) as is.
