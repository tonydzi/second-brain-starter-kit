# Канон ответов для форм (из apply-playbook, вердикты Антона 01.09)

- Name: Anton Dziatkovskii (First: Anton, Last: Dziatkovskii)
- Email: dzyatkovskiy.a@gmail.com (a@platinum.fund НЕ использовать)
- Phone: +1 341 222 9178 · Country для телефона: United States
- Location: US-роль → Palo Alto, CA; EU-роль → Lisbon, Portugal
- Website: https://tonydzi.github.io/ · GitHub: https://github.com/tonydzi
- X/Twitter: https://x.com/Tony_Stef_ · Scholar: https://scholar.google.com/citations?user=b8gKHiMAAAAJ
- LinkedIn ТЕКСТОВОЕ поле (лейбл без валидации, часто с подсказкой «N/A если нет»): "No LinkedIn account - please see https://tonydzi.github.io/ and https://github.com/tonydzi"
- LinkedIn URL-ВАЛИДИРУЕМОЕ поле: РОВНО `https://tonydzi.github.io/` — чистая ссылка, БЕЗ приписок и скобок.
  ⚠️ Боевой замер 03-04.09: любая приписка («(no LinkedIn account)») валит строгий валидатор — Ashby отбивает сабмит с «Please enter a valid URL» (AIUC, Spade, Avoca). Пояснение про отсутствие LinkedIn кладём в свободную textarea формы, если она есть; если её нет — молча оставляем чистый URL.
  Как отличить: поле с `type=url`, лейблом «LinkedIn URL/Profile» или отбившее сабмит на валидации → URL-вариант; всё остальное → текстовый.
- Зарплата ТЕКСТОВОЕ поле: "Open / market rate"
- Зарплата ЧИСЛОВОЕ поле (вердикт Антона 03.09 «180-200-400 по позиции, решай сам» → лестница): senior IC / senior PM / senior engineer → 180000; staff / principal / lead / EM / Head-of → 200000; VP / C-level / Head в top-tier AI-компании → 400000. Валюта поля = та же цифра (USD/CAD/EUR annual). Месячная gross → годовую/12 (180k→15000, 200k→16700). Другие цифры не выдумывать.
- ДАТЫ ОКОНЧАНИЯ РОЛИ — два РАЗНЫХ правила, не путать (ломатель 04.09 нашёл три расходящихся трактовки в слоях скилла):
  1. Общий вопрос «когда закончилась твоя последняя full-time роль / когда ты последний раз работал» → **2026-09-01** (вердикт Антона 03.09, его слова «например, 1 сентября»; согласуется с "Available immediately").
  2. Вопрос про КОНКРЕТНУЮ прошлую компанию из CV («end date at Everex») → **честная дата из CV**, Everex → 2018-12-31. Текущие роли (Palo Alto AI Research Lab, Platinum) — ongoing, дату окончания не ставим вовсе.
  Правило разрешения спора: если в вопросе назван работодатель — это случай 2; если вопрос обезличенный — случай 1. Цифры вне этих двух не выдумывать.
- Work auth US: authorized (O-1 active), спонсорство = No ВЕЗДЕ (и сейчас, и в будущем)
- Work auth EU: Yes, EU citizen (Poland), no visa needed. UK = No. Канада/Австралия = No, но "eligible for an expedited talent visa"
- Export-control (xAI): "Eligible to obtain the required authorizations from the U.S. Department of State"
- Арбитраж (OpenAI/Anthropic/Greenhouse): соглашаемся (единственная опция — брать её)
- Старт: "Available immediately"; календарное поле → 2026-09-15
- Relocation: Yes. Remote: Yes. Офис ≥25%/3дня: Yes
- EEO/демография: везде Decline to self-identify / I don't wish to answer
- Education: BSc + MSc MEPhI (в справочниках школ MEPhI нет → "Other - School Not Listed"); Degree поле — Engineer's Degree (вопрос Q2 к Антону открыт); PhD Paris College of International Education
- How did you hear: "Company careers page" (HN-строки: "Hacker News")
- Опыт вне домена: честно 0/No + текстом перенести смежный опыт
- Интервью в Anthropic раньше: No
- CV-кластеры (PDF в sent-2026-09-01/): FDE · Security · BD-Partnerships · Product · DevRel · Startup-Ecosystem · Writer

## Жёсткие стопы
CAPTCHA / verification code / создание аккаунта / пароль → blocked-* и дальше. Незнакомый вопрос без безопасного дефолта → blocked-question + текст вопроса в отчёт. Факты НЕ выдумывать.

