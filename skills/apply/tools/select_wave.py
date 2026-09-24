"""Отбор волны вакансий для Трубы А: берёт свободные роли из jobs.db под фильтры и капы.

Назначение: собрать N ролей одного ATS, которые НИКТО (ни эта машина, ни другие узлы флота)
ещё не занял, и записать их в `<wave-dir>/[машина флота]_wave<N>.json` — вход для воркфлоу-волны.

Вход:  --wave <N> --ats ashby|lever|greenhouse|workable --target <сколько ролей>
       env APPLY_WAVE_DIR (где лежат файлы волн и результатов; дефолт — текущая папка)
       env JOBS_DB (дефолт $IMPORTS_ROOT/jobs-watch/jobs.db, затем ~/Obsidian/_imports/...)
       ~/.claude/skills/apply/rowmap.json — межмашинный замок (СНАЧАЛА `mark_row.py build-cache`)
Выход: [машина флота]_wave<N>.json + человекочитаемая таблица в stdout. Код возврата 0 / 2 (нет ролей) / 3 (нет замка).
Кто дёргает: скилл /apply, шаг «отбор волны»; вручную перед каждой волной.
Рельса: детерминированный python, 0 LLM, 0 сети (читает локальную БД + локальный кэш реестра).
Тест: tools/_test_select_wave.py.

⚠️ ТРИ КОРНЯ, ОПЛАЧЕННЫЕ КРОВЬЮ 03-04.09.2026 — не откатывать:
1. Компанейский кап считается ТОЛЬКО по Sheets-замку, где у каждой строки есть ДАТА.
   Файлы прошлых волн дают лишь seen_urls. Раньше они шли и в счётчик компаний: за 13 волн
   накопились 2+ на компанию, и 90 компаний забанились НАВСЕГДА вместо окна «вчера+сегодня».
   Итог замера 04.09: пул показывал 12 ролей вместо 428 — рельсу Ashby чуть не похоронили.
2. Никаких хардкод-списков «сегодня уже подавались» в коде: они протухают через сутки и
   молча режут пул. Занятость живёт в реестре, у неё есть дата.
3. Запись волны без ключа "url" (кастомные страницы HN несут "links") роняла весь отбор
   KeyError-ом — читаем через .get и добираем links.

Updated: 2026-09-04.
"""
import argparse, datetime, glob, json, os, platform, re, sqlite3, sys, time

ROWMAP = os.path.expanduser("~/.claude/skills/apply/rowmap.json")
# Журнал резерваций — единственное, что переживает смерть сессии.
# Файлы волн лежат в папке сессии: у НОВОЙ сессии она пуста, и без этого журнала
# селектор выдал бы роли, которые прямо сейчас подаёт соседняя волна (ломатель 04.09, blocker).
RESERVED = os.path.expanduser("~/.claude/skills/apply/tools/reserved.jsonl")
RESERVE_TTL_H = 18          # столько часов роль считается занятой до отметки в реестре

# Вендоры, к которым не идём вообще: лимиты, баны, exercise-гейты, дубль-классы.
BANNED = {"mistral", "cohere", "openai", "anthropic", "reflection", "runway",
          "xai", "synthesia", "dropbox", "perplexity", "elevenlabs",
          "enpal", "flagright", "iceye", "legion", "jerry", "jerryai"}
DEAD = {"cursor", "anysphere"}            # Ashby отдаёт «Page not found»
FDE_MAX = 9                                # кластерная квота: не вся волна в один кластер
CAP_PER_COMPANY = 2                        # ≤2 подачи на компанию за окно
CAP_WINDOW_DAYS = 1                        # окно = вчера + сегодня
COMPANY_COOLDOWN_DAYS = 30                 # компания сама сказала «хватит» → не стучимся 30 дней

ATS_PAT = {"ashby": r"ashbyhq\.com/([^/]+)/",
           "lever": r"lever\.co/([^/]+)/",
           "greenhouse": r"greenhouse\.io/(?:embed/job_app\?for=)?([^/&?]+)",
           "workable": r"workable\.com/(?:j/)?([^/]+)"}
ANY_PAT = r"(?:ashbyhq\.com|lever\.co)/([^/]+)/"

