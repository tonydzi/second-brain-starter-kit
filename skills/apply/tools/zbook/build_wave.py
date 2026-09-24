# -*- coding: utf-8 -*-
"""Собрать батч подачи из вердиктов воркфлоу: python build_wave.py <pool.json> <prefix> <journal.jsonl> <out.json>

Читает последний result с полем picked из journal.jsonl воркфлоу wave-fit-and-answers, находит роль в пуле,
подмешивает ответы из <prefix>_extra_<slug>.json (слаг по компании, при двух файлах — по куску тайтла),
кластер берёт из вердикта (под CV_MAP движка). Роли без файла ответов всё равно идут — с канон-правилами моста.
"""
import json, os, re, sys, glob
sys.stdout.reconfigure(encoding="utf-8")
HERE = os.path.dirname(os.path.abspath(__file__))
pool_p, prefix, journal_p, out_p = sys.argv[1:5]

pool = json.load(open(os.path.join(HERE, pool_p), encoding="utf-8"))
picked, verdicts = None, []
for line in open(journal_p, encoding="utf-8"):
    try:
        rec = json.loads(line)
    except Exception:
        continue
    if not isinstance(rec, dict):
        continue
    res = rec.get("result")
    # в журнале лежат результаты АГЕНТОВ: у судей — verdicts, финальный picked воркфлоу туда не пишется
    if isinstance(res, dict) and isinstance(res.get("verdicts"), list):
        verdicts.extend(res["verdicts"])
    if isinstance(res, dict) and isinstance(res.get("picked"), list):
        picked = res["picked"]
if picked is None and verdicts:
    picked = [v for v in verdicts if v.get("fit") in ("strong", "ok")]
    print(f"вердиктов судей: {len(verdicts)} -> берём {len(picked)} (strong/ok)")
if not picked:
    print("в журнале нет ни picked, ни verdicts — воркфлоу не завершился или вернул пусто")
    sys.exit(2)

CLUSTER_OK = {"fde", "founder-bd", "product", "devrel", "security", "startup-ecosystem"}
extras = {}
for f in glob.glob(os.path.join(HERE, f"{prefix}_extra_*.json")):
    slug = os.path.basename(f)[len(prefix) + 7:-5]
    try:
        extras[slug] = json.load(open(f, encoding="utf-8"))
    except Exception as e:
        print("BAD extra", slug, e)

def key(s):
    return re.sub(r"[^a-z0-9]", "", (s or "").lower())

def pick_extra(company, title):
    co, ti = key(company), key(title)
    cands = [(s, d) for s, d in extras.items() if key(s).startswith(co[:8]) or co.startswith(key(s.split("-")[0])[:8])]
    if not cands:
        return {}
    if len(cands) == 1:
        return cands[0][1]
    # несколько файлов на компанию: берём тот, чей хвост слага встречается в тайтле
    for s, d in cands:
        tail = key(s.split("-", 1)[1]) if "-" in s else ""
        if tail and tail[:6] in ti:
            return d
    return max(cands, key=lambda sd: len(sd[0]))[1]

out, seen = [], set()
for v in picked:
    t = next((dict(x) for x in pool
              if key(x["company"]) == key(v["company"]) and key(v["title"])[:25] in key(x["title"])), None)
    if t is None:
        t = next((dict(x) for x in pool if key(x["company"]) == key(v["company"]) and x["url"] not in seen), None)
    if t is None:
        print("НЕ НАЙДЕНО в пуле:", v["company"], "|", v["title"][:50]); continue
    if t["url"] in seen:
        continue
    seen.add(t["url"])
    t["cluster"] = v.get("cluster") if v.get("cluster") in CLUSTER_OK else (t.get("cluster") or "fde")
    ex = pick_extra(t["company"], t["title"])
    if ex:
        t["extra"] = ex
    t.pop("score", None); t.pop("tier", None)
    out.append(t)
    print(f"{v.get('fit','?'):<6} {t['company'][:20]:<20} | {t['title'][:44]:<44} | {t['cluster']:<11} | правил {len(ex)}")

json.dump(out, open(os.path.join(HERE, out_p), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
print(f"\n{out_p}: {len(out)} ролей")
