# Skill map: all 230 skills

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

## Added since v0.3.0 (groomed)

| Skill | What it does |
|---|---|
| [`/continue`](continue/SKILL.md) | Drive the current task to a verified result instead of stopping at a plausible report. Use when the user says /continue, keep going, not done yet, pus… |
| [`/fundraise`](fundraise/SKILL.md) | - КАК ДЕЛАЕТСЯ ФАНДРЕЙЗИНГ - общий плейбук рейза по этапам 0-7 (подготовка и активы -> нарратив -> структура сделки -> пайплайн и momentum -> заголовк… |
| [`/five-whys`](five-whys/SKILL.md) | Investigate the root cause of a recurring or systemic defect across a series of incidents, not a single one. Use on the third recurrence, or when… |
| [`/fake-it`](fake-it/SKILL.md) | Sell layer: raise the framing of an artifact to the scale it actually deserves without touching a single number. Use before anything goes outbound… |
| [`/deflate`](deflate/SKILL.md) | Cut background heat and noise on this machine: audit scheduled tasks by runs per hour, autostart entries, GPU holders, power plan and top CPU, then… |
| [`/link-rot`](link-rot/SKILL.md) | Sweep every external pointer to you (profiles, READMEs, bios, link pages) after a rename of a repo, org, domain, handle or account, and fix the dead… |
| [`/worth`](worth/SKILL.md) | Score how much attention a person deserves: classify them (investor, engineer, student, partner, community, noise, personal), estimate the value they… |
| [`/promises`](promises/SKILL.md) | Track and collect promises: every promise, theirs to us and ours to them, goes into a registry with date and source, gets a reminder when due and is… |
| [`/read-with-ai`](read-with-ai/SKILL.md) | Add a 'Read with AI' widget under published content: a copy-the-prompt button plus deep links that open the material already loaded into an agent… |
| [`/elephant`](elephant/SKILL.md) | Eat the elephant one bite at a time: turn a large list-shaped job into a finite routine that chews a small batch every night, detects when it is… |
| [`/decide-as-cofounder`](decide-as-cofounder/SKILL.md) | Decide-as-cofounder mode: the owner hands over the decision itself, so the agent does not ask back, does not offer a menu of options and does not… |
| [`/llm-pact`](llm-pact/SKILL.md) | Protocol for two LLM agents (Claude, Codex or any other) to agree and work from one shared folder: message format, channels, roles, evidence rules,… |

## Raw imports, grooming in progress

These arrived with the full local set and still carry their original working descriptions (mostly Russian). A nightly routine grooms about ten a night: English description, MIT license, fictional data. They are scanned for secrets like everything else.

| Skill | Original description |
|---|---|
| [`/ai-slop`](ai-slop/SKILL.md) | АНТИ-AI-SLOP ХУМАНИЗАТОР (Антон зовёт его AI_SLOPE) — берёт текст, написанный роботом, и переделывает в текст живого ОЧЕНЬ ЗАНЯТОГО человека: режет 50… |
| [`/alpha-credit`](alpha-credit/SKILL.md) | - КРЕДИТ АВТОРУ ИДЕИ: совет из комментария (TG @ClawRus / @ClawInga, комменты под постами Антона в FB, треды и issue на… Триггеры: “/alpha-credit“, “/… |
| [`/ask-any`](ask-any/SKILL.md) | ПОРУЧИТЬ РАБОТУ ЛЮБОЙ ЖИВОЙ LLM, а не только Claude: задание уходит ОДНОВРЕМЕННО на codex + grok + gemini + claude, побеждает первая ответившая. Тригг… |
| [`/ask-debt`](ask-debt/SKILL.md) | READ-ONLY замер «ДОЛГА АВТОНОМНОСТИ» по журналу одобрений 02 (approvals.db) — сколько я спросил Антона за окно, сколько из этого ПРОТУХЛО (никто не от… |
| [`/audit-content`](audit-content/SKILL.md) | Verifies truthfulness, accuracy, and link integrity of content before publishing. Catches fabricated statistics, dead URLs, misattributed sources, and… |
| [`/audit-website-aeo`](audit-website-aeo/SKILL.md) | Audits a live website for AI-engine discoverability (AEO/GEO). Crawls the site, runs 16 deterministic checks plus a 6-dimension content evaluation, an… |
| [`/bold-followup`](bold-followup/SKILL.md) | Наглый фоллоуап, когда НАШЕ исходящее молчит. Триггеры “/bold-followup“, “/bump“, “наглый аутрич“, “письмо молчит“, “тишина от лида“, “фоллоуап по тиш… |
| [`/borrowed-audience`](borrowed-audience/SKILL.md) | Добыть ВНЕШНИЕ ССЫЛКИ на наши репо через чужие курируемые поверхности — awesome-lists, каталоги тулов, вендорские showcase. Триггеры “/borrowed-audien… |
| [`/brain-onboard`](brain-onboard/SKILL.md) | Onboard a NEW human peer ([коллега], [коллега], [коллега], future family/colleagues/clients) into building THEIR OWN Second Brain — the HUMAN layer th… |
| [`/build-backlinks`](build-backlinks/SKILL.md) | Finds free backlink and brand mention opportunities across Hacker News, Quora, GitHub, directories, and niche communities. Outputs a prioritized actio… |
| [`/build-resource-pages`](build-resource-pages/SKILL.md) | Takes existing content markdown files and builds production-final resource center pages on client websites using their existing tech stack and design … |
| [`/chip`](chip/SKILL.md) | ЧИП ТОЛЬКО ПО ПРЯМОМУ ЗАПРОСУ ЮЗЕРА (anton 14.08): сделать ЧИПЫ (spawn_task), которые юзер нажмёт сам. |
| [`/comment-to-call`](comment-to-call/SKILL.md) | ВОРОНКА «ПОЛЕЗНЫЙ ЧЕЛОВЕК → ДИАЛОГ → ЗВОНОК»: каждый, кто дал нам пользу / написал качественный коммент / покритиковал по-доброму / поделился знанием … |
| [`/consumer-hunt`](consumer-hunt/SKILL.md) | - ВЫПУСТИЛ ФУНКЦИОНАЛ → НАЙДИ ЕГО ПОТРЕБИТЕЛЕЙ НА GITHUB И ПРИДИ К НИМ. Триггеры: “/consumer-hunt“, “/ch“, “кому это нужно“, “найди потребителей“, “ку… |
| [`/contrib-watch`](contrib-watch/SKILL.md) | - СТОРОЖ ВХОДЯЩЕГО ФИДБЭКА: кто из посторонних инженеров пришёл к НАШИМ репозиториям, что написал, сколько часов ждёт… Триггеры: “/contrib-watch“, “/c… |
| [`/corpus-bench`](corpus-bench/SKILL.md) | Станок верификации чужого кода на НАШИХ живых корпусах (GIT-25). Триггеры - “/corpus-bench“, “прогони по корпусу“, “проверь их фикс на наших транскрип… |
| [`/create-geo-charts`](create-geo-charts/SKILL.md) | Creates data visualizations (charts, graphs, tables) optimized for AI engine parsing and citation. Produces inline SVG/HTML with text summaries, data … |
| [`/dash`](dash/SKILL.md) | ДАШБОРД ОТ ИДЕИ ДО ССЫЛКИ В ОДИН ЗАХОД: собрать визуализацию, положить в единый каталог, перелинковать с остальными, выложить на наш GitHub Pages, СРА… |
| [`/devrel-wave`](devrel-wave/SKILL.md) | - МУЛЬТИКАНАЛЬНАЯ ЛЕСТНИЦА КАСАНИЙ к DevRel/research-людям топ-LLM лабов: 1 прицельный человек = 1 вендор, касания идут по 2-3 каналам, а не одним DM … |
| [`/dig-through-data-brokers`](dig-through-data-brokers/SKILL.md) | - Use people-search aggregators and primary public records to find addresses, phone numbers, relatives, age and background on a person, and to audit a… |
| [`/dr-teasers`](dr-teasers/SKILL.md) | ДР-ПОЛОСА — превратить наши дипресёрчи в 10 тизеров в день и разослать их по каналам лаборатории. Триггеры “/dr-teasers“, “/dr-lane“, “тизеры по ресёр… |
| [`/engineer-pool`](engineer-pool/SKILL.md) | Наполнение пула ИНЖЕНЕРОВ-ТЕСТЕРОВ под миссию №2 из живых issue вендорских и агентных репо (не из крипто-базы leads.db). Триггеры: «/engineer-pool», «… |
| [`/fb-audience`](fb-audience/SKILL.md) | Вычислить нашу тёплую аудиторию в Facebook — кто регулярно лайкает и комментирует НАШИ посты — и превратить её в актив: дедуп, перелинковка с CRM, зав… |
| [`/fb-likes`](fb-likes/SKILL.md) | Ежедневная лайк-активность в Facebook двумя лейнами. Триггеры «/fb-likes», «/fb-like», «лайк-хвост», «пролайкай комменты», «обход лидов», «полайкай ли… |
| [`/find-anyone`](find-anyone/SKILL.md) | - Build a sourced, corroborated profile of a named individual from public records, social platforms, professional networks, court and property filings… |
| [`/find-exposed-servers`](find-exposed-servers/SKILL.md) | - Find internet-exposed hosts, ports, services and devices using third-party internet-scan data instead of touching the target. Use when asked what a … |
| [`/find-hidden-subdomains`](find-hidden-subdomains/SKILL.md) | - Enumerate an organisation's subdomains and sibling domains from Certificate Transparency logs and passive DNS, without sending traffic to the target… |
| [`/find-leaks-in-the-wild`](find-leaks-in-the-wild/SKILL.md) | - Find leaked or mentioned selectors circulating in pastes, leak forums, Telegram channels and dump markets, and judge whether a claimed leak is genui… |
| [`/find-person`](find-person/SKILL.md) | Найти человека и его каналы связи по нашим ЖЕ данным: архив ТГ 16.7 млн сообщений, CRM, книга чатов, почта, досье. Триггеры: /find-person, найди хэндл… |
| [`/find-the-original-image`](find-the-original-image/SKILL.md) | - Reverse image search across Yandex, Google Lens, Bing Visual Search, TinEye and Baidu to find where a picture came from and who published… Use when … |
| [`/firefox`](firefox/SKILL.md) | БРАУЗЕР ПО УМОЛЧАНИЮ = FIREFOX (решение Антона 2026-07-30, канон decision-2026-07-16-browser-automation-layer). Триггеры: /firefox, /ff, «через firefo… |
| [`/follow-the-crypto`](follow-the-crypto/SKILL.md) | - Trace cryptocurrency addresses and transactions on public blockchains using block explorers including Etherscan, Blockchair, mempool.space and Block… |
| [`/geo-content-planning`](geo-content-planning/SKILL.md) | Reads existing brand DNA, keywords.csv, and prompts.csv, then produces a plan.csv — a strictly-schema'd content architecture telling the next pipeline… |
| [`/geo-content-research`](geo-content-research/SKILL.md) | Researches what prompts people ask AI engines (ChatGPT, Gemini, Perplexity, Claude) about a product category and produces a prompts.csv artifact — a p… |
| [`/geo`](geo/SKILL.md) | GEO-замер — цитируют ли нас AI-движки. Три стадии (краул → индекс → цитата), каждая мерится отдельно. Используй, когда речь про находимость, SEO/GEO, … |
| [`/geolocate-from-pixels`](geolocate-from-pixels/SKILL.md) | - Geolocate and chronolocate a photo or video from visual evidence alone — plate and phone number formats, road markings, utility poles, bollards, sig… |
| [`/gh-discussions`](gh-discussions/SKILL.md) | ОТДЕЛЬНАЯ ДВЕРЬ под GitHub Discussions — Q&A-поверхность, где ответ помечается как «Answer», у автора ответа растёт… Триггеры: “/gh-discussions“, “/gh… |
| [`/github-growth`](github-growth/SKILL.md) | КАК МЫ ДВОЕ (Антон + Макс) продвигаемся на GitHub — рабочий манифест лейнов, не теория. Триггеры: /github-growth, /ghg, «как продвигаться на гитхабе»,… |
| [`/goblin`](goblin/SKILL.md) | - ГОЛОС РАННИЙ ГОБЛИН — написать текст Антона в измеренной манере раннего [человек] Пучкова (oper.ru 2000-2014): рубленый ритм, абзац в 1-2 предложени… |
| [`/gonka-fundraise`](gonka-fundraise/SKILL.md) | - Фандрайз по методике Гонки: упаковать НАШ рейз/анонс/заголовок по каталогу приёмов Gonka/Либерманов (журналистское досье, anton голосом 26.08.2026)…… |
| [`/google-like-a-spy`](google-like-a-spy/SKILL.md) | - Craft advanced search-engine queries and Google dorks to surface hidden files, documents and mentions. Use when building a Google dork, hunting a le… |
| [`/graph-the-network`](graph-the-network/SKILL.md) | - Build an entity-relationship link-analysis graph of an investigation — nodes, typed edges carrying source and confidence, aliases, and temporal vali… |
| [`/grok-sync`](grok-sync/SKILL.md) | Pull Anton's Grok (grok.com / SuperGrok) conversation history into the Obsidian vault from an official Grok data export (prod-grok-backend.json). Trig… |
| [`/guide`](guide/SKILL.md) | Вечнозелёный ГАЙД по «формуле Юницкого» — обучающий лонгформ для не-технарей (Дзен-урок-сшивка, GitHub гайд-хаб, LJ), собранный из НАШЕЙ живой фактуры… |
| [`/hk`](hk/SKILL.md) | «Что уже сделали роботы сегодня» — экран состояния обслуживания ПЕРЕД тем, как чинить руками. Триггеры: “/hk“, “/housekeeping“, “/уборка“, “что сегодн… |
| [`/hubrun`](hubrun/SKILL.md) | Прогнать PowerShell-скрипт или команду на удалённом узле флота (дефолт: хаб [машина флота]) и получить вывод назад ОДНОЙ командой. Trigger on «/hubrun… |
| [`/hunt-a-handle`](hunt-a-handle/SKILL.md) | - Enumerate a username across hundreds of platforms with sherlock, maigret and WhatsMyName, then correlate and confirm which accounts genuinely belong… |
| [`/hyper-research`](hyper-research/SKILL.md) | ГИПЕР-РЕСЁРЧ: один вопрос уходит в максимум НЕЗАВИСИМЫХ LLM разом (рельса = вендор#аккаунт: Claude x3 бака, ChatGPT x2, Gemini, Grok, GLM, Mistral), к… |
| [`/improve-aeo-geo`](improve-aeo-geo/SKILL.md) | Audits a website codebase and makes code changes so AI engines (ChatGPT, Claude, Perplexity, Google AI Overviews) can better discover, parse, quote, a… |
| [`/investigate-anything`](investigate-anything/SKILL.md) | - Start-here router and tradecraft baseline for any investigation into a person, company, domain, image or selector. |
| [`/investigate-without-getting-made`](investigate-without-getting-made/SKILL.md) | - Investigator OPSEC — threat-model who might notice you, control your attribution surface across IP, ASN, browser and TLS fingerprint, timing and log… |
| [`/is-this-photo-real`](is-this-photo-real/SKILL.md) | - Verify whether an image or video is authentic, original and correctly captioned — provenance checks, error level analysis, noise and JPEG compressio… |
| [`/ledger`](ledger/SKILL.md) | «Что было в тот день» — мгновенный ответ из дневного леджера, который роботы собирают каждую ночь из бесплатных следов… Триггеры: “/ledger“, “/день“, … |
| [`/llll`](llll/SKILL.md) | /LLLL = короткий алиас /LLMs: решить текущий вопрос через адресный ограниченный консенсус других LLM. Триггеры: /LLLL, llll, четыре l. Вся логика живё… |
| [`/llms`](llms/SKILL.md) | /LLMs решает текущий вопрос через ограниченный консенсус Claude, Codex, Cursor, Grok и других пиров. Передаёт тему и контекст сессии, читает только ад… |
| [`/memory-tidy`](memory-tidy/SKILL.md) | Привести в порядок всегда-загружаемый индекс памяти MEMORY.md на этой машине (macOS/Linux) — подрезать, унести закрытое в архив, сложить домены в хабы… |
| [`/mycroft-joke`](mycroft-joke/SKILL.md) | Дверь к банку шуток Майкрофта: подобрать строку раскрытия/ответку/гэг под конкретный текст и канал. Триггеры: '/mycroft-joke', '/mj', 'шутка майкрофта… |
| [`/nsr`](nsr/SKILL.md) | NEW SESSION IN ROUTINE: я САМ поднимаю новую ВИДИМУЮ сессию через запланированную задачу — Антону жать нечего, но в списке он её видит и может продолж… |
| [`/outbound-gate`](outbound-gate/SKILL.md) | ГЕЙТ ЛЮБОГО ИСХОДЯЩЕГО (PR/issue-коммент/DM/инвайт/пост/заявка/аутрич): исходящее обязано закрывать ЧЬЮ-ТО живую просьбу (анкер), выстрел в пустоту = … |
| [`/pack`](pack/SKILL.md) | 📦 УПАКОВКА КОНТРИБЬЮШЕНА КАК ПРОДУКТА (декрет Антона 24.08.2026: «нам нужно всегда делать КАЧЕСТВЕННО... Триггеры: “/pack“, “/упакуй“, “упакуй как про… |
| [`/pattern-of-life-from-socials`](pattern-of-life-from-socials/SKILL.md) | - Deep-dive a subject's social media presence — profile metadata, follower and mutual network, content analysis, and posting-time pattern of life acro… |
| [`/peer-onboard`](peer-onboard/SKILL.md) | Онбординг КЛОДА нового внешнего лида/пира в наш Second Brain — вся цепочка одной командой: оформить TG-комнату (название по формуле,… Триггеры: “/peer… |
| [`/pr-reply`](pr-reply/SKILL.md) | - ОТВЕТИТЬ РЕВЬЮЕРУ на НАШЕМ пул-реквесте в чужом репозитории: найти треды, где мяч у нас, отделить живого человека от бота, сделать ровно то,… Тригге… |
| [`/pult`](pult/SKILL.md) | 📱 ПУЛЬТ — ежедневная ПУСТАЯ сессия с Remote Control на каждом узле Антона, чтобы он мог управлять машиной с ТЕЛЕФОНА без AnyDesk. Триггеры “/pult“, “/… |
| [`/raise-sourcing`](raise-sourcing/SKILL.md) | - СОРСИНГ ПОД РЕЙЗ в два трека: инвесторы из нашего VC-графа (leads.db) и покупатели-пилоты, найденные ПО СИМПТОМУ в интернете (GitHub issues, Hacker … |
| [`/read-deleted-pages`](read-deleted-pages/SKILL.md) | - Recover deleted, edited or historical web content using the Wayback Machine and its CDX API, archive.today, Common Crawl… Use when a page is deleted… |
| [`/recon-a-domain-passively`](recon-a-domain-passively/SKILL.md) | - End-to-end passive reconnaissance for a domain, website or IP — builds an asset inventory covering registration, DNS, subdomains, infrastructure, te… |
| [`/red-first-review`](red-first-review/SKILL.md) | Review someone else's pull request by measuring which of its own guards its own test suite actually catches. Use when reviewing a PR, auditing test co… |
| [`/reddit-opportunity-research`](reddit-opportunity-research/SKILL.md) | Researches Reddit using a brand's Brand DNA to find promotable pain-point discussions, target subreddits, and real user search language. Produces a pr… |
| [`/rep-reply`](rep-reply/SKILL.md) | Найти ЖИВЫЕ чужие треды (GitHub issues/discussions) по темам, где у нас есть РЕАЛЬНЫЙ боевой опыт и артефакты, и ответить в них нашим опытом — прокачк… |
| [`/research-brand`](research-brand/SKILL.md) | Researches a company from its URL and produces a Brand DNA file covering positioning, audience, competitors, voice, and messaging. Use when starting w… |
| [`/research-keywords`](research-keywords/SKILL.md) | Finds high-value SEO and GEO keywords using web search, AI analysis, and optionally paid tools like Ahrefs or Semrush. Produces a validated keywords.c… |
| [`/retro-lost`](retro-lost/SKILL.md) | Ретро для БРОШЕННОЙ сессии (>24ч без касания = потеряшка, anton 02.09; ретро не делалось) — переработанный /retro под холодный контекст. Триггеры: “/r… |
| [`/routine-opt`](routine-opt/SKILL.md) | Аудит и УДЕШЕВЛЕНИЕ парка рутин узла: кто сколько жрёт за прогон, какой рычаг применить (модель · декомпозиция · частота · префикс · утиль) и как дока… |
| [`/scholar-nerd-style`](scholar-nerd-style/SKILL.md) | СТИЛЬ УЧЁНОГО ЗАДРОТА — фирменный визуальный язык наших сайтов-документов: рукописный HTML в один файл, шрифт с… Триггеры “/scholar-nerd-style“, “/ner… |
| [`/screenpipe-api`](screenpipe-api/SKILL.md) | Query the user's local and synced-device data via the screenpipe REST API at localhost:3030 — recordings, audio, UI, meetings, connected services, and… |
| [`/screenpipe-cli`](screenpipe-cli/SKILL.md) | Set up and operate screenpipe from the terminal, including always-on recording, service modes, capture health, storage, local search, pipes, and conne… |
| [`/screenpipe-durable-learning`](screenpipe-durable-learning/SKILL.md) | Turn a verified correction or repeated workflow into a reusable local learning. |
| [`/screenpipe-focus-review`](screenpipe-focus-review/SKILL.md) | Review focus and context switching over a chosen period without inventing productivity scores. |
| [`/screenpipe-meeting-follow-up`](screenpipe-meeting-follow-up/SKILL.md) | Capture decisions and commitments after a meeting and draft a concise follow-up. |
| [`/screenpipe-meeting-prep`](screenpipe-meeting-prep/SKILL.md) | Prepare for a specific upcoming meeting using verified identity and prior context. |
| [`/screenpipe-recall`](screenpipe-recall/SKILL.md) | Find a past decision, document, or conversation in Screenpipe with source links. |
| [`/screenpipe-research-synthesis`](screenpipe-research-synthesis/SKILL.md) | Synthesize repeated themes from selected research conversations or notes. |
| [`/screenpipe-shareable-recap`](screenpipe-shareable-recap/SKILL.md) | Create a shareable recap of selected Screenpipe activity while minimizing private details. |
| [`/screenpipe-worklog`](screenpipe-worklog/SKILL.md) | Reconstruct a daily or weekly worklog from observed activity and outcomes. |
| [`/secrets-in-file-metadata`](secrets-in-file-metadata/SKILL.md) | - Extract and interpret embedded file metadata with exiftool — EXIF GPS coordinates, camera make, model and serial, DateTimeOriginal and CreateDate ti… |
| [`/secrets-in-git-history`](secrets-in-git-history/SKILL.md) | - Mine GitHub, GitLab and git history for identities, infrastructure and leaked credentials using commit author emails, GitHub code search, the commit… |
| [`/session-groups`](session-groups/SKILL.md) | Пометить КАЖДУЮ сессию Claude Desktop (Code tab) ИКОНКОЙ её группы прямо в заголовке — «⚙️ Имя», «💰 Р+ Имя». Пока сайдбар-инструмент ccd_sidebar запер… |
| [`/sessions`](sessions/SKILL.md) | Показать одним экраном, ЧТО СЕЙЧАС ДЕЛАЮТ сессии Claude на этой машине: сколько работает и над чем, сколько закрылось за 12ч, что ЖДЁТ решения Антона … |
| [`/share-fix`](share-fix/SKILL.md) | - 🌍 ПОЧИНИЛ — РАЗДАЙ МИРУ (декрет Антона 24.08.2026, голосом): переносимая починка КЛАССА / добытый результат → в том же заходе найти страдальцев на G… |
| [`/slot`](slot/SKILL.md) | РЕЕСТР ПЕРЕИСПОЛЬЗУЕМЫХ СЕССИЙ + выдача слота: породить ВИДИМУЮ Антону фоновую сессию БЕЗ апрув-окна, переиспользовав… Триггеры: /slot, /слот, «дай сл… |
| [`/social-daily`](social-daily/SKILL.md) | Единый вход публикации контент-фабрики на все живые площадки: Facebook, X, Telegram-каналы, Threads, Instagram. Публикую САМ. Триггеры: /social-daily,… |
| [`/sostav-dm`](sostav-dm/SKILL.md) | Личка и реплаи лидам клуба СОСТАВ в стиле Антона: два текста на лида (reply в группе под его свежим сообщением + личка), удочка без подсечки на первом… |
| [`/sostav-reply`](sostav-reply/SKILL.md) | Ответы Антона в топики клуба СОСТАВ полным циклом: показать черновик ВМЕСТЕ с исходным диалогом (на что отвечаем) → Антон выбирает основной/запасной/с… |
| [`/spawn-bridge`](spawn-bridge/SKILL.md) | ⭐ ПРАВИЛО (anton 23.09 голосом): «подними сессию/декомпозируй» адресовано ТЕБЕ = поднимай У СЕБЯ, своими средствами (Cursor → Task-tool/background age… |
| [`/sync-sessions`](sync-sessions/SKILL.md) | Сделать сессии Claude Code на ЭТОМ компьютере видимыми под любым аккаунтом, как локальные треды Codex. Триггеры: /sync-sessions, «синхронизируй сессии… |
| [`/teach-podcast`](teach-podcast/SKILL.md) | Учебные аудиоподкасты для Антона в NotebookLM: выбирает, чему учить (труба собеседований, дыры сверки), пишет пакет и промпт ведущим, генерирует аудио… |
| [`/tg-connect`](tg-connect/SKILL.md) | ПОДКЛЮЧИТЬ Telegram на ЭТОЙ машине — оба стека сразу: Telethon-рельса (роботы, 0 LLM) и MCP (живые сессии). Триггеры «/tg-connect», «/tg-login», «подк… |
| [`/thread-clean`](thread-clean/SKILL.md) | Чистка спамных личных переписок перед повторным касанием: детерминированный план (какие НАШИ веерные рассылки и неотвеченные залпы стереть из диалога)… |
| [`/track-planes-and-ships`](track-planes-and-ships/SKILL.md) | - Track aircraft and vessels from public ADS-B and AIS broadcasts using ADS-B Exchange, Flightradar24, FlightAware,… Use when following a tail number … |
| [`/triage`](triage/SKILL.md) | - РАЗБОР ВХОДЯЩЕГО от живых людей: кто написал нам в Telegram (личка + упоминания в группах), WhatsApp и другие мессенджеры, сколько часов ждёт, кто о… |
| [`/tt-probe`](tt-probe/SKILL.md) | E2E-проба конвейера fleet-skill-autonomy (создан на [машина флота] 2026-07-16 для verify #41ac669a). Не вызывать - это тестовый маркер, после верифика… |
| [`/useosint`](useosint/SKILL.md) | - Entry point for open-source intelligence, investigation and verification work. Use when asked to investigate, research, verify, vet, check out, look… |
| [`/vibe-teach`](vibe-teach/SKILL.md) | Ежедневная обучающая серия «Claude Code / Codex для не-кодеров» — сгенерировать и опубликовать 1-3 поста дня (тизер + средний FB-пост) для аудитории «… |
| [`/voice-sessions`](voice-sessions/SKILL.md) | Нарезать голосовые Антона из чата «00 Архив ГОЛОСА» на ОТДЕЛЬНЫЕ ВИДИМЫЕ СЕССИИ: одна голосовая = одна сессия, всегда. Триггеры «/voice-sessions», «/v… |
| [`/what-an-email-reveals`](what-an-email-reveals/SKILL.md) | - Investigate an email address — MX and syntactic validation, Gravatar lookup, corporate email-format inference, breach exposure, and full mail-header… |
| [`/what-leaked-about-you`](what-leaked-about-you/SKILL.md) | - Check and interpret data-breach exposure for an email, username, phone or name using Have I Been Pwned, the Pwned Passwords k-anonymity range API, D… |
| [`/whatsapp-pair`](whatsapp-pair/SKILL.md) | Привязать (или ПЕРЕпривязать) WhatsApp к этой машине — единственный шаг, который нельзя сделать за Антона, потому что… Триггеры «/whatsapp-pair», «/wa… |
| [`/where-was-this-taken`](where-was-this-taken/SKILL.md) | - End-to-end workflow to establish where and when a photo or video was captured and whether it is authentic — evidentiary handling, metadata extractio… |
| [`/who-owns-this-domain`](who-owns-this-domain/SKILL.md) | - Establish who registered and who operates a domain using WHOIS, RDAP and DNS. Use when running a whois lookup, querying RDAP, digging A, AAAA, MX, N… |
| [`/who-really-owns-it`](who-really-owns-it/SKILL.md) | - Research companies, directors, shareholders and ultimate beneficial ownership in official corporate registries, filings and offshore datasets — Open… |
| [`/whose-number-is-this`](whose-number-is-this/SKILL.md) | - Investigate a phone number — E.164 normalisation with libphonenumber, phoneinfoga scanning, carrier and line-type identification, VoIP and burner de… |
| [`/windowless`](windowless/SKILL.md) | Убрать мелькающие ЧЁРНЫЕ КОНСОЛЬНЫЕ ОКНА (cmd/powershell/Windows Terminal) на любом Windows-узле флота: найти все три источника уликами, погасить обра… |
| [`/write-seo-geo-content`](write-seo-geo-content/SKILL.md) | Writes product-led content pages optimized for both search engines and AI engine citations. Produces markdown files with frontmatter, following page-t… |
| [`/write-the-intel-brief`](write-the-intel-brief/SKILL.md) | - Turn findings into a defensible intelligence product — BLUF key judgements, standardised estimative probability language, per-claim sourcing with ti… |
| [`/x-inbox-watch`](x-inbox-watch/SKILL.md) | - ВАХТА ИНБОКСА X (Twitter) — периодически проверяю DM (включая папку Requests), mentions и reply-тред Антона через его живой залогиненный Chrome, что… |
| [`/x-ray-a-company`](x-ray-a-company/SKILL.md) | - Corporate due-diligence workflow — resolve a brand or website to its registered legal entity, map group structure and beneficial ownership, profile … |
| [`/youtube-publish`](youtube-publish/SKILL.md) | Публикует готовый контент на личный YouTube-канал Антона [аккаунт]: вычерпывает новое из NotebookLM и очереди, рендерит аудио в видео, пишет описание … |