## Вендор-капы на 02.09 (вечер)
Mistral 3/3 ⛔ · Cohere 5/5 ⛔ · OpenAI 4/5 (последний слот — только вердиктом Антона) · Anthropic ⛔ code-gate · Synthesia 3/30д ⛔ · Reflection 4 за 2 дня ⛔ (Q7) · Runway 4 за 2 дня ⛔ · xAI 3 за 2 дня — пауза сегодня · dropbox ⛔ (дубль-класс) · JetBrains 1 сегодня — можно ещё 1 · ≤2/компанию/день, UK-only роли — skip (Q4)

## Канонизировано 02.09 вечер (решения кофаундера, Антон в курсе по отчёту)
- Current Company: "Palo Alto AI Research Lab (Founder); Platinum VC & Incubator (Co-Founder)"
- Локация для дуальной EU+US роли: "Lisbon, Portugal (EU citizen; regularly in Palo Alto, CA on active US O-1)"
- "How did you hear" без опции careers page → "Website"
- AI-transcription consent на интервью (voluntary) → Yes
- US Government/clearance: честно No / no clearance (не гражданин, O-1)
- Lever-формы: plain HTML, поля по name (name, email, phone, org, urls[...], resume file input, comments textarea) — заполнять селениумом напрямую, комбо-граблей нет

## Work-auth за пределами США — честно по СТРАНЕ РОЛИ (замер 04.09, волна 25)
Канон «спонсорство = No ВЕЗДЕ» относится к США (у Антона активная O-1). Если роль в ДРУГОЙ стране, где у него нет разрешения на работу (Сингапур, Канада, Австралия, Япония), ответ «мне не нужно спонсорство» = ложное заявление о квалификации.
Правильно: «Are you legally authorised to work in <страна>?» → честное **No**; «Will you require sponsorship in <страна>?» → честное **Yes**; в свободном поле добавить «open to relocation» (+ для Канады/Австралии: «eligible for an expedited talent visa»).
ЕС — исключение: Антон гражданин Польши, в ЕС авторизован без спонсорства (Португалия, Франция, Германия, Ирландия, Нидерланды).
⚠️ ОТКРЫТЫЙ ВОПРОС К АНТОНУ (агенты волны 25 подняли дважды — Baseten, Valon): формулировки «**unrestricted** work authorization in the US» и «authorized to work for **ANY** employer in the US» строго читаются шире, чем O-1 (виза привязана к работодателю). Сейчас отвечаем Yes по канону. Нужен вердикт: оставляем Yes или переходим на «Yes, with employer sponsorship transfer required» там, где стоит слово unrestricted/any.

## Проверка формы «зелёная» ≠ форма готова к отправке (замер 04.09, волна 27)
Ashby-автозаполнение из резюме доезжает ПОЗЖЕ заявленных 20-25 секунд и стирает состояние уже заполненных полей. LangChain: проверка показала Name/Email/GitHub заполненными, потом автофилл переписал форму, и сервер отбил ровно эти три поля.
Правило: снимок проверки, сделанный ПОСЛЕ заполнения, доказательством НЕ является — доказательство только снимок непосредственно ПЕРЕД кликом Submit.
⚠️ Парная грабля (Anyscale): лечение «перезаполнить всё перед сабмитом» ломает радиогруппы — повторный клик по уже выбранной опции Ashby СНИМАЕТ выбор, и корректно заполненная форма тихо портится. Работает только пара: перед сабмитом перечитать состояние и до-заполнить ТОЛЬКО реально пустое, никогда не перекликивать выбранное.
⚠️ Поле резюме зовётся по-разному: «Resume», «CV/Resume» (Attio). Проверка приложенного файла по лейблу, начинающемуся на «Resume», пропустила бы заявку без CV — искать по /resume|cv/ с исключением /cover|autofill/.

## Вердикты Антона 07.09 (голосом, сессия волн 28+) — закрывают четыре класса форм
- **ZIP / почтовый индекс (US)** → `94301` (Palo Alto, CA). Обязательное поле адреса больше не blocked-question:
  street address по-прежнему не выдумываем, но город+штат+ZIP = «Palo Alto, CA 94301».
- **Kraken: «пользовался ли продуктом за 6 месяцев»** → **Yes** («пользуюсь постоянно»).
- **Paris College of International Education (PhD)** → **2019–2022**.
- **МИФИ (BSc+MSc)** → даты Антон НЕ назвал («очень давно») — поле дат МИФИ остаётся blocked-question,
  если обязательно; необязательное — пропускаем.
- **«Unrestricted work authorization in the US» / «authorized for ANY employer» при O-1** → **просто Yes**,
  без приписок про sponsorship transfer. Обоснование Антона: он сам себе работодатель (своя компания).
  Открытый вопрос выше (раздел «Work-auth за пределами США», абзац ⚠️) ЗАКРЫТ этим вердиктом.
