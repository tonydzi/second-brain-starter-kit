"""Сетка для select_wave.py — стережёт три корня, оплаченных 03-04.09.2026.

Каждый кейс ловит конкретную регрессию, а не «код запускается»:
K1 файлы прошлых волн НЕ считаются в компанейский кап (иначе пул схлопывается: замер 12 вместо 587)
K2 занятый URL из замка не выдаётся повторно (межмашинный дубль)
K3 компания с 2 applied в окне режется, с 1 — проходит
K4 applied СТАРШЕ окна компанию не режет (кап двухдневный, не вечный)
K5 компания с висящим code-gate не берётся второй ролью
K6 запись волны без ключа "url" (страницы HN несут links) не роняет отбор KeyError-ом
K7 фильтры титула/локации: junior/UK-only отсекаются, «Associate Director» проходит
K8 ИНТЕГРАЦИОННЫЙ прогон main(): компания с ролями в старом файле волны не забанена
   (юнит-кейсы этот корень пропускали — мутант прошёл сетку зелёным, потому что pick()
    получает счётчик готовым, а портила его вызывающая сторона)
K9 журнал резерваций: отобранное записывается, читается обратно, протухает по TTL

Изоляция: сетка подменяет и ROWMAP, и RESERVED на временные файлы. Без этого прогон
дописывал фейковую компанию в БОЕВОЙ reserved.jsonl (замер 04.09) — тест, который
портит рабочие данные, хуже отсутствующего.

Прогон: python3 _test_select_wave.py  (0 LLM, 0 сети, временные файлы в tempdir)
Мутанты, на которых сетка обязана краснеть (проверено 04.09): счётчик компаний из файлов
волн · кап без окна дат · игнор pending · r["url"] вместо .get · замок не исключает занятые.
Кто дёргает: /tt после правки select_wave.py, ночная регресс-сетка, verify посылки.
Updated: 2026-09-04.
"""
import datetime, json, os, sys, tempfile, time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import select_wave as sw

TODAY = datetime.date.today()
YESTERDAY = (TODAY - datetime.timedelta(days=1)).isoformat()
OLD = (TODAY - datetime.timedelta(days=30)).isoformat()
A = "https://jobs.ashbyhq.com/{}/{}"

fails = []


def check(name, cond, detail=""):
    print(("  ✅ " if cond else "  ❌ ") + name + ("" if cond else f" — {detail}"))
    if not cond:
        fails.append(name)


def rows(*specs):
    """specs: (slug, jobid, title, location, cluster)"""
    return [(A.format(s, j), s, t, loc, cl, 9) for s, j, t, loc, cl in specs]


def write_rowmap(tmp, entries):
    """entries: {url: [status, date]}"""
    p = os.path.join(tmp, "rowmap.json")
    json.dump({"_built": time.time(), "map": {u: i + 2 for i, u in enumerate(entries)},
               "st": entries}, open(p, "w"))
    return p


