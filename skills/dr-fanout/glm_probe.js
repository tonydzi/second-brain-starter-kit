/* dr-fanout / glm_probe.js — READ-ONLY probe композера GLM (chat.z.ai) ПЕРЕД Send.
 *
 * Назначение: доказать ДО траты квоты, что заказ уйдёт в правильном режиме —
 *   (а) Advanced Search ON  (б) Deep Think = Max  (в) композер найден.
 *   Корень: приказ Антона 31.08.2026 «не забывай включать Deep Think на Max» —
 *   синий атом «Deep think enabled» НЕ значит Max, уровень задаётся отдельной
 *   выпадашкой. Брак молчит: файл в results/ появится, разведки в нём не будет
 *   (тот же класс, что Advanced Search OFF и Grok в Expert вместо Heavy).
 *
 * Вход:  window.__glmProbe()  — через Claude-in-Chrome javascript_tool. Ничего не кликает,
 *        ничего не пишет в страницу: probe НИКОГДА не меняет состояние (иначе он же и сломает ран).
 * Выход: компактный объект-СЫРЬЁ + строки evidence (что именно прочитано со страницы).
 *        ⛔ Поле ok здесь СПРАВОЧНОЕ. Судья — `glm_probe.py verdict '<json>'` (0 LLM, exit-код),
 *        чтобы «прибор сказал ок» нельзя было принять на слово ([[prichina-kak-claim]]).
 * Кто дёргает: скилл /dr-fanout, СОСТОЯНИЕ 2 — PROBE, шаг 1 (перед Send на рельсе glm).
 * Рельса: подписка Z.ai в живом Chrome (вход = [рабочий аккаунт]@gmail.com). Вендорских
 *        токенов не тратит вообще: это чтение DOM.
 * Тесты: _test_glm_probe.js (node, DOM-заглушка + мутанты) · _test_glm_probe.py (судья + мутанты).
 * updated: 2026-09-06 — UI сентября: глобус САМ есть тумблер Advanced Search (data-active),
 *        подменю вендор свернул; читаем тумблер ПЕРВЫМ, текст/меню — запасным путём.
 *
 * ⚠️ ЧЕСТНАЯ ГРАНИЦА (две эпохи UI, обе поддержаны):
 *    · UI до 09.2026 — `Advanced Search` был пунктом МЕНЮ ПОД ГЛОБУСОМ и при закрытом меню
 *      не читался: probe возвращал advSearch.found=false, судья валил прогон (fail-closed),
 *      лечилось «открой меню и прогони probe снова». «Не прочитал» ≠ «включено».
 *    · UI с 09.2026 — меню свёрнуто, состояние живёт в data-active у кнопки-глобуса в
 *      composer-form; надпись «Advanced Search» осталась только тултипом по наведению.
 *      Тултип НЕ орган управления и не должен перебивать data-active (замер 06.09).
 */
