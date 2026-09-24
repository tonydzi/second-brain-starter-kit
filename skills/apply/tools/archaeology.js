export const meta = {
  name: 'apply-archaeology',
  description: 'Волна 20 умерла с процессом: восстановить из транскриптов агентов, что реально подано',
  phases: [{ title: 'Dig', detail: '4 археолога, по транскрипту на каждого' }],
}

const A0 = (typeof args === 'object' && args) ? args : {}
if (!A0.run) throw new Error('args.run обязателен: путь к папке прогона (…/subagents/workflows/wf_XXXX) умершей волны')
const WF = String(A0.run).replace(/\/$/, '')
const SCRATCH = String(A0.dir || '').replace(/\/$/, '')
if (!SCRATCH) throw new Error('args.dir обязателен: папка волны, где лежат [машина флота]_wave<N>.json и скрины')

const SCHEMA = {
  type: 'object', required: ['results'],
  properties: {
    agent_file: { type: 'string' },
    indices_claimed: { type: 'string' },
    results: { type: 'array', items: {
      type: 'object', required: ['company', 'outcome', 'evidence'],
      properties: {
        idx: { type: 'integer' }, company: { type: 'string' }, url: { type: 'string' },
        outcome: { type: 'string', enum: ['applied', 'code-gate', 'closed', 'blocked-captcha', 'blocked-question', 'error', 'no-fit', 'email-needed', 'unfinished'] },
        evidence: { type: 'string' },
      } } },
  },
}

const COMMON = `Ты — АРХЕОЛОГ прерванной волны подач. Процесс Claude умер 03.09 в 10:14 PDT посреди работы: четыре агента подавали заявки Антона Дзятковского на вакансии, ни один не успел вернуть структурированный результат. Их транскрипты уцелели. Твоя задача — восстановить ПРАВДУ по одному транскрипту.

⛔ ТЫ НИЧЕГО НЕ ПОДАЁШЬ И НЕ ОТКРЫВАЕШЬ БРАУЗЕР. Только чтение файлов. Любая повторная подача = дубль заявки, это запрещено.

ТВОЙ ФАЙЛ (читай ТОЛЬКО его): ${WF}/<файл ниже>
Спека волны (что кому назначалось): ${SCRATCH}/[машина флота]_wave20.json — там массив, индекс = позиция в массиве, поля company/title/cluster/links.

Файл огромный (250-730 КБ) — НЕ читай его целиком Read-ом. Работай grep/python: например
  python3 -c "import re;t=open('<файл>',errors='ignore').read();print(len(t))"
и дальше выборки регулярками. Полезные маркеры:
- "мой индекс=N, company=..., открыл title=..." — агент объявлял каждую вакансию перед работой;
- "Success", "successfully submitted", "Thank you for applying", "application received" — экраны успеха ПОСЛЕ сабмита (не путать с текстом ДЕТЕКТОРА в промпте и с кодом gh_lib.py, где эти фразы встречаются как строковые литералы в if-ах — это НЕ доказательство подачи);
- "Verify you are human" / Turnstile / hCaptcha — капча (blocked-captcha);
- "verification code" / "8-character" на СТРАНИЦЕ после сабмита — code-gate;
- "no longer accepting", "Job not found", 404 — closed;
- последние записи "thinking" агента — там он подводит итог своими словами;
- имена скринов w20_i<idx>_<comp>_after.png — проверь их существование через ls ${SCRATCH}/w20_*.png (наличие скрина само по себе НЕ доказывает успех, но помогает привязать индекс к компании).

ПРАВИЛА ВЕРДИКТА (строго, без натяжек):
- applied — ТОЛЬКО если в транскрипте виден текст страницы ПОСЛЕ сабмита с явной фразой успеха. Цитируй эту фразу в evidence.
- code-gate / blocked-captcha / closed / blocked-question / no-fit / email-needed — по маркерам выше, с цитатой.
- error — агент явно упёрся в ошибку и сдался.
- unfinished — агент до этого индекса НЕ дошёл (процесс умер раньше) ИЛИ начал, но нет ни успеха, ни явного стопа. Это ЧАСТЫЙ и НОРМАЛЬНЫЙ исход, не выдумывай успех.
⚠️ Сомневаешься между applied и unfinished → ставь unfinished. Ложный applied хуже пропущенного: он навсегда закроет вакансию в реестре, и Антон туда не подастся.

ВЕРНИ по одной записи на КАЖДЫЙ свой индекс из назначенной группы (даже если исход unfinished), плюс agent_file и indices_claimed (какие индексы агент реально объявлял в транскрипте). Строго JSON по схеме, ничего кроме StructuredOutput.`

const FILES = A0.files || []   // имена agent-*.jsonl; пусто → возьмём все из папки прогона
const GROUPS = (FILES.length ? FILES : ['*']).map((f, i) => ({
  label: `dig-${i + 1}`, file: f,
  idx: A0.groups && A0.groups[i] ? A0.groups[i] : 'определи по транскрипту (объявления «мой индекс=»)',
}))

phase('Dig')
const results = await parallel(GROUPS.map(g => () =>
  agent(`${COMMON}\n\nТВОЙ ФАЙЛ: ${g.file}\nТВОЯ ГРУППА: ${g.idx}`,
    { label: g.label, phase: 'Dig', schema: SCHEMA })
))
const flat = []
for (const r of results) if (r && Array.isArray(r.results)) flat.push(...r.results.map(x => ({ ...x, agent: r.agent_file })))
const applied = flat.filter(x => x.outcome === 'applied')
log(`Археология волны 20: ${applied.length} applied, ${flat.length} записей всего`)
return { results: flat }
