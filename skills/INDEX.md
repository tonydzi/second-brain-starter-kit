# Skill map — all 101

One skill = one `/name` command for Claude Code. This is the full set the lab runs every
day; personal data in the examples is replaced with plausible fictional stand-ins
(see [WHAT-IS-SHARED.md](../docs/WHAT-IS-SHARED.md)).


## Fleet and machines

| Skill | What it does |
|---|---|
| [`/bus`](bus/SKILL.md) | Cross-machine messaging between computers in the fleet over a shared TELEGRAM GROUP (primary rail) — every machine posts/reads in one group via the Te… |
| [`/inbox`](inbox/SKILL.md) | Check this machine's cross-machine mailbox — messages Claude on ANOTHER computer left for Claude here, via a file-synced bus folder (no couriers). Tri… |
| [`/fleet`](fleet/SKILL.md) | Snapshot of the autonomous Claude fleet — what the background agents across machines are doing right now, what they've built/committed, and whether an… |
| [`/follower-onboard`](follower-onboard/SKILL.md) | Onboard a NEW family/team machine as a FOLLOWER-CONSUMER joining the multi-machine Claude+vault network. A follower READS the shared vault + canon + s… |
| [`/migrate`](migrate/SKILL.md) | One command surface over the machine-migration machinery — move/sync the Claude+vault HUB role across computers (always-on desktop = hub; laptops = sa… |
| [`/raise-sync`](raise-sync/SKILL.md) | ACTIVE recovery when machines can't see each other over the file-sync network — the "raise the sync" runbook as one command. Establishes ground truth… |
| [`/sync-check`](sync-check/SKILL.md) | READ-ONLY green/red report on THIS machine's file synchronization with the whole fleet — one command instead of polling the sync REST API by hand. Sho… |
| [`/reboot`](reboot/SKILL.md) | Safe REBOOT of a fleet node (Mac or PC) by a single protocol — not just shutdown: pre-flight (save state, finish syncing, warn peers, verify autostart… |
| [`/tg-check`](tg-check/SKILL.md) | Per-machine self-test of BOTH Telegram rails (MCP + userbot library) — does THIS computer's Telegram work on both? Trigger on "/tg-check", "are both t… |
| [`/quarantine`](quarantine/SKILL.md) | Show what's currently in the QUARANTINE for incoming deliverables — fixes/scripts/tasks that arrived via file sync from an unverified source or withou… |
| [`/arch`](arch/SKILL.md) | Read the "System Architect" map — a deterministic catalog of EVERYTHING the system is made of (vault + import scripts + scheduled tasks + MCP servers… |
| [`/mcp`](mcp/SKILL.md) | Health-check the connected MCP servers and discover/suggest new ones — the safe pre-flight before any integration work, plus a connector scout. Trigge… |
| [`/03`](03/SKILL.md) | Launch autonomous multi-machine consensus between Claude peers (hub + laptops + teammate machines): the peers negotiate a decision among themselves ov… |
| [`/health-sync`](health-sync/SKILL.md) | On-demand pull of fresh messages from a set of health-related Telegram chats (medicine, supplements, longevity, fasting, etc.) into the Obsidian vault… |
| [`/tt-probe`](tt-probe/SKILL.md) | E2E probe marker for the fleet-skill-autonomy pipeline (created for a one-off verification). Do not invoke — it's a test marker; the writer may delete… |
| [`/n8n`](n8n/SKILL.md) | Health-check, audit and (on approval) fix a self-hosted n8n automation stack. Trigger on "/n8n", "/n8n health", "/n8n fix <id>", "which workflows are… |

## Quality and review

| Skill | What it does |
|---|---|
| [`/tt`](tt/SKILL.md) | QUALITY GATE right after building — "prove that what we JUST built actually works" while the context is still hot. Trigger on "/tt", "/test", "prove i… |
| [`/secondop`](secondop/SKILL.md) | A SECOND OPINION from an external LLM on every substantial task — 3 checkpoints: T1 start ("is the plan valid?"), T2 fork ("which path?"), T3 finish +… |
| [`/codex-review`](codex-review/SKILL.md) | Two-way heterogeneous code-review pair: Claude reviews Codex's diff AND Codex reviews Claude's diff — the final check is done by the OTHER vendor (res… |
| [`/codex-mirror`](codex-mirror/SKILL.md) | Rebuild the canon mirror for Codex (~/.codex/AGENTS.md) after a CLAUDE.md version bump: the engine shows the delta from the changelog, the operator wr… |
| [`/gemini`](gemini/SKILL.md) | Gemini as a THIRD external pair of eyes, alongside Codex and Grok: diff review (VERDICT: APPROVE | REQUEST_CHANGES) and QA breaker for the post-build… |
| [`/declined`](declined/SKILL.md) | Fast access to the registry of DECLINED/deferred decisions — "what we already rejected and why", so the agent never re-pitches the same idea. Trigger… |
| [`/five-hard`](five-hard/SKILL.md) | Five Hard Questions — monthly (or on demand) the second brain ITSELF asks the owner 5 hard questions about their own long-held beliefs and codex entri… |
| [`/taste-check`](taste-check/SKILL.md) | Auto-reviewer of CONTENT QUALITY (vault notes / outgoing drafts / dedup merges / service files) — an explicit verdict ✅ pass / ❌ fail / ⚠️ manual-revi… |
| [`/precedent`](precedent/SKILL.md) | Before deciding/proposing anything structural — look up whether it was ALREADY decided: searches past verdicts in the decisions journal, the declined-… |
| [`/skill-forge`](skill-forge/SKILL.md) | Peer-local skill forge — create a local-<skill> on THIS node (local autonomy lane) and prepare its promotion into the shared skill set through a gate.… |
| [`/skill-gap`](skill-gap/SKILL.md) | Audit recent Claude Code work to find which NEW skills are worth building — scan sessions for recurring MANUAL patterns that have no skill yet, cross-… |
| [`/canon-revision`](canon-revision/SKILL.md) | Full structural REVISION of an always-loaded rules file (CLAUDE.md / MEMORY.md): build a TOP block of the most important rules + numbered categories,… |
| [`/intake`](intake/SKILL.md) | Rule intake: one pass routes a new rule/preference/policy edit into ALL the right homes (always-loaded canon, memory, the behavioral Bible, a skill, a… |

## Second brain

| Skill | What it does |
|---|---|
| [`/ask`](ask/SKILL.md) | Ask the second brain in plain words — semantic search over the curated knowledge vault (embeddings + reranker), not a full-corpus dump. Trigger on "/a… |
| [`/brain`](brain/SKILL.md) | One-glance health of the "second brain" so failures aren't SILENT — is the local search server alive, is the RAG index fresh, is the session-memory le… |
| [`/obsidian-ingest`](obsidian-ingest/SKILL.md) | Universal import pipeline for an Obsidian vault. Handles ANY source: social-media posts, Telegram HTML exports, ChatGPT JSON, voice-note transcripts,… |
| [`/obsidian-backup`](obsidian-backup/SKILL.md) | The Obsidian data-safety runbook: 3-2-1 backup of the vault, the never-deleted originals archive, the schedulers that keep it running, and the restore… |
| [`/relink`](relink/SKILL.md) | Bidirectional integration of an important NEW node (concept, framework, theory, project, principle) into the WHOLE vault graph — not just creating a n… |
| [`/dedup`](dedup/SKILL.md) | Find and merge DUPLICATE / near-duplicate notes anywhere in the vault (rules, concepts, people, leads) using a deterministic scanner + a proven supers… |
| [`/defuddle`](defuddle/SKILL.md) | Clean web→markdown extraction via the defuddle CLI (the engine behind Obsidian Web Clipper) — turn any article URL into a vault-ready markdown note WI… |
| [`/wisdom-distill`](wisdom-distill/SKILL.md) | Weekly Wisdom Distill — once a week, squeeze 3-5 durable lessons from the owner's OWN words of the last 7 days into a week-note in the insights folder… |
| [`/find`](find/SKILL.md) | Find a person, lead, contact or company by name in ANY spelling — deterministic name search that catches transliteration (Viktor/Victor across alphabe… |
| [`/search`](search/SKILL.md) | Keyword/full-text search INSIDE all conversations at once — Telegram, Facebook, ChatGPT, Claude, notes, transcripts — via a local BM25/FTS5 catalog. 0… |
| [`/chat`](chat/SKILL.md) | Find a Telegram CHAT/group/channel by name instantly — returns its telegram_id + t.me link from a local chats.db index (0 tokens, no live crawl). Trig… |
| [`/chat-search`](chat-search/SKILL.md) | Search INSIDE past Claude Code sessions (the episodic "book of chats" index) — find which previous session discussed a topic, and continue it with one… |
| [`/last30days`](last30days/SKILL.md) | Deterministic "what's NEW in the last 30 days on topic X" trend-watch to run BEFORE any strategic decision — the fresh-signal feeder for the GAP phase… |
| [`/notebooklm`](notebooklm/SKILL.md) | Drive NotebookLM (the audio/artifact layer over the second brain) via a programmatic CLI, no browser — turn a vault slice into an Audio Overview / stu… |
| [`/gitbook-import`](gitbook-import/SKILL.md) | Import a GitBook space (company docs / whitepaper) into the Obsidian vault as well-linked atomic notes + MOC + concept links + RAG reindex — a proven… |
| [`/portret`](portret/SKILL.md) | Build a deep DOSSIER on a person — recall everything already known about them from the vault, map their public profiles via web research, emit a Deep-… |
| [`/journey`](journey/SKILL.md) | Resurrect and continue a build-in-public BOOK — the serialized story of a founder + AI- cofounder journey. One command: pick up state (which days are… |
| [`/reality-show`](reality-show/SKILL.md) | Season-continuity engine for serialized build-in-public content: reads a single canon file (season/arcs/beats/loops) and suggests which narrative beat… |

## Research

| Skill | What it does |
|---|---|
| [`/alfa-search-recall-deepresearch`](alfa-search-recall-deepresearch/SKILL.md) | Mandatory decision protocol ("Alpha Protocol") for any new STRATEGIC work — never jump to implementation on local recall alone. Run RECALL over the kn… |
| [`/dr-fanout`](dr-fanout/SKILL.md) | One command to fan a Deep Research prompt out to several external LLMs at once (ChatGPT / Gemini / Grok / others) through the operator's logged-in bro… |
| [`/research-swarm`](research-swarm/SKILL.md) | Research swarm — turn ANY hypothesis (however wild or fringe) into an ARGUMENT MAP, never a verdict. Fans out 5 independent lenses — Consensus, Skepti… |
| [`/alpha-judge`](alpha-judge/SKILL.md) | The LLM-JUDGE stage of an alpha-extraction engine — the reusable "expensive judge" half of the "cheap detector → expensive judge" pattern, shared by a… |
| [`/alpha-review`](alpha-review/SKILL.md) | Open the ALPHA REVIEW screen — the one place to mark judge keepers as gold/miss and see per- miner precision — and print the eval state. Trigger on "/… |
| [`/community-alpha`](community-alpha/SKILL.md) | Run ONE full community-alpha pass over an imported community-chat corpus — deterministic detector (0 tokens) → LLM judge → harvest → review screen. Tr… |
| [`/mine-channel`](mine-channel/SKILL.md) | Mine ANY Telegram channel/chat for alpha in one command — scrape (0-token, incremental) → deterministic detector shortlist → LLM judge (what's genuine… |
| [`/watch-channel`](watch-channel/SKILL.md) | Put a NIGHTLY alpha watcher on ANY Telegram channel/chat in one command — the "make channel- mining a routine" button. Registers the channel and a sin… |
| [`/issue-match`](issue-match/SKILL.md) | Measure a TARGET repository's queue + find a LIVE door (an open issue matching our artifact) BEFORE pushing a PR there. Trigger on "/issue-match", "is… |
| [`/notpeople-wave`](notpeople-wave/SKILL.md) | Run the next investor-outreach wave end-to-end, the verified way: batch of targets → personalized pitches from real templates → send via the designate… |

## People and CRM

| Skill | What it does |
|---|---|
| [`/fa`](fa/SKILL.md) | Follow-up after a call — written in the owner's authentic VOICE, not a bot template. Trigger on "/fa", "follow-up", "what should I write to <name> aft… |
| [`/intro`](intro/SKILL.md) | Make a warm INTRODUCTION between two (or more) people from the owner's network — the "introduce X to Y" operation. Trigger on "/intro", "introduce X a… |
| [`/task`](task/SKILL.md) | A delegation lane over a shared task chat: a task is assigned by a short CODE PHRASE ("task <PERSON>-<n>"), and the assignee's Claude expands it into… |
| [`/agenda`](agenda/SKILL.md) | The operator's day at a glance, on demand — today's calendar plus what needs THEM personally (leads due, real humans awaiting a reply, deadlines) pull… |
| [`/crm-sync`](crm-sync/SKILL.md) | Keep the CRM knowledge layer in the vault in sync with the live CRM code repositories. Pull the latest of the read-only repos, detect which changed, a… |
| [`/telegram-lead-outreach`](telegram-lead-outreach/SKILL.md) | How to work leads in Telegram — find prospects by topic, keep only those who SELF-mentioned it, resolve their @handle (incl. the common-groups trick),… |
| [`/telegram-assistant`](telegram-assistant/SKILL.md) | Operate Telegram as a SCOPED auto-reply assistant, grounded in the owner's knowledge vault and written in their voice. In whitelisted low-stakes chats… |
| [`/telegram-howto`](telegram-howto/SKILL.md) | Operating manual for Telegram via the connected MCP (~115 tools). How to find a chat by title, the full tool inventory grouped by job, resolving chat… |
| [`/telegram-watch`](telegram-watch/SKILL.md) | An always-on watch loop over Telegram using MCP push tools, run under a SEPARATE assistant account. Mode 1: when the assistant account is mentioned in… |
| [`/telegram-reimport`](telegram-reimport/SKILL.md) | One-command incremental RE-IMPORT of a Telegram chat that already lives in the vault. Use whenever a fresh/updated export of an already-imported chat… |
| [`/sostav-comments`](sostav-comments/SKILL.md) | Draft short, in-voice reply candidates to a fresh community-alpha shortlist — read the nightly detector report, pick posts in safe/opinion topics, pul… |
| [`/comments`](comments/SKILL.md) | Handle comments under OUR published content in one pass — show unanswered ones (default = stay silent; reply only where a reply is genuinely expected,… |

## Content

| Skill | What it does |
|---|---|
| [`/episode`](episode/SKILL.md) | Tier-based publication adapters for a content factory: take one source post and split it into drafts — teaser (short, chat-sized) · medium (main socia… |
| [`/content-mine`](content-mine/SKILL.md) | Manual run of the CONTENT MINER — read through recent Claude Code sessions and capture content-worthy moments as DRAFTS into the publishing funnel (dr… |
| [`/wow`](wow/SKILL.md) | "Milestone session → episode → publish OUT OF BAND" — at the end of a great session, one command assembles a full content episode (all tiers) from the… |
| [`/release-slice`](release-slice/SKILL.md) | The "ship a slice" ritual for open-sourcing pieces of a private system: take a component → sanitize → leak-scan (hard gate) → publish to GitHub → chan… |
| [`/speak-as`](speak-as/SKILL.md) | Write a PUBLIC post in the owner's own voice with a ROLE MODEL's style and idea-palette layered on top — a generalized engine that reads a style-palet… |
| [`/fb-post`](fb-post/SKILL.md) | Publish a VETTED post to a personal Facebook wall through the owner's real logged-in Chrome (live-tab automation = low-ban-risk path), rate-limit-guar… |
| [`/fb-reply`](fb-reply/SKILL.md) | Read who commented on the owner's recent Facebook posts and post PERSONALIZED replies through their real logged-in Chrome (live-tab, low-ban-risk), dr… |
| [`/fb-watch`](fb-watch/SKILL.md) | Monitor the owner's Facebook wall for AUTHORED posts that don't yet have a teaser, and immediately draft the teasers for the short-form channels (draf… |
| [`/tg-post`](tg-post/SKILL.md) | Publish a VETTED post to one of YOUR OWN Telegram channels/supergroups via the Telegram MCP (not a browser), channel resolved STRICTLY by id from a ch… |
| [`/x-post`](x-post/SKILL.md) | Publish a VETTED post/tweet to an X (Twitter) account through the owner's real logged-in Chrome (live-tab, low-ban-risk path), rate-guarded and draft-… |
| [`/tg-slot`](tg-slot/SKILL.md) | Free a SLOT in Telegram for a new group and join it immediately. Accounts have a hard ceiling of channels+supergroups; at the ceiling the account can… |
| [`/pipeline`](pipeline/SKILL.md) | Work the lead pipeline — CRM/outreach triage: who needs action TODAY (replied → send scheduling link; link sent 24h+ but not booked → nudge; awaiting-… |

## Source syncing

| Skill | What it does |
|---|---|
| [`/fireflies-sync`](fireflies-sync/SKILL.md) | On-demand pull of fresh calls from Fireflies.ai (auto-recording bot, real speaker names) into the Obsidian vault via the official GraphQL API, plus di… |
| [`/granola-sync`](granola-sync/SKILL.md) | On-demand pull of fresh calls/meetings from Granola (summaries + transcripts + participants) into the Obsidian vault via the official API. Incremental… |
| [`/chatgpt-sync`](chatgpt-sync/SKILL.md) | On-demand pull of FRESH ChatGPT conversations into the Obsidian vault — the manual twin of the scheduled nightly sync. Incremental + idempotent (keyed… |
| [`/claudeai-sync`](claudeai-sync/SKILL.md) | One-command incremental sync of a claude.ai WEB account into the Obsidian vault — pull only new/changed chats, fold them in as notes (idempotent, neve… |
| [`/faaa-sync`](faaa-sync/SKILL.md) | On-demand pull of FRESH follow-up call notes from a dedicated Telegram group into the CRM layer of the vault. Incremental + idempotent (dedup by Teleg… |
| [`/whatsapp-sync`](whatsapp-sync/SKILL.md) | On-demand refresh of WhatsApp text into the Obsidian vault (data layer + dashboard + group labels + contact notes). TEXT ONLY — never downloads media.… |
| [`/gmail`](gmail/SKILL.md) | Check / search / digest Gmail on demand across multiple mailboxes (personal / assistants / work) via the owner's own OAuth connector — no browser need… |
| [`/takeout-pull`](takeout-pull/SKILL.md) | Never let a Google Takeout export expire un-downloaded again. Detects "ready to download" Takeout emails in the mailbox (0-token deterministic scan),… |
| [`/local-chatgpt-token-heal`](local-chatgpt-token-heal/SKILL.md) | Refresh the ChatGPT bearer token when the nightly sync dies with a token-expired exit code. Root-cause fix: the bearer lives days but the session cook… |

## Session rituals

| Skill | What it does |
|---|---|
| [`/1`](1/SKILL.md) | Recover after a HARD session crash (app died, computer rebooted, context lost mid-work) with one ultra-short command: where were we + is everything al… |
| [`/cc`](cc/SKILL.md) | Hotkey alias for "compact the context": prints a READY-made `/compact <block>` line in a canonical handoff format so the operator can paste it as the… |
| [`/rr`](rr/SKILL.md) | Hotkey alias for /retro — the short double-letter is faster to type. IDENTICAL to /retro, zero differences (like /1 == /! and /tt == /test). On any tr… |
| [`/retro`](retro/SKILL.md) | End-of-session retrospective: (0) RECALL & reconcile this session against the whole collaboration first, (1) INVENTORY what was actually built (git lo… |
| [`/handoff`](handoff/SKILL.md) | Build a curated "semicolon" — a self-contained handoff document that lets ANOTHER session / person / machine continue the work exactly where this one… |
| [`/resume-last`](resume-last/SKILL.md) | "Continue the previous chat in one motion" — collects the LAST human session (or a specific one by id) into a seed and puts it on the clipboard: open… |
| [`/intention`](intention/SKILL.md) | The INTENTIONS lane of a content factory. One command: mine the owner's intentions from all of the day's sessions → cluster into distinct intentions →… |
| [`/coach`](coach/SKILL.md) | A daily AI coach — a forward-looking accountability + mirror loop grounded in the owner's FULL identity layer (the vault knows them better than anyone… |
| [`/cofounder`](cofounder/SKILL.md) | A synthetic COFOUNDER — an aggressive, capital-literate operator persona that spars with the founder on the BUSINESS (revenue, funnel, pricing, fundra… |
| [`/cofounder-watch`](cofounder-watch/SKILL.md) | Phase 0 of an ambient synthetic cofounder — a 0-token, PING-ONLY dispatcher that watches the LIVE lead funnel and surfaces salient events as short cof… |
| [`/bible`](bible/SKILL.md) | The operations Bible — a single behavioral codex governing everyone who acts AS or FOR the owner: the owner, human assistants, and AI agents. Load BEF… |
