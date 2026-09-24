---
name: local-repo-intel
description: >
  РАЗВЕДКА ЧУЖОГО GITHUB-РЕПО + «что говорят в народе» — один проход: сам проект
  (метаданные, README, пульс issues/PR, кто контрибьюторы) + внешняя молва
  (Reddit/HN/dev.to/обзоры/YouTube) + security-досье (CVE, Socket.dev, npm-инциденты)
  + ToS/ban-риски + вердикт «берём / берём с заборами / не трогаем» под НАШ юзкейс.
  Триггеры: "/repo-intel <url>", "/local-repo-intel", "изучи этот гитхаб", "что о нём
  говорят", "разведка репо", "стоит ли брать этот тул", "repo intel", "study this repo".
  Родился 2026-07-31 из разведки OmniRoute (DR26-07-31-MACANTON-03-2122).
  НЕ путать с /issue-match (замер репо под НАШ PR) и /borrowed-audience (куда класть НАШИ репо).
---

# /local-repo-intel — разведка чужого репо и молвы о нём

Вход: URL репо + (важно!) НАШ юзкейс — зачем мы его рассматриваем. Вердикт всегда
относительно юзкейса, не «хороший ли проект вообще».

## Шаг 0 — RECALL
Память + волт + реестр ДР: не изучали ли уже? (`grep` по волту, `dr_registry.py list`).

## Шаг 1 — Сам проект (0 токенов, gh api)
```bash
gh api repos/<owner>/<repo> --jq '{full_name,description,stars:.stargazers_count,forks:.forks_count,open_issues:.open_issues_count,created:.created_at,pushed:.pushed_at,language,license:.license.spdx_id,archived,topics}'
gh api 'repos/<owner>/<repo>/issues?state=all&per_page=50' --jq '.[] | {n:.number,t:.title,state,comments,user:.user.login,created:.created_at}'
```
Смотрю: возраст vs звёзды (звёзды за месяцы = хайп-волна, проверить накрутку),
пульс (свежие коммиты/issues), тон багов ([BUG] про core = красный),
кто пишет issues (живые юзеры vs сам мейнтейнер себе), bus-factor.

## Шаг 2 — README глазами скептика (WebFetch)
Что обещает, как ставится, какие цифры заявляет. Каждую громкую цифру пометить
«проверить в народе» — маркетинг ≠ замер ([[prichina-kak-claim]]).

## Шаг 3 — Народ (WebSearch, 3-4 запроса)
- `<name> reddit OR "hacker news" review experience`
- `<name> security CVE OR vulnerability OR malware`
- `<name> ToS OR ban OR "terms of service"` (для тулов-прокси/обходов — обязательный)
- `<name> vs <главный конкурент>`
Искать ЗАМЕРЫ, не пересказы README: посты «я потестил, вот цифры» > обзоры-рерайты.
Лучшие 1-2 источника дочитать WebFetch'ем целиком.

## Шаг 4 — Security-досье
CVE по имени; Socket.dev/npm advisories; инциденты supply-chain; как мейнтейнер
РЕАГИРОВАЛ на репорты (реакция важнее самого факта дыры).

## Шаг 5 — ToS/ban-риск (если тул трогает чужие аккаунты/квоты)
Чьи аккаунты поедут через тул? Что говорят ToS этих провайдеров про прокси/harness?
Есть ли у тула evasion-фичи (TLS-fingerprint stealth, MITM) — их наличие = провайдеры
уже банят такой класс. Наш аккаунт-капитал (Anthropic!) не рискуем никогда.

## Шаг 6 — Вердикт + маршрут
Формат: ✅ берём / ⚠️ берём с заборами (какими именно) / ⛔ не трогаем — ПОД ЮЗКЕЙС,
+ таблица альтернатив, + уверенность по каждому claim (established/emerging/speculative).
Глубокая ставка (деньги/инфра/необратимое) → дополнительно ДР наружу через
`dr_start.py` (реестр+веер). Находки → в волт ([[always-archive-artifacts-to-vault]]).

## Грабли
- Звёзды покупаются и нагоняются листингами — сверять с graph контрибьюторов и тоном issues.
- «N контрибьюторов» в описании репо часто = drive-by typo-фиксы.
- Обзоры в блогах на 80% рерайт README — искать автора с собственным замером.
- Web search молчит про свежие скандалы <2 недель — дочитать issues репо и X.