BAD_TITLE = re.compile(r"junior|intern|analyst|new grad|staff attorney|counsel|"
                       r"recruiter|account executive|sales development|sdr\b|"
                       r"german|french-speak|spanish-speak|japanese|"
                       r"m/w/d|wärme|\bassociate\b(?! director)|"
                       r"mandarin|cantonese|spanish|portuguese|fluency required|bilingual", re.I)
UK_ONLY = re.compile(r"london|united kingdom|\bUK\b|^GB-", re.I)


def slug_of(url, pat):
    m = re.search(pat, url or "", re.I)
    return (m.group(1) if m else "").lower()


def jobs_db():
    env = os.environ.get("JOBS_DB")
    if env:
        return env
    imports = os.environ.get("IMPORTS_ROOT")
    if imports:
        p = os.path.join(imports, "jobs-watch", "jobs.db")
        if os.path.exists(p):
            return p
    return os.path.expanduser("~/Obsidian/_imports/jobs-watch/jobs.db")


def load_lock(rowmap_path=None, today=None):
    """Межмашинный замок: занятые URL всего флота + компанейский кап ПО ДАТАМ.

    Возвращает (seen_urls, comp_count, pending_companies, busy_total, age_hours).
    pending_companies — компании, где висит наш code-gate/blocked: туда второй ролью не идём.

    ⚠️ Путь к замку разрешаем в ТЕЛЕ, а не в значении аргумента: дефолт вычисляется один раз
    при импорте и замораживает ~/ той машины, где модуль загрузился, из-за чего подмена ROWMAP
    в тестах не действует. Канарейка 04.09 на чистом HOME поймала именно это — сетка была
    зелёной лишь потому, что рядом случайно лежал настоящий rowmap.
    """
    rowmap_path = rowmap_path or ROWMAP
    today = today or datetime.date.today()
    cutoff = (today - datetime.timedelta(days=CAP_WINDOW_DAYS)).isoformat()
    cooldown_cutoff = (today - datetime.timedelta(days=COMPANY_COOLDOWN_DAYS)).isoformat()
    seen, comp, pending = set(), {}, set()
    rm = json.load(open(rowmap_path, encoding="utf-8"))
    age_h = (time.time() - rm.get("_built", 0)) / 3600
    # FAIL-CLOSED (ломатель 04.09, blocker): кэш старого формата несёт "map", но не "st".
    # Такой замок молча выглядит как «никто ничего не занял» — и волна пойдёт по занятым
    # ролям всего флота. Пустой замок при непустом реестре = отказ, а не тишина.
    if rm.get("map") and not rm.get("st"):
        raise ValueError("rowmap без ключа 'st' (кэш старого формата) — межмашинный замок "
                         "выродился бы в пустой. Пересобери: mark_row.py build-cache")
    for url, pair in (rm.get("st") or {}).items():
        status = (pair[0] if isinstance(pair, (list, tuple)) else pair) or ""
        date = (pair[1] if isinstance(pair, (list, tuple)) and len(pair) > 1 else "") or ""
        if not status or status == "new":
            continue
        u = url.rstrip("/")
        seen.add(u)
        s = slug_of(u, ANY_PAT)
        if not s:
            continue
        if status == "applied" and date >= cutoff:
            comp[s] = comp.get(s, 0) + 1
        if status in ("code-gate", "blocked-captcha") and date >= cutoff:
            pending.add(s)
        # ⛔ КОМПАНЕЙСКИЙ КАП САМОЙ КОМПАНИИ (замер 04.09, волна 26: 6 из 20 ролей отбиты).
        # Ashby-компании держат свой лимит («вы подавались 2 раза за 30/60/90 дней»,
        # у Ramp — даже per-department). Пока окно не вышло, ЛЮБАЯ их роль = гарантированный
        # отказ: агент тратит 5 минут, форму заполняет впустую. Держим компанию закрытой
        # COMPANY_COOLDOWN_DAYS от даты отказа — это не наказание, а экономия волны.
        if status == "closed" and date >= cooldown_cutoff:
            pending.add(s)
    return seen, comp, pending, len(seen), age_h


