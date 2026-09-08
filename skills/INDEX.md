# Skill map: all 100 skills

One skill = one `/name` command for Claude Code. This is the full set the lab runs every
day; personal data in the examples is replaced with plausible fictional stand-ins
(see [WHAT-IS-SHARED.md](../docs/WHAT-IS-SHARED.md)).


## Fleet and machines

| Skill | What it does |
|---|---|
| [`/bus`](bus/SKILL.md) | Send and read messages between machines in a fleet over a shared Telegram group, so cross-machine coordination survives a file-sync outage and humans can watch the… |
| [`/inbox`](inbox/SKILL.md) | Read this machine's cross-machine mailbox, the messages another computer's agent left here over a file-synced bus folder, and send messages back the same way. |
| [`/fleet`](fleet/SKILL.md) | Show what the background agents across every machine are doing right now, what they have built or committed, and whether anything is stuck or burning tokens. |
| [`/follower-onboard`](follower-onboard/SKILL.md) | Onboard a new machine as a receive-only follower on a multi-machine agent network: |
| [`/migrate`](migrate/SKILL.md) | Move or sync the hub role of an agent-plus-vault setup between computers, where an always-on desktop is the hub and laptops are satellites. |
| [`/raise-sync`](raise-sync/SKILL.md) | Recover a fleet whose machines cannot see each other over the file-sync network: |
| [`/sync-check`](sync-check/SKILL.md) | Report this machine's file-synchronization state with the whole fleet: |
| [`/reboot`](reboot/SKILL.md) | Reboot a fleet node safely by one protocol: |
| [`/tg-check`](tg-check/SKILL.md) | Self-test both Telegram rails on this machine, the MCP connector and the userbot library, with a deterministic zero-token detector plus a real in-session MCP probe,… |
| [`/quarantine`](quarantine/SKILL.md) | List incoming deliverables held in quarantine: |
| [`/arch`](arch/SKILL.md) | Read the system-architect map: |
| [`/mcp`](mcp/SKILL.md) | Health-check the connected MCP servers and scout new ones: |
| [`/03`](03/SKILL.md) | Run an autonomous consensus round between agent peers on several machines: |
| [`/health-sync`](health-sync/SKILL.md) | Pull fresh messages from a set of health-related Telegram chats (medicine, supplements, longevity, fasting) into an Obsidian vault. |
| [`/n8n`](n8n/SKILL.md) | Health-check, audit and, on approval, fix a self-hosted n8n automation stack. |

## Quality and review