def main():
    tmp = tempfile.mkdtemp(prefix="selwave_")

    # ---------- K1 + K6: файлы волн дают только seen_urls, битая запись не роняет ----------
    json.dump([{"url": A.format("acme", "1"), "company": "acme"},
               {"url": A.format("acme", "2"), "company": "acme"},
               {"url": A.format("acme", "3"), "company": "acme"},
               {"company": "hn-page", "links": ["https://example.com/careers"]}],  # ← без "url"
              open(os.path.join(tmp, "[машина флота]_wave1.json"), "w"))
    try:
        seen_files = sw.wave_files_urls(tmp)
        k6 = True
    except Exception as e:
        seen_files, k6 = set(), False
        check("K6 запись без url не роняет отбор", False, repr(e))
    if k6:
        check("K6 запись без url не роняет отбор", True)
        check("K6 links из такой записи попали в исключения",
              "https://example.com/careers" in seen_files, seen_files)

    free = rows(("acme", "9", "Senior Product Manager", "New York", "product"))
    got = sw.pick(free, seen_files, {}, set(), "ashby", 5)
    check("K1 три роли acme в файле волны НЕ банят компанию",
          len(got) == 1 and got[0]["company"] == "acme", got)
    got_same = sw.pick(rows(("acme", "1", "Senior PM", "NY", "product")), seen_files, {}, set(), "ashby", 5)
    check("K1b но конкретный URL из файла волны исключён", got_same == [], got_same)

    # ---------- K2 + K3 + K4 + K5: замок и капы по датам ----------
    rm = write_rowmap(tmp, {
        A.format("busy", "1"): ["applied", YESTERDAY],          # занятый url
        A.format("twice", "1"): ["applied", YESTERDAY],         # компания с 2 подачами в окне
        A.format("twice", "2"): ["applied", TODAY.isoformat()],
        A.format("once", "1"): ["applied", YESTERDAY],          # компания с 1 подачей
        A.format("stale", "1"): ["applied", OLD],               # подача вне окна
        A.format("stale", "2"): ["applied", OLD],
        A.format("gated", "1"): ["code-gate", TODAY.isoformat()],
    })
    seen, comp, pending, busy, age = sw.load_lock(rm, today=TODAY)
    check("K2 занятый URL в замке", A.format("busy", "1") in seen, busy)
    check("K3 компания с 2 applied в окне достигла капа", comp.get("twice") == 2, comp)
    check("K3b компания с 1 applied ниже капа", comp.get("once") == 1, comp)
    check("K4 applied 30-дневной давности НЕ считается в кап", comp.get("stale", 0) == 0, comp)
    check("K5 компания с code-gate попала в pending", "gated" in pending, pending)

    cand = rows(("busy", "1", "Senior PM", "NY", "product"),
                ("twice", "3", "Senior PM", "NY", "product"),
                ("once", "3", "Senior PM", "NY", "product"),
                ("stale", "3", "Senior PM", "NY", "product"),
                ("gated", "3", "Senior PM", "NY", "product"))
    picked = {r["company"] for r in sw.pick(cand, seen, comp, pending, "ashby", 10)}
    check("K2b занятый URL не выдан повторно", "busy" not in picked, picked)
    check("K3c компания в капе не выдана", "twice" not in picked, picked)
    check("K3d компания ниже капа выдана", "once" in picked, picked)
    check("K4b компания со старыми подачами выдана", "stale" in picked, picked)
    check("K5b pending-компания не выдана", "gated" not in picked, picked)

    # ---------- K7: фильтры титула и локации ----------
    t = rows(("f1", "1", "Junior Product Manager", "NY", "product"),
             ("f2", "1", "Senior PM", "Remote - United Kingdom", "product"),
             ("f3", "1", "Associate Director, Business Development", "NY", "founder-bd"),
             ("f4", "1", "Hardware PM (m/w/d)", "Berlin", "product"),
             ("f5", "1", "Senior Solutions Engineer", "London, Europe", "fde"))
    names = {r["company"] for r in sw.pick(t, set(), {}, set(), "ashby", 10)}
    check("K7 junior отсечён", "f1" not in names, names)
    check("K7b UK-only отсечён", "f2" not in names, names)
    check("K7c Associate Director прошёл", "f3" in names, names)
    check("K7d немецкая m/w/d отсечена", "f4" not in names, names)
    check("K7e London+Europe прошёл", "f5" in names, names)

    # ---------- K10 + K11: вендорные баны и кластерная квота (слепая зона сетки до 04.09) ----------
    banned = rows(("mistral", "1", "Senior PM", "NY", "product"),
                  ("openai", "1", "Senior PM", "NY", "product"),
                  ("cursor", "1", "Senior PM", "NY", "product"),          # DEAD
                  ("goodco", "1", "Senior PM", "NY", "product"))
    names_b = {r["company"] for r in sw.pick(banned, set(), {}, set(), "ashby", 10)}
    check("K10 вендор из BANNED не выдан", "mistral" not in names_b and "openai" not in names_b, names_b)
    check("K10b мёртвый борд (DEAD) не выдан", "cursor" not in names_b, names_b)
    check("K10c обычная компания при этом выдана", "goodco" in names_b, names_b)

    fde = rows(*[(f"fde{i}", "1", "Forward Deployed Engineer", "NY", "fde") for i in range(sw.FDE_MAX + 3)])
    got_fde = sw.pick(fde, set(), {}, set(), "ashby", 100)
    check("K11 кластерная квота fde соблюдена", len(got_fde) == sw.FDE_MAX,
          f"взято {len(got_fde)} при квоте {sw.FDE_MAX}")
    mixed = fde + rows(("prodco", "1", "Senior PM", "NY", "product"))
    got_mixed = [r["company"] for r in sw.pick(mixed, set(), {}, set(), "ashby", 100)]
    check("K11b другой кластер после исчерпания квоты fde проходит", "prodco" in got_mixed, got_mixed[-3:])

    # ---------- K8: ИНТЕГРАЦИОННЫЙ прогон main() — стережёт главный корень целиком ----------
    # Мутант «файлы волн снова наполняют компанейский счётчик» юнит-кейсы K1 НЕ ловили:
    # pick() получает comp готовым, а наполняется он в main(). Замер 04.09: именно эта
    # регрессия схлопнула пул с 587 ролей до 12. Гоняем полный путь.
    import sqlite3 as _sq
    db = os.path.join(tmp, "jobs.db")
    con = _sq.connect(db)
    con.execute("CREATE TABLE ats_jobs (url TEXT, company TEXT, title TEXT, location TEXT, "
                "cluster TEXT, score INT, ats TEXT, status TEXT, last_seen TEXT)")
    for j in range(1, 6):                      # 5 свободных ролей одной компании
        con.execute("INSERT INTO ats_jobs VALUES (?,?,?,?,?,?,?,?,?)",
                    (A.format("wideco", str(j)), "wideco", "Senior Product Manager", "New York",
                     "product", 9, "ashby", "new", "2026-09-04"))
    con.commit()
    # в файле прошлой волны — ТРИ роли той же компании (в кап идти не должны)
    json.dump([{"url": A.format("wideco", "91"), "company": "wideco"},
               {"url": A.format("wideco", "92"), "company": "wideco"},
               {"url": A.format("wideco", "93"), "company": "wideco"}],
              open(os.path.join(tmp, "[машина флота]_wave7.json"), "w"))
    rm2 = write_rowmap(tmp, {A.format("other", "1"): ["applied", YESTERDAY]})
    # ⚠️ тест НЕ трогает боевые данные: журнал резерваций уводим во временный файл
    # (замер 04.09: без этого прогон сетки дописывал фейковую компанию в живой reserved.jsonl)
    saved_rowmap, saved_argv, saved_res = sw.ROWMAP, sys.argv, sw.RESERVED
    sw.ROWMAP = rm2
    sw.RESERVED = os.path.join(tmp, "reserved.jsonl")
    sys.argv = ["select_wave.py", "--wave", "99", "--ats", "ashby", "--target", "3",
                "--wave-dir", tmp, "--db", db]
    try:
        rc = sw.main()
        produced = json.load(open(os.path.join(tmp, "[машина флота]_wave99.json"), encoding="utf-8"))
    except Exception as e:
        rc, produced = -1, []
        check("K8 main() отработал", False, repr(e))
    finally:
        sw.ROWMAP, sys.argv, sw.RESERVED = saved_rowmap, saved_argv, saved_res
    check("K8 main() вернул 0", rc == 0, rc)
    check("K8b компания с 3 ролями в старом файле волны НЕ забанена",
          len(produced) >= 1 and produced[0]["company"] == "wideco",
          f"выдано {len(produced)}: {[p.get('company') for p in produced]}")
    # K9: резервация — мост между «волна отобрана» и «результат отмечен»
    resfile = os.path.join(tmp, "reserved.jsonl")
    check("K9 отобранные роли записаны в журнал резерваций",
          os.path.exists(resfile) and len(open(resfile).read().strip().splitlines()) == len(produced),
          f"файл={os.path.exists(resfile)}")
    got_res = sw.reserved_urls(resfile)
    check("K9b резервации читаются обратно",
          got_res == {p["url"] for p in produced}, got_res)
    check("K9c протухшая резервация (старше TTL) не считается занятой",
          sw.reserved_urls(resfile, ttl_h=0.0001, now=time.time() + 999999) == set(),
          "старые записи всё ещё блокируют роли")

    # K12: у записи резервации может быть СВОЙ срок (карантин заполненных форм = 720ч).
    # Замер 04.09: этот патч ОДИН РАЗ уже потерялся при цельной перезаписи файла —
    # без кейса регрессия молчит, а карантин протухает за 18ч и робот подаёт дубль.
    qf = os.path.join(tmp, "quarantine.jsonl")
    with open(qf, "w") as fh:
        fh.write(json.dumps({"url": A.format("gatedco", "1"), "wave": "pending-gated",
                             "ts": time.time() - 100 * 3600, "ttl_h": 720}) + "\n")   # 100 ч назад, срок 720 ч
        fh.write(json.dumps({"url": A.format("oldwave", "1"), "wave": 3,
                             "ts": time.time() - 100 * 3600}) + "\n")                  # 100 ч назад, срок дефолтный 18 ч
    q = sw.reserved_urls(qf)
    check("K12 карантинная запись со своим ttl_h=720 жива через 100 ч", A.format("gatedco", "1") in q, q)
    check("K12b обычная резервация через 100 ч протухла", A.format("oldwave", "1") not in q, q)

    # K13: компания, которая САМА отказала («вы подавались недавно»), выбывает на COMPANY_COOLDOWN_DAYS.
    # Замер 04.09 волна 26: 6 из 20 ролей — гарантированные отказы, волна потрачена впустую.
    VERY_OLD = (TODAY - datetime.timedelta(days=sw.COMPANY_COOLDOWN_DAYS + 10)).isoformat()
    rm3 = write_rowmap(tmp, {A.format("capco", "1"): ["closed", TODAY.isoformat()],
                             A.format("oldcap", "1"): ["closed", VERY_OLD]})
    seen3, comp3, pending3, _, _ = sw.load_lock(rm3, today=TODAY)
    check("K13 компания со свежим closed попала в pending", "capco" in pending3, pending3)
    check(f"K13b компания с closed старше {sw.COMPANY_COOLDOWN_DAYS}д снова открыта", "oldcap" not in pending3, pending3)
    picked3 = {r["company"] for r in sw.pick(
        rows(("capco", "9", "Senior PM", "NY", "product"), ("oldcap", "9", "Senior PM", "NY", "product")),
        set(), {}, pending3, "ashby", 10)}
    check("K13c роль закрытой компании не выдана", "capco" not in picked3, picked3)
    check("K13d роль отлежавшейся компании выдана", "oldcap" in picked3, picked3)

    check("K8c конкретные URL из старого файла волны не выданы",
          all(p["url"] not in (A.format("wideco", "91"), A.format("wideco", "92"),
                               A.format("wideco", "93")) for p in produced), produced)

    print(f"\n{'ВСЁ ЗЕЛЁНОЕ' if not fails else 'КРАСНОЕ: ' + ', '.join(fails)}")
    return 1 if fails else 0


if __name__ == "__main__":
    sys.exit(main())