def reserved_urls(path=None, ttl_h=RESERVE_TTL_H, now=None):
    """URL, зарезервированные любой сессией этой машины за последние ttl_h часов.

    Мост между «волна отобрана» и «результат отмечен в реестре»: пока волна бежит,
    её роли нигде не помечены, и другая сессия честно считает их свободными.
    """
    path = path or RESERVED
    now = now or time.time()
    out = set()
    if not os.path.exists(path):
        return out
    for line in open(path, encoding="utf-8"):
        line = line.strip()
        if not line:
            continue
        try:
            rec = json.loads(line)
        except Exception:
            continue
        # у записи может быть СВОЙ срок: заполненные формы, ждущие кода/капчи, держим
        # долго — ночная пересборка реестра сбрасывает их статус в 'new' (замер 04.09:
        # 0 строк code-gate наутро после 27 проставленных), и без этого слоя селектор
        # выдал бы их снова, а робот подал бы дубль в уже заполненную форму.
        own_ttl = rec.get("ttl_h") or ttl_h
        if now - rec.get("ts", 0) <= own_ttl * 3600 and rec.get("url"):
            out.add(rec["url"].rstrip("/"))
    return out


def reserve(urls, wave, path=None):
    """Записать отобранные роли в журнал резерваций (append-only, переживает сессию)."""
    path = path or RESERVED
    os.makedirs(os.path.dirname(path), exist_ok=True)
    # os.uname() НЕ существует на Windows (замер ZBOOKG8 05.09.2026: K8/K8b/K9 красные,
    # AttributeError убивал main() целиком). platform.node() портируем на все узлы флота.
    host = (os.environ.get("HOSTNAME") or os.environ.get("COMPUTERNAME")
            or platform.node() or "unknown")
    with open(path, "a", encoding="utf-8") as fh:
        for u in urls:
            fh.write(json.dumps({"url": u, "wave": wave, "ts": time.time(),
                                 "host": host}, ensure_ascii=False) + "\n")
    return len(urls)


def wave_files_urls(wave_dir):
    """URL из файлов прошлых волн — ТОЛЬКО как исключения (см. корень 1 в докстринге)."""
    urls = set()
    pats = ("w*_applied_urls.json", "w*_exclude_urls.json", "[машина флота]_wave*.json")
    for p in sorted({f for pat in pats for f in glob.glob(os.path.join(wave_dir, pat))}):
        try:
            data = json.load(open(p, encoding="utf-8"))
        except Exception:
            continue
        if not isinstance(data, list):
            continue
        for r in data:
            if isinstance(r, dict):
                cand = [r.get("url")] + list(r.get("links") or [])
            else:
                cand = [r]
            for u in cand:
                if isinstance(u, str):
                    urls.add(u.rstrip("/"))
    return urls


def pick(rows, seen, comp, pending, ats, target, per_wave_cap=1):
    """Чистая функция отбора — её и проверяет тест.

    per_wave_cap: сколько ролей одной компании берём В ОДНУ волну (боевое значение 1).
    При подсчёте пула ставим большое число, иначе прибор врёт: он показывал
    «85 доступных ролей» вместо 574, потому что резал по одной на компанию (ломатель 04.09).
    """
    pat = ATS_PAT[ats]
    out, used_comp, cluster_used = [], {}, {}
    for url, company, title, location, cluster, score in rows:
        u = (url or "").rstrip("/")
        slug = slug_of(u, pat)
        cl = (company or slug).lower().replace(" ", "").replace("/", "")
        if not slug or u in seen:
            continue
        if any(b in slug or b in cl for b in BANNED) or slug in DEAD:
            continue
        if slug in pending or cl in pending:
            continue
        if comp.get(slug, 0) >= CAP_PER_COMPANY:
            continue
        if BAD_TITLE.search(title or ""):
            continue
        loc = location or ""
        if UK_ONLY.search(loc) and not re.search(r"europe|EMEA|united states", loc, re.I):
            continue
        if UK_ONLY.search(title or ""):
            continue
        if used_comp.get(slug, 0) >= per_wave_cap:   # в одной волне — не больше роли на компанию
            continue
        c = cluster or "product"
        if c == "fde" and cluster_used.get("fde", 0) >= FDE_MAX:
            continue
        used_comp[slug] = used_comp.get(slug, 0) + 1
        cluster_used[c] = cluster_used.get(c, 0) + 1
        # "ats" ОБЯЗАТЕЛЕН: auto_apply.py читает entry["ats"] (ветка greenhouse) и без него
        # падает KeyError, а run_slice метит исход как "crash:timeout" -- 05.09 (ZBOOKG8) волна
        # 50 встала на первой же роли. Старый selenium_apply/select_wave.py ключ писал; при
        # переносе инструментов в дом скилла (apply-wave-tools-[id]) он потерялся.
        out.append({"url": u, "company": company or slug, "title": title,
                    "location": loc, "cluster": c, "score": score, "ats": ats})
        if len(out) >= target:
            break
    return out