window.__glmProbe = function () {
  const out = {
    v: 1,
    url: String(location.href),
    composer: { found: false, sel: '', isPM: null, len: null },
    deepThink: { found: false, enabled: null, level: null, evidence: '' },
    advSearch: { found: false, on: null, evidence: '' },
    model: { found: false, name: null, evidence: '' },
    ok: false,
    reason: '',
  };

  // ⚠️ СОДЕРЖИМОЕ ДИАЛОГА -- НЕ СОСТОЯНИЕ КОМПОЗЕРА (замер 04.09.2026, chat.z.ai).
  // Вендор показал промо-всплывашку «New GLM-5.3-Flash», и probe прочитал имя модели
  // ИЗ НЕЁ: вернул model.name='GLM-5.3-Flash', хотя это анонс, а не выбранная модель.
  // Стоило погасить всплывашку -- модель не читалась вовсе. То есть прибор докладывал
  // рекламу вендора как факт о нашем прогоне. Диалоги исключаем из ВСЕХ чтений сразу:
  // тот же обман возможен и для Deep Think, и для Advanced Search.
  const inDialog = (el) => !!(el && el.closest && el.closest('[role="dialog"],dialog,.modal'));
  const vis = (el) => !!(el && el.offsetParent !== null && el.getClientRects().length && !inDialog(el));
  const txt = (el) => (el && (el.innerText || el.textContent) || '').replace(/\s+/g, ' ').trim();
  const cut = (s, n) => (s || '').slice(0, n || 120);

  // ---------- 1) КОМПОЗЕР (замер 04.08: обычный <textarea> внутри form, НЕ ProseMirror) ----------
  for (const s of ['form textarea', 'textarea', 'div[contenteditable="true"]']) {
    const cand = Array.from(document.querySelectorAll(s)).filter(vis);
    if (cand.length) {
      const el = cand[cand.length - 1];
      out.composer = {
        found: true,
        sel: s,
        isPM: !!(el.className && String(el.className).match(/ProseMirror|tiptap/i)),
        len: (el.value !== undefined && el.value !== null ? el.value : txt(el)).length,
      };
      break;
    }
  }

  // ---------- 2) DEEP THINK: включён? и на каком УРОВНЕ? ----------
  // Ищем без хрупкого селектора: сперва aria-label (замер 04.08: "Deep think enabled"),
  // затем текстовый скан — берём САМЫЙ МЕЛКИЙ элемент со словами "deep think",
  // чтобы не утащить полстраницы и не прочитать уровень из соседнего блока.
  const RE_DT = /deep\s*think/i;
  let dtEl = null;
  const aria = Array.from(document.querySelectorAll('[aria-label]')).filter(
    (el) => RE_DT.test(el.getAttribute('aria-label') || '')
  );
  const ariaVis = aria.filter(vis);
  if (ariaVis.length) dtEl = ariaVis[0];
  if (!dtEl) {
    const all = Array.from(document.querySelectorAll('button,[role="button"],[role="combobox"],span,div,label'))
      .filter(vis)
      .filter((el) => RE_DT.test(txt(el)))
      .sort((a, b) => txt(a).length - txt(b).length);
    if (all.length) dtEl = all[0];
  }

  if (dtEl) {
    const al = dtEl.getAttribute('aria-label') || '';
    // Контейнер: сам элемент + подпись рядом (выпадашка уровня — СОСЕДНИЙ узел, не внутри кнопки).
    const holder = dtEl.parentElement || dtEl;
    const blob = [al, txt(dtEl), txt(holder)].join(' | ');
    out.deepThink.found = true;
    out.deepThink.evidence = cut(blob, 200);

    if (/\bdisabled\b|\boff\b/i.test(al)) out.deepThink.enabled = false;
    else if (/\benabled\b|\bon\b/i.test(al)) out.deepThink.enabled = true;
    else if (dtEl.getAttribute('aria-pressed') !== null) out.deepThink.enabled = dtEl.getAttribute('aria-pressed') === 'true';
    else if (dtEl.getAttribute('aria-checked') !== null) out.deepThink.enabled = dtEl.getAttribute('aria-checked') === 'true';

    // Уровень: (а) явный select/combobox рядом; (б) хвост текста ПОСЛЕ слов "Deep Think".
    const near = Array.from(holder.querySelectorAll('select,[role="combobox"],[role="listbox"],button')).filter(vis);
    for (const n of near) {
      const t = (n.tagName === 'SELECT' && n.selectedOptions && n.selectedOptions[0])
        ? txt(n.selectedOptions[0]) : txt(n);
      if (t && !RE_DT.test(t) && t.length <= 24) { out.deepThink.level = t; break; }
    }
    if (!out.deepThink.level) {
      const m = txt(holder).match(/deep\s*think[\s:·|-]*([A-Za-z0-9+\-]{1,16})/i);
      if (m && m[1]) out.deepThink.level = m[1];
    }
  }

  // ---------- 3-А) UI СЕНТЯБРЯ 2026: ГЛОБУС САМ ЕСТЬ ТУМБЛЕР ADVANCED SEARCH ----------
  // Замер 06.09.2026 на живом chat.z.ai (Firefox AutoFF, [машина флота], сессия
  // AUTO-[машина флота]-dr-quorum-topup): вендор СВЕРНУЛ подменю «Search / Advanced Search».
  // Осталась одна кнопка-глобус в композере, состояние = атрибут data-active:
  //   до клика  data-active="false"  ->  после клика  data-active="true"
  // Надпись «Advanced Search» живёт ТОЛЬКО в тултипе по наведению: охота по всему DOM
  // даёт хит после hover и ноль после клика — поэтому пункт меню (блок 3) не находится
  // НИКОГДА, и судья fail-closed запрещал Send навсегда при исправном UI.
  // ⛔ Порядок важен и он ОБРАТЕН прежнему (перевёрнут 06.09 после живого прогона
  //    DR26-08-30-HUB-02-1937): ПЕРВЫМ читаем прямое состояние органа управления, и лишь
  //    затем текстовую эвристику. Причина: если курсор остался над глобусом, в DOM висит
  //    тултип «Advanced Search Multi-round search…», текстовый путь цепляется за него и
  //    возвращает on=false ПОВЕРХ data-active="true" -> судья fail-closed валит исправный
  //    прогон. Тултип — подсказка, а не орган: причинно проверено, что клик флипает
  //    именно data-active.
  // Fail-closed сохранён: кандидат обязан быть РОВНО ОДИН, иначе ничего не читаем.
  if (!out.advSearch.found) {
    try {
      const skip = { 'upload-file-button': 1, 'send-message-button': 1 };
      const cand = Array.from(document.querySelectorAll('form button[data-active], form [role="button"][data-active]'))
        .filter(vis)
        .filter((el) => !skip[el.id || '']);
      if (cand.length === 1) {
        const g = cand[0];
        const st = String(g.getAttribute('data-active') || '').toLowerCase();
        if (st === 'true' || st === 'false') {
          out.advSearch.found = true;
          out.advSearch.on = st === 'true';
          out.advSearch.evidence = cut('globe-toggle data-active=' + st + ' | ' + cut(String(g.className), 90), 200);
        }
      } else if (cand.length > 1) {
        out.advSearch.evidence = cut('тумблер не опознан: кандидатов ' + cand.length + ' (нужен ровно 1)', 120);
      }
    } catch (e) { out.advSearch.evidence = 'toggle-error:' + cut(String(e && e.message), 40); }
  }

  // ⛔ ВТОРИЧНО: включается, только если прямой тумблер (блок 3-А) состояние НЕ прочитал.
  //    Причина — замер 06.09: тултип «Advanced Search…» под курсором не орган управления,
  //    но текстовая эвристика цепляется за него и врёт on=false поверх data-active="true".
  if (out.advSearch.on === null) {
    // ---------- 3) ADVANCED SEARCH (тумблер в меню под глобусом; при закрытом меню НЕ читается) ----------
    const advCand = Array.from(document.querySelectorAll('button,[role="button"],[role="menuitem"],[role="switch"],[aria-label],li,div,span'))
      .filter(vis)
      .filter((el) => /advanced\s*search/i.test(txt(el) + ' ' + (el.getAttribute('aria-label') || '')))
      .sort((a, b) => txt(a).length - txt(b).length);
    if (advCand.length) {
      const el = advCand[0];
      const holder = el.parentElement || el;
      out.advSearch.found = true;
      out.advSearch.evidence = cut([el.getAttribute('aria-label') || '', txt(el), txt(holder)].join(' | '), 200);
      const sw = el.matches('[role="switch"],[aria-checked],[aria-pressed],[data-state]')
        ? el
        : (holder.querySelector('[role="switch"],[aria-checked],[aria-pressed],[data-state]') || null);
      if (sw) {
        const st = sw.getAttribute('aria-checked') || sw.getAttribute('aria-pressed') || sw.getAttribute('data-state') || '';
        if (/true|checked|on\b/i.test(st)) out.advSearch.on = true;
        else if (/false|unchecked|off\b/i.test(st)) out.advSearch.on = false;
      }
    }

  }

  // 3-бис) УЛИКА ПРИ ЗАКРЫТОМ МЕНЮ: глобус подсвечивается акцентным синим, когда режим поиска включён
  //   (видно на скриншоте Антона 31.08). ⚠️ Это СПРАВОЧНАЯ улика, а не доказательство: цвет читается
  //   вслепую по computed style и вендор может перекрасить UI. Судья её НЕ принимает — только человек
  //   как подсказку «меню открывать или нет» ([[prichina-kak-claim]]: индикатор — тоже claim).
  try {
    const globe = Array.from(document.querySelectorAll('button,[role="button"]')).filter(vis).find((el) => {
      const a = (el.getAttribute('aria-label') || '') + ' ' + (el.getAttribute('title') || '');
      return /search|web|globe/i.test(a) || !!el.querySelector('svg.lucide-globe,svg[class*="globe" i]');
    });
    if (globe) {
      const cs = getComputedStyle(globe.querySelector('svg') || globe);
      const c = cs.color || '';
      const m = c.match(/(\d+)\D+(\d+)\D+(\d+)/);
      let hint = 'unread';
      if (m) {
        const [r, g, b] = [Number(m[1]), Number(m[2]), Number(m[3])];
        hint = (b > r + 40 && b > 120) ? 'accent-colored(похоже ON)' : 'plain(похоже OFF)';
      }
      out.advSearch.globeHint = hint + ' ' + cut(c, 32);
    }
  } catch (e) { out.advSearch.globeHint = 'error:' + cut(String(e && e.message), 40); }

  // ---------- 4) МОДЕЛЬ (правило «всегда самая умная»: ждём GLM-5.2) ----------
  const mm = Array.from(document.querySelectorAll('button,[role="button"],[role="combobox"],span'))
    .filter(vis)
    .map((el) => txt(el))
    .find((t) => /^GLM-[\w.\-]+/i.test(t) && t.length <= 32);
  if (mm) { out.model.found = true; out.model.name = mm.match(/GLM-[\w.\-]+/i)[0]; out.model.evidence = cut(mm, 60); }

  // Справочный вердикт (судит всё равно glm_probe.py — fail-closed на любом «не прочитал»).
  const dtMax = !!(out.deepThink.level && /^max$/i.test(String(out.deepThink.level).trim()));
  out.ok = !!(out.composer.found && dtMax && out.advSearch.on === true);
  out.reason = out.ok ? 'ok'
    : !out.composer.found ? 'composer-not-found'
    : !out.deepThink.found ? 'deepthink-control-not-found'
    : !dtMax ? ('deepthink-level-not-max:' + (out.deepThink.level || 'unread'))
    : out.advSearch.found ? 'advsearch-off-or-unread'
    : 'advsearch-not-visible(открой меню глобуса и прогони probe снова)';
  return out;
};
