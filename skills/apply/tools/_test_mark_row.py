"""Сетка для mark_row.py — отметка строк реестра Трубы А.

Штатный `selftest` внутри mark_row.py проверял только json-roundtrip и callable:
три мутанта подряд (запись в row+1, снятая проверка возраста кэша, build_cache без "st")
проходили его зелёными. Эта сетка бьёт по самой механике записи.

M1 mark() пишет РОВНО в строку из кэша и ровно в колонки O:P
M2 значения уходят в правильном порядке [status, applied]
M3 протухший кэш (> MAX_CACHE_AGE_H) → отказ и НИ ОДНОЙ записи в лист
M4 URL не в кэше → отказ и НИ ОДНОЙ записи (иначе метка уедет на чужую строку)
M5 build_cache пишет и "map", и "st" (без "st" межмашинный замок вырождается в пустой)
M6 в "st" попадают статус И дата, строки без статуса не попадают

Изоляция: модуль `sheets` подменяется фейком в sys.modules, CACHE — во временную папку.
Ни одного сетевого вызова, боевой кэш не трогается.

Прогон: python3 _test_mark_row.py   ·  Кто дёргает: /tt после правки mark_row.py, verify посылки.
Updated: 2026-09-04.
"""
import json, os, sys, tempfile, time, types

HERE = os.path.dirname(os.path.abspath(__file__))
SKILL = os.path.dirname(HERE)
sys.path.insert(0, SKILL)

WRITES = []                      # сюда фейковый sheets складывает всё, что у него просили записать


def _install_fake_sheets(rows=None):
    fake = types.ModuleType("sheets")
    fake.set_range = lambda sid, rng, vals: WRITES.append((sid, rng, vals))
    fake.read_as_dicts = lambda sid, tab: rows or []
    sys.modules["sheets"] = fake
    return fake


fails = []


def check(name, cond, detail=""):
    print(("  ✅ " if cond else "  ❌ ") + name + ("" if cond else f" — {detail}"))
    if not cond:
        fails.append(name)


def main():
    _install_fake_sheets()
    import mark_row as mr

    tmp = tempfile.mkdtemp(prefix="markrow_")
    saved_cache = mr.CACHE
    mr.CACHE = os.path.join(tmp, "rowmap.json")

    url_a = "https://jobs.ashbyhq.com/acme/aaa"
    url_b = "https://jobs.ashbyhq.com/beta/bbb"

    def write_cache(age_h=0.0):
        json.dump({"_built": time.time() - age_h * 3600,
                   "map": {url_a: 42, url_b: 77},
                   "st": {url_a: ["new", ""]}},
                  open(mr.CACHE, "w", encoding="utf-8"))

    # ---------- M1 + M2: точная строка, точные колонки, порядок значений ----------
    write_cache()
    WRITES.clear()
    rc = mr.mark(url_a, "applied", "2026-09-04")
    check("M1 mark() вернул 0", rc == 0, rc)
    check("M1b запись ровно одна", len(WRITES) == 1, WRITES)
    if WRITES:
        sid, rng, vals = WRITES[0]
        check("M1c диапазон = строка из кэша, колонки O:P", rng == "registry!O42:P42", rng)
        check("M2 значения [status, applied] в правильном порядке",
              vals == [["applied", "2026-09-04"]], vals)

    # ---------- M3: протухший кэш не пишет НИЧЕГО ----------
    write_cache(age_h=mr.MAX_CACHE_AGE_H + 1)
    WRITES.clear()
    rc = mr.mark(url_a, "applied", "2026-09-04")
    check("M3 протухший кэш → отказ", rc != 0, rc)
    check("M3b протухший кэш → ни одной записи в лист", WRITES == [], WRITES)

    # ---------- M4: неизвестный URL не пишет НИЧЕГО ----------
    write_cache()
    WRITES.clear()
    rc = mr.mark("https://jobs.ashbyhq.com/unknown/zzz", "applied", "2026-09-04")
    check("M4 URL не в кэше → отказ", rc != 0, rc)
    check("M4b URL не в кэше → ни одной записи (метка не уедет на чужую строку)", WRITES == [], WRITES)

    # ---------- M5 + M6: build_cache даёт и map, и st ----------
    _install_fake_sheets(rows=[
        {"url": url_a, "status": "applied", "applied": "2026-09-03"},
        {"url": url_b, "status": "", "applied": ""},
        {"url": "", "status": "applied", "applied": "2026-09-03"},        # мусорная строка без url
    ])
    sys.modules.pop("mark_row", None)
    import importlib
    mr2 = importlib.import_module("mark_row")
    mr2.CACHE = os.path.join(tmp, "rowmap2.json")
    mr2.build_cache()
    data = json.load(open(mr2.CACHE, encoding="utf-8"))
    check("M5 build_cache пишет 'map'", bool(data.get("map")), list(data))
    check("M5b build_cache пишет 'st' (иначе замок пуст)", bool(data.get("st")), list(data))
    check("M6 в 'st' статус и дата", data["st"].get(url_a) == ["applied", "2026-09-03"], data.get("st"))
    check("M6b строка без статуса в 'st' не попала", url_b not in data.get("st", {}), data.get("st"))
    check("M6c строка без url не попала в 'map'", "" not in data.get("map", {}), list(data.get("map", {}))[:3])

    mr.CACHE = saved_cache
    print(f"\n{'ВСЁ ЗЕЛЁНОЕ' if not fails else 'КРАСНОЕ: ' + ', '.join(fails)}")
    return 1 if fails else 0


if __name__ == "__main__":
    sys.exit(main())