def main():
    ap = argparse.ArgumentParser(description="Отбор волны вакансий Трубы А")
    ap.add_argument("--wave", type=int, required=True, help="номер волны → [машина флота]_wave<N>.json")
    ap.add_argument("--ats", default="ashby", choices=sorted(ATS_PAT), help="какой ATS выбираем")
    ap.add_argument("--target", type=int, default=15, help="сколько ролей взять")
    ap.add_argument("--wave-dir", default=os.environ.get("APPLY_WAVE_DIR", os.getcwd()),
                    help="папка волн (файлы [машина флота]_wave*.json, w*_applied_urls.json)")
    ap.add_argument("--db", default=jobs_db(), help="путь к jobs.db")
    ap.add_argument("--count-only", action="store_true", help="только посчитать доступное, не писать файл")
    ap.add_argument("--no-reserve", action="store_true",
                    help="не писать журнал резерваций (сухой прогон/тест)")
    args = ap.parse_args()

    try:
        seen, comp, pending, busy, age_h = load_lock()
    except Exception as e:
        print(f"⛔ замок Sheets НЕ загружен ({e}) — сперва: python3 ~/.claude/skills/apply/mark_row.py build-cache")
        return 3
    if age_h > 2:
        print(f"⚠️ rowmap {age_h:.1f}ч — прогони: python3 ~/.claude/skills/apply/mark_row.py build-cache")
    print(f"🔒 замок: {busy} занятых URL со всех машин · компаний в капе: "
          f"{sum(1 for v in comp.values() if v >= CAP_PER_COMPANY)} · pending-компаний: {len(pending)}")

    seen |= wave_files_urls(args.wave_dir)
    res = reserved_urls()
    seen |= res
    print(f"🧾 резерваций за {RESERVE_TTL_H}ч: {len(res)} (роли, отобранные другими сессиями и ещё не отмеченные)")
    con = sqlite3.connect(args.db)
    rows = con.execute(
        "SELECT url, company, title, location, cluster, score FROM ats_jobs "
        "WHERE ats=? AND status='new' ORDER BY score DESC, last_seen DESC", (args.ats,)).fetchall()

    out = pick(rows, seen, comp, pending, args.ats,
               10 ** 6 if args.count_only else args.target,
               per_wave_cap=10 ** 6 if args.count_only else 1)
    if args.count_only:
        comps = {slug_of(r["url"], ATS_PAT[args.ats]) for r in out}
        print(f"{args.ats}: доступно ролей {len(out)} у {len(comps)} компаний (из {len(rows)} сырых); "
              f"за одну волну возьмётся не больше {len(comps)} (кап: одна роль на компанию)")
        return 0
    if not out:
        print(f"⛔ {args.ats}: ни одной свободной роли под фильтры (сырых строк {len(rows)})")
        return 2

    outname = os.path.join(args.wave_dir, f"[машина флота]_wave{args.wave}.json")
    json.dump(out, open(outname, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    for i, r in enumerate(out):
        print(f"{i:2} | {r['company']:<22} | {r['cluster']:<12} | {str(r['score']):>3} | "
              f"{(r['title'] or '')[:52]} | {(r['location'] or '')[:28]}")
    if not args.no_reserve:
        reserve([r["url"] for r in out], args.wave)
        print(f"🧾 зарезервировано ролей: {len(out)} (журнал {RESERVED})")
    print(f"\nвсего: {len(out)} → {outname}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
