export const meta = {
  name: 'wave-fit-and-answers',
  description: 'Отобрать волну вакансий по фиту Антона и написать точечные ответы (параметризуется args)',
  phases: [
    { title: 'Отбор', detail: 'судьи делят пул, каждый решает fit/skip и назначает CV-кластер' },
    { title: 'Ответы', detail: 'на прошедших — авторские ответы в файлы <prefix>_extra_*.json' },
  ],
}

const SP = '[путь владельца]'
const POOL = (args && args.pool) || 'batch_w6.json'
const PREFIX = (args && args.prefix) || 'w6'
const COUNT = (args && args.count) || 26
const TODAY = (args && args.today) || (() => { throw new Error('args.today обязателен (класс 07.09: протухшее «сегодня»)') })()

const CONTEXT = `
Ты работаешь на Антона Дзятковского (Anton Dziatkovskii). Сегодня ${TODAY}; с 03.09 подано ~100 заявок
и собираем следующую волну. Пул кандидатов: ${SP}\\\\${POOL} (записи: company/title/ats/url/cluster/location).

ФАКТЫ ОБ АНТОНЕ бери ТОЛЬКО отсюда — выдумывать запрещено жёстко:
- мастер-резюме: [путь владельца]
- канон-ответы (правда, проверено сегодня): база Palo Alto, California 94301; зарплата 180000 USD; 15 лет опыта;
  старт 10/01/2026 либо "Immediately available"; pronouns He/him; демография — Decline;
  немецкий C2 = НЕТ; живёт в NYC/London = НЕТ, но РЕЛОКАЦИЯ = ДА (готов переехать, включая NYC и SF);
  Bay Area = ДА; web3 с 2017 = ДА; сам код не пишет (уровень Python — начальный), но управляет
  продакшн-флотом агентов; вместо LinkedIn всегда https://tonydzi.github.io/
- ПРАВО НА РАБОТУ: активная O-1 в США (спонсорство не нужно) + польский паспорт = ЕС.
  Британии и Канады права на работу НЕТ, спонсорство мы не берём → такие роли идут в skip.
- накопленный опыт подач: [путь владельца]

Не знаешь честного ответа — роль в skip, а не выдуманный факт.
`

const FIT_SCHEMA = {
  type: 'object',
  properties: {
    verdicts: {
      type: 'array',
      items: {
        type: 'object',
        properties: {
          company: { type: 'string' },
          title: { type: 'string' },
          fit: { type: 'string', enum: ['strong', 'ok', 'weak', 'skip'] },
          cluster: { type: 'string', enum: ['fde', 'founder-bd', 'product', 'devrel', 'security', 'startup-ecosystem'] },
          why: { type: 'string' },
        },
        required: ['company', 'title', 'fit', 'cluster', 'why'],
      },
    },
  },
  required: ['verdicts'],
}

const WRITE_SCHEMA = {
  type: 'object',
  properties: {
    files: { type: 'array', items: { type: 'string' } },
    notes: { type: 'string' },
  },
  required: ['files'],
}

phase('Отбор')
const step = Math.ceil(COUNT / 3)
const SLICES = [[0, step], [step, step * 2], [step * 2, COUNT]]
const judged = await parallel(SLICES.map(([lo, hi]) => () =>
  agent(`${CONTEXT}

ЗАДАЧА: прочитай ${SP}\\\\${POOL} и разбери записи с индекса ${lo} по ${hi - 1} включительно.
По каждой вынеси вердикт фита:
- strong — профиль прямо ложится: forward-deployed / solutions / deployment strategist, партнёрства и BD,
  корпоративное развитие, продукт в крипте либо AI-инфре, founding GTM;
- ok — реалистичная растяжка (product marketing в девтулзах/крипте, growth-лид с BD-уклоном, solutions engineer);
- weak — далеко, но не абсурд;
- skip — не подаём: глубокая инженерия и безопасность как исполнитель, роли под язык, которым он не владеет,
  стажировки, клинические роли, И ЛЮБЫЕ роли, требующие права на работу в UK, Канаде или Сингапуре;
  ТАКЖЕ skip: роли инженера-исполнителя (Software/Infrastructure/Security Engineer, Researcher с кодом, «coding interview»),
  оборонные роли под TS/SCI, роли с обязательным немецким/французским; sales-роли ниже директора (BDR/SDR/AE) — skip.
cluster — под какой вариант CV подавать (fde / founder-bd / product / devrel / security / startup-ecosystem).
why — одна конкретная строка по-русски, с указанием локации и права на работу, если они решают.

Верни СТРОГО объект по схеме.`,
    { label: `fit:${lo}-${hi}`, phase: 'Отбор', schema: FIT_SCHEMA, effort: 'medium' })))

const all = judged.filter(Boolean).flatMap(r => r.verdicts || [])
const keep = all.filter(v => v.fit === 'strong' || v.fit === 'ok')
log(`отбор: ${all.length} судимо -> ${keep.length} берём (strong ${all.filter(v => v.fit === 'strong').length}, ok ${all.filter(v => v.fit === 'ok').length})`)
if (!keep.length) return { picked: [], all }

phase('Ответы')
const GROUPS = []
for (let i = 0; i < keep.length; i += 3) GROUPS.push(keep.slice(i, i + 3))

const written = await parallel(GROUPS.map((grp) => () =>
  agent(`${CONTEXT}

ЗАДАЧА: подготовь файлы точечных ответов для ролей:
${JSON.stringify(grp.map(g => ({ company: g.company, title: g.title, cluster: g.cluster })), null, 1)}

1. Возьми их url из ${SP}\\\\${POOL} и прочитай описание вакансии (WebFetch). Страница не отдалась — пиши
   по названию роли и компании, это нормально, но так и отметь в notes.
2. На каждую роль запиши файл ${SP}\\\\${PREFIX}_extra_<company-slug>.json.
   Формат: { "<устойчивый фрагмент вопроса как regex>": { "section": "...", "value": ... } }
   Секции: "text" (свободный ответ), "yesno" (true/false), "option" (СПИСОК кандидатов-вариантов
   по убыванию точности), "checkbox" (true).
   ⚠️ Ключ — короткий фрагмент формулировки, по нему идёт regex-поиск по label поля; не пиши весь вопрос.
   ⚠️ Для "option" перечисляй несколько формулировок: движок перебирает их по порядку и жмёт первую
   совпавшую опцию (совпадение по подстроке тоже работает).
3. Закрой типовые открытые вопросы этой роли: почему эта компания, релевантный опыт, как использует AI
   в работе, сильнейшее достижение, деньги (180000), старт (10/01/2026), готовность к локации (релокация = да).
4. Голос: первое лицо, короткие сильные фразы, никаких превосходных степеней, ноль выдуманных фактов.
   Опора на настоящее: продакшн-флот многоагентных Claude-агентов, 11 лет венчурного инкубатора в APAC,
   фонд и синдикат инвесторов, партнёрства с банками ЮВА по стейблкоинам (2018), MyWish и партнёрство
   с Binance, публичные OSS-вклады и опубликованные evals.

Верни {files: [абсолютные пути], notes: "что не открылось"}.`,
    { label: `answers:${grp.map(g => g.company).join('+').slice(0, 40)}`, phase: 'Ответы', schema: WRITE_SCHEMA, effort: 'medium' })))

const files = written.filter(Boolean).flatMap(w => w.files || [])
log(`файлов ответов: ${files.length}`)
return { picked: keep, skipped: all.filter(v => v.fit === 'weak' || v.fit === 'skip'), files }
