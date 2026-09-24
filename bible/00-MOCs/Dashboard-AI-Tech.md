---
title: "Dashboard — AI & Tech"
aliases: [AI-Dashboard, "AI Tech Dashboard"]
tags: [dashboard, ai, MOC]
date: 2026-05-30
type: moc
authored_by: claude-cowork
language: ru
value_score: 0.95
topic: 01-AI-Tech
parent: "MOC-index [internal]"
summary: "Дашборд AI/Tech: ChatGPT/Claude/Eliza эксперименты, AI-агенты, инфраструктура (n8n, MCP), будущее."
---

# 🤖 AI & Tech — Dashboard

> Главный фронт: AI-агенты, Eliza-fork, ChatGPT Deep Research, MCP/n8n автоматизация.
> 🛰 Альфа из комьюнити: _ClawRus-Alpha-MOC [internal] (OpenClaw/Claude Code RU, мониторинг через watcher).

---

## 🔥 Активные концепты

```dataview
TABLE WITHOUT ID
  file.link AS "Концепт",
  length(file.inlinks) AS "← refs"
FROM "06-Concepts"
WHERE contains(tags, "ai") OR contains(file.name, "AI") OR contains(file.name, "GPT") OR contains(file.name, "LLM") OR contains(file.name, "agent")
SORT length(file.inlinks) DESC
LIMIT 20
```

## 🧠 Топ-50 insights (vs ≥ 0.7)

```dataview
TABLE WITHOUT ID
  file.link AS "Инсайт",
  value_score AS "VS",
  summary AS "Идея"
FROM "03-Insights/AI-Tech"
WHERE !archive
SORT value_score DESC
LIMIT 50
```

## 🦙 Eliza [человек] (хронология экспериментов)

```dataview
TABLE WITHOUT ID
  file.link AS "Eliza#",
  date AS "Дата",
  summary AS "Что освоено"
FROM "01-Conversations/Facebook"
WHERE contains(file.name, "Eliza") OR contains(file.name, "eliza")
SORT date ASC
```

## 🛠 Tools & workflows

```dataview
TABLE WITHOUT ID
  file.link AS "Тул",
  value_score AS "VS",
  summary AS "Что"
FROM "01-Conversations" OR "03-Insights"
WHERE !archive AND value_score >= 0.65
  AND (contains(summary, "ChatGPT") OR contains(summary, "Claude") OR contains(summary, "n8n") OR contains(summary, "MCP") OR contains(summary, "NotebookLM") OR contains(summary, "Deep Research") OR contains(summary, "промпт"))
SORT value_score DESC
LIMIT 30
```

## 🔮 Будущее AI / прогнозы / нарративы

```dataview
TABLE WITHOUT ID
  file.link AS "Нота",
  value_score AS "VS",
  summary AS "Прогноз"
FROM "01-Conversations" OR "03-Insights"
WHERE !archive AND value_score >= 0.7
  AND (contains(summary, "AGI") OR contains(summary, "стена Мура") OR contains(summary, "AI-risk") OR contains(summary, "AI-CEO") OR contains(summary, "scaling"))
SORT value_score DESC
LIMIT 25
```

## 🔄 Open loops (review_after)

```dataview
LIST
FROM "02-Decisions" OR "03-Insights"
WHERE topic = "01-AI-Tech" AND review_after AND date(review_after) <= date(today) + dur(45 days)
SORT review_after ASC
```

## ⚓ Якорные концепты

- [[concept-autonomous-ai-agents]] / [[AGI]]
- Eliza [internal] / [человек] OS [internal]
- ChatGPT / Claude [internal] / Deep Research [internal]
- [[n8n]] / Questflow [internal]
- [[Fetch.ai]] / [[SingularityNET]]
- NotebookLM [internal]
- [[Digital-Immortality]]
- AGENTS.md [internal]

## 🔗 См. также

- [[MOC-AI-Agents]]
- Dashboard-Crypto-Web3 [internal] (AI×Crypto)
- _high-value-report-[id] [internal]

---

*Auto-built: 2026-05-30.*