| Skill | What it does |
|---|---|
| [`/tt`](tt/SKILL.md) | Quality gate immediately after building: |
| [`/secondop`](secondop/SKILL.md) | Get a second opinion from an external LLM at three checkpoints: |
| [`/codex-review`](codex-review/SKILL.md) | Cross-vendor code review: |
| [`/codex-mirror`](codex-mirror/SKILL.md) | Rebuild the canon mirror for a second coding agent (AGENTS.md) after a rules-file version bump: |
| [`/gemini`](gemini/SKILL.md) | Use Gemini as a third external reviewer alongside two other vendors: |
| [`/declined`](declined/SKILL.md) | Look up the registry of declined and deferred decisions, so the same idea is never re-pitched: |
| [`/five-hard`](five-hard/SKILL.md) | Have the second brain ask the owner five hard questions about their own long-held beliefs and codex entries that have not been revisited, so assumptions stop… |
| [`/taste-check`](taste-check/SKILL.md) | Review content quality before anything is shown or sent (vault notes, outgoing drafts, dedup merges, service files) and return an explicit pass, fail or… |
| [`/precedent`](precedent/SKILL.md) | Check whether something was already decided before proposing it: |
| [`/skill-forge`](skill-forge/SKILL.md) | Create a node-local skill on a follower machine and prepare its promotion into the shared set through a gate. |
| [`/skill-gap`](skill-gap/SKILL.md) | Audit recent agent work for recurring manual patterns that have no skill yet, cross-check against installed skills and public skill catalogs (installing beats… |
| [`/canon-revision`](canon-revision/SKILL.md) | Restructure an always-loaded rules file such as CLAUDE.md or MEMORY.md: |
| [`/intake`](intake/SKILL.md) | Route a new rule, preference or policy edit into every home it belongs in (always-loaded canon, memory, the behavioral codex, a skill, a hook) and leave a trace in… |

## Second brain

| Skill | What it does |
|---|---|
| [`/ask`](ask/SKILL.md) | Ask the second brain in plain words: |
| [`/brain`](brain/SKILL.md) | Health-check the second brain so failures are not silent: |
| [`/obsidian-ingest`](obsidian-ingest/SKILL.md) | Import any source into an Obsidian vault as well-linked atomic notes: |
| [`/obsidian-backup`](obsidian-backup/SKILL.md) | Run the vault data-safety runbook: |
| [`/relink`](relink/SKILL.md) | Weave a new node (concept, framework, theory, project, principle) into the whole vault graph rather than just creating a note. |
| [`/dedup`](dedup/SKILL.md) | Find and merge duplicate or near-duplicate notes anywhere in a vault (rules, concepts, people, leads) with a deterministic scanner and a supersede-not-delete merge… |
| [`/defuddle`](defuddle/SKILL.md) | Turn an article URL into a clean, vault-ready markdown note with the defuddle CLI, stripping ads, navigation and comments and cutting 40-60% of tokens versus a raw… |
| [`/wisdom-distill`](wisdom-distill/SKILL.md) | Squeeze three to five durable lessons out of the owner's own words from the last seven days into a weekly note in the insights folder. |
| [`/find`](find/SKILL.md) | Find a person, lead, contact or company by name in any spelling: |
| [`/search`](search/SKILL.md) | Full-text keyword search across every conversation at once (Telegram, Facebook, ChatGPT, Claude, notes, transcripts) over a local BM25/FTS5 catalog: |
| [`/chat`](chat/SKILL.md) | Find a Telegram chat, group or channel by name and return its numeric id and t.me link from a local index, with no live crawl. |
| [`/chat-search`](chat-search/SKILL.md) | Search inside past agent sessions and continue the one that matters with a single command. |
| [`/last30days`](last30days/SKILL.md) | Report what is genuinely new in the last 30 days on a topic, by slicing locally collected nightly channel databases with no live crawling. |
| [`/notebooklm`](notebooklm/SKILL.md) | Drive NotebookLM over a programmatic CLI with no browser: |
| [`/gitbook-import`](gitbook-import/SKILL.md) | Import a GitBook space (company docs, a whitepaper) into an Obsidian vault as linked atomic notes plus a map-of-content, concept links and a RAG reindex. |
| [`/portret`](portret/SKILL.md) | Build a dossier on a person: |
| [`/journey`](journey/SKILL.md) | Pick up and continue a serialized build-in-public book: |
| [`/reality-show`](reality-show/SKILL.md) | Keep serialized build-in-public content continuous: |

## Research

| Skill | What it does |
|---|---|
| [`/alfa-search-recall-deepresearch`](alfa-search-recall-deepresearch/SKILL.md) | Decision protocol for strategic work: |
| [`/dr-fanout`](dr-fanout/SKILL.md) | Fan one deep-research prompt out to several external LLMs at once through a logged-in browser, then collect the reports, archive the originals and synthesize a… |
| [`/research-swarm`](research-swarm/SKILL.md) | Turn any hypothesis, however fringe, into an argument map rather than a verdict: |
| [`/alpha-judge`](alpha-judge/SKILL.md) | LLM-judge stage of an alpha-mining pipeline: |
| [`/alpha-review`](alpha-review/SKILL.md) | Open the alpha review screen to mark judge keepers as gold or miss, read per-miner precision, and print the eval state. |
| [`/community-alpha`](community-alpha/SKILL.md) | Run one full mining pass over an imported community-chat corpus: |
| [`/mine-channel`](mine-channel/SKILL.md) | Mine any Telegram channel or chat for signal in one command: |
| [`/watch-channel`](watch-channel/SKILL.md) | Put a nightly watcher on any Telegram channel or chat in one command: |
| [`/issue-match`](issue-match/SKILL.md) | Measure a target repository's queue and find a live open issue the contribution would close, before opening a pull request there. |
| [`/notpeople-wave`](notpeople-wave/SKILL.md) | Run an investor-outreach wave end to end: |

## People and CRM

| Skill | What it does |
|---|---|
| [`/fa`](fa/SKILL.md) | Write the follow-up after a call in the owner's own voice instead of a bot template: |
| [`/intro`](intro/SKILL.md) | Introduce two or more people from the owner's network: |
| [`/task`](task/SKILL.md) | Delegate work over a shared task chat: |
| [`/agenda`](agenda/SKILL.md) | Show the operator's day: |
| [`/crm-sync`](crm-sync/SKILL.md) | Sync CRM knowledge notes in a vault with the live CRM code repositories: |
| [`/telegram-lead-outreach`](telegram-lead-outreach/SKILL.md) | Work leads in Telegram: |
| [`/telegram-assistant`](telegram-assistant/SKILL.md) | Run Telegram as a scoped auto-reply assistant grounded in the owner's vault and written in their voice: |
| [`/telegram-howto`](telegram-howto/SKILL.md) | Operating manual for Telegram over its MCP connector and roughly 115 tools: |
| [`/telegram-watch`](telegram-watch/SKILL.md) | Run an always-on Telegram watch loop under a separate assistant account using MCP push tools. |
| [`/telegram-reimport`](telegram-reimport/SKILL.md) | Fold a fresh export of an already-imported Telegram chat into a vault, adding only the new messages. |
| [`/sostav-comments`](sostav-comments/SKILL.md) | Draft short, in-voice reply candidates to a fresh community shortlist: |
| [`/comments`](comments/SKILL.md) | Work the comments under published posts in one pass: |

## Content

| Skill | What it does |
|---|---|
| [`/episode`](episode/SKILL.md) | Split one source post into tier-sized drafts (teaser, main social post, longread, technical dev-log) with cross-links downward and a canonical link back to the… |
| [`/content-mine`](content-mine/SKILL.md) | Scan recent agent sessions for content-worthy moments and capture them as drafts in a publishing funnel, publishing nothing. |
| [`/wow`](wow/SKILL.md) | Assemble a full multi-tier content episode from a milestone session's hot context and publish it out of band, ahead of the nightly schedule: |
| [`/release-slice`](release-slice/SKILL.md) | Open-source one slice of a private system: |
| [`/speak-as`](speak-as/SKILL.md) | Write a public post in the owner's own voice with a role model's style and idea palette layered on top, reading a style-palette file so the same engine works for… |
| [`/fb-post`](fb-post/SKILL.md) | Publish an already-vetted post to a personal Facebook wall through the owner's real logged-in Chrome tab (a low-ban-risk path), rate-limit-guarded and draft-first: |
| [`/fb-reply`](fb-reply/SKILL.md) | Read who commented on recent Facebook posts and publish personalized replies through the real logged-in Chrome tab, draft-first, with a daily cap and a minimum gap… |
| [`/fb-watch`](fb-watch/SKILL.md) | Check a Facebook wall for authored posts that have no teaser yet and draft the teasers for short-form channels. |
| [`/tg-post`](tg-post/SKILL.md) | Publish a vetted post to one of your own Telegram channels or supergroups over the MCP connector rather than a browser, with the channel resolved strictly by id… |
| [`/x-post`](x-post/SKILL.md) | Publish a vetted post to an X (Twitter) account through the owner's real logged-in Chrome tab, rate-guarded and draft-first. |
| [`/tg-slot`](tg-slot/SKILL.md) | Free a membership slot so a Telegram account can join or create a group. |
| [`/pipeline`](pipeline/SKILL.md) | Triage a lead pipeline and say who needs action today: |

## Source syncing

| Skill | What it does |
|---|---|
| [`/fireflies-sync`](fireflies-sync/SKILL.md) | Pull fresh call recordings and transcripts from Fireflies.ai into an Obsidian vault over the official GraphQL API, then distill action items and commitments and… |
| [`/granola-sync`](granola-sync/SKILL.md) | Pull fresh meetings from Granola (summaries, transcripts, participants) into an Obsidian vault over the official API. |
| [`/chatgpt-sync`](chatgpt-sync/SKILL.md) | Pull fresh ChatGPT conversations into an Obsidian vault on demand, the manual twin of the nightly job. |
| [`/claudeai-sync`](claudeai-sync/SKILL.md) | Pull new and changed claude.ai web conversations into an Obsidian vault, extract artifacts as first-class notes, concept-link them, and refresh the RAG index and… |
| [`/faaa-sync`](faaa-sync/SKILL.md) | Pull fresh follow-up call notes from a dedicated Telegram group into the CRM layer of a vault. |
| [`/whatsapp-sync`](whatsapp-sync/SKILL.md) | Refresh WhatsApp text into an Obsidian vault (data layer, dashboard, group labels, contact notes). |
| [`/gmail`](gmail/SKILL.md) | Check, search or digest Gmail across several mailboxes over the owner's own OAuth connector, with no browser and near-zero tokens for the raw pull. |
| [`/takeout-pull`](takeout-pull/SKILL.md) | Stop a Google Takeout export from expiring undownloaded: |
| [`/local-chatgpt-token-heal`](local-chatgpt-token-heal/SKILL.md) | Re-mint a ChatGPT bearer token when a nightly sync exits with a token-expired code: |

## Session rituals

| Skill | What it does |
|---|---|
| [`/1`](1/SKILL.md) | Recover a session after a hard crash (app died, machine rebooted, context lost mid-work): |
| [`/cc`](cc/SKILL.md) | Print a ready-made /compact line in a canonical handoff format, so the operator pastes it as the next message and shrinks working memory without losing the thread. |
| [`/rr`](rr/SKILL.md) | Alias for the retro skill: |
| [`/retro`](retro/SKILL.md) | Close a work session properly: |
| [`/handoff`](handoff/SKILL.md) | Write a self-contained handoff document so another session, person or machine continues the work without this session's context: |
| [`/resume-last`](resume-last/SKILL.md) | Collect the last human session, or a specific one by id, into a seed on the clipboard, so a new session continues where the old one broke off, including after a… |
| [`/intention`](intention/SKILL.md) | Mine the day's sessions for the owner's intentions, cluster them into distinct ones, store them, and write two or three detailed posts with an explicit ask per… |
| [`/coach`](coach/SKILL.md) | Run a daily accountability loop grounded in the owner's identity layer in the vault: |
| [`/cofounder`](cofounder/SKILL.md) | Spar with the founder as a synthetic cofounder on business questions (revenue, funnel, pricing, fundraising, debt, hiring, runway) with numbered objections and no… |
| [`/cofounder-watch`](cofounder-watch/SKILL.md) | Watch a live lead funnel with a zero-token dispatcher and surface salient events as short advice: |
| [`/bible`](bible/SKILL.md) | Load the operations codex that governs everyone acting as or for the owner (the owner, human assistants and AI agents) before outreach, replies in their chats,… |
