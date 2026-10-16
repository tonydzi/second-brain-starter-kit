#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""brain_kit.py — «второй мозг за 20 минут» для ОДНОГО человека.

Заводит ЛИЧНЫЙ волт члена команды на ЕГО машине и ставит границу приватности
ПАПКАМИ (не frontmatter-полем). Почему папками — решено 2026-07-29, АК-47:
  * папку видно в проводнике без Obsidian и без знания markdown;
  * перенос = перетащить мышкой, откат = перетащить назад;
  * забыл поле в frontmatter -> заметка утекает (fail-open);
    забыл положить в 03-Shared -> заметка НЕ уедет (fail-closed);
  * граница синхронизации в Syncthing и так папочная — механизм совпадает с транспортом.

Три корзины (слова владельца, не техника):
  01-Private  🔴 только моё      — не уезжает никуда и никогда
  02-Team     🟡 шарю точечно    — уедет, только если владелец сам положит сюда
  03-Shared   🟢 общий волт      — едет в общий волт команды

Команды:
  init    --person <имя> --root <папка>   создать волт (идемпотентно, ничего не затирает)
  check   --root <папка>                  структура цела? граница на месте? (exit 0/2)
  receipt --root <папка> [--out f.md]     КВИТАНЦИЯ: только счётчики и даты, НИ ОДНОГО
                                          имени файла и ни строчки содержимого
  fix     --root <папка> [--person <имя>] ВОССТАНОВИТЬ границу и пропавшие папки
                                          (строки в .stignore только дописывает)
  --self-test                             регрессия (16 проверок)

Zero-knowledge: наружу (в общий чат / хабу / Антону) уходит ТОЛЬКО квитанция.
Секреты и пароли в волт не кладём — им дом в secrets-store.

Паспорт детали: 00-System\\Brain-Kit-README.md
"""
import io, json, os, re, sys, argparse, datetime

for _s in (sys.stdout, sys.stderr):        # cp1251-консоль -> кириллица не роняет запуск
    try: _s.reconfigure(encoding="utf-8", errors="replace")
    except Exception: pass

VERSION = "1.0"
MARKER = ".brain-kit.json"

# (папка, эмодзи, короткое имя, что сюда класть)
BASKETS = [
    ("01-Private", "🔴", "только моё",
     "Всё, что не должно уехать никуда: здоровье, деньги, семья, личные мысли.\n"
     "Эта папка не синхронизируется. Даже если волт когда-нибудь расшарят — она останется тут."),
    ("02-Team", "🟡", "шарю точечно",
     "То, чем ты готова поделиться с командой ИМЕННО СЕЙЧАС и осознанно.\n"
     "Claude может предложить «давай положим сюда» — но кладёшь только ты."),
    ("03-Shared", "🟢", "общий волт",
     "Рабочее и полезное всем: инструкции, находки, решения по общим проектам.\n"
     "Уезжает в общий волт команды."),
]
# Что обязано быть закрыто в .stignore. ОДИН источник: и check, и fix читают отсюда,
# иначе проверка и починка разъезжаются и «починили» перестаёт значить «check зелёный».
BOUNDARY_MUST = ["01-Private", "02-Team"]
IDENTITY = "00-Про-меня"
ORIGINALS = "_originals"

README = """# Твой второй мозг — читай меня первой

Привет, {person}. Это твоя личная папка знаний. Она живёт **на твоём компьютере**.

## Три корзины — вся приватность целиком

| Папка | Что это | Кто увидит |
|---|---|---|
| `01-Private` | 🔴 только моё | **никто**, кроме тебя |
| `02-Team` | 🟡 шарю точечно | команда — но только то, что ты сюда сама положила |
| `03-Shared` | 🟢 общий волт | команда, это общая рабочая база |

**Как поделиться заметкой?** Перетащи файл мышкой в `02-Team` или `03-Shared`.
**Как забрать назад?** Перетащи обратно в `01-Private`.
Всё. Больше знать нечего.

**Правило при сомнении:** не уверена — оставляй в `01-Private`. Поделиться можно завтра,
забрать обратно уже уехавшее — нельзя.

## Что ещё лежит рядом

- `00-Про-меня` — кто ты, как ты работаешь, как любишь получать ответы. Это то,
  из-за чего твой Claude отвечает тебе, а не «вообще кому-то».
- `_originals` — сырые оригиналы того, что импортировали (письма, переписки).

## Чего тут НЕ будет

- Паролей и секретов — им место в защищённом хранилище, не в заметках.
- Антон сюда не смотрит. Наружу уходит только квитанция: «столько-то заметок,
  последняя такого-то числа». Ни одного названия файла, ни одной строчки текста.

---
_Заведено {date} · brain_kit v{version}_
"""

BASKET_NOTE = """# {emoji} {short}

{what}

---
Папка-корзина, brain_kit v{version}. Переносить заметки сюда и отсюда — мышкой.
"""

IDENTITY_SEED = """---
type: person-profile
owner: {person}
created: {date}
basket: private
---

# Про меня — {person}

> Это черновик. Твой Claude дополняет его сам, когда ты что-то про себя рассказываешь.

## Кто я
- Роли (работа / семья / проекты):

## Как я работаю
- Инструменты, которыми пользуюсь каждый день:
- Ритм дня (когда я в рабочем режиме):
- Что меня бесит в работе:
- Что мне помогает:

## Как со мной разговаривать
- Длина ответов (коротко / подробно):
- Язык:
- Тон:

## Где что лежит
- Почта:
- Мессенджеры:
- Соцсети:
- Файлы и облака:

## Чего я хочу от своего Claude в первую очередь
-
"""

PRIVACY_MAP = """---
type: privacy-map
owner: {person}
created: {date}
basket: private
---

# Моя карта приватности

Живой документ: меняется, когда меняется решение владельца. Решает **только {person}**.

| Тема | Корзина | Решено |
|---|---|---|
| Рабочие задачи и проекты | 🟢 03-Shared | {date} |
| Мои заметки про то, как я работаю | 🟡 02-Team | {date} |
| Здоровье, деньги, семья, документы | 🔴 01-Private | {date} |
| Личные переписки | 🔴 01-Private | {date} |

Дефолт для всего, чего нет в таблице: 🔴 01-Private.
"""

# Syncthing-игнор: даже если волт когда-нибудь расшарят целиком, приватное не уедет.
STIGNORE = """// brain_kit: граница приватности. Не удалять.
// Приватная и точечная корзины не уезжают по синку НИКОГДА.
01-Private
02-Team
00-Про-меня
_originals
.brain-kit.json
"""


def _now():
    return datetime.datetime.now().strftime("%Y-%m-%d")


def _write(path, text, force=False):
    """Пишем только если файла нет — init обязан быть идемпотентным и не затирать живое."""
    if os.path.exists(path) and not force:
        return False
    with io.open(path, "w", encoding="utf-8", newline="\n") as f:
        f.write(text)
    return True


def cmd_init(root, person):
    created, skipped = [], []
    os.makedirs(root, exist_ok=True)
    for name, emoji, short, what in BASKETS:
        d = os.path.join(root, name)
        os.makedirs(d, exist_ok=True)
        p = os.path.join(d, "_ЧТО-СЮДА.md")
        (created if _write(p, BASKET_NOTE.format(
            emoji=emoji, short=short, what=what, version=VERSION)) else skipped).append(p)
    for d in (IDENTITY, ORIGINALS):
        os.makedirs(os.path.join(root, d), exist_ok=True)

    files = [
        (os.path.join(root, "README-ЧИТАЙ-МЕНЯ.md"),
         README.format(person=person, date=_now(), version=VERSION)),
        (os.path.join(root, IDENTITY, "про-меня.md"),
         IDENTITY_SEED.format(person=person, date=_now())),
        (os.path.join(root, IDENTITY, "карта-приватности.md"),
         PRIVACY_MAP.format(person=person, date=_now())),
        (os.path.join(root, ".stignore"), STIGNORE),
    ]
    for p, text in files:
        (created if _write(p, text) else skipped).append(p)

    _write(os.path.join(root, MARKER), json.dumps(
        {"person": person, "created": _now(), "version": VERSION,
         "baskets": [b[0] for b in BASKETS]}, ensure_ascii=False, indent=1))
    print("Волт: %s" % root)
    print("Владелец: %s" % person)
    print("Создано файлов: %d, уже было (не тронуто): %d" % (len(created), len(skipped)))
    for p in created:
        print("  + %s" % os.path.relpath(p, root))
    return 0


def cmd_fix(root, person):
    """Чинит ГРАНИЦУ, не трогая содержимое волта.

    Зачем отдельная команда: init намеренно ничего не перезаписывает (идемпотентность),
    поэтому сломанную границу он оставлял сломанной. Найдено 2026-07-29 на живом пилоте:
    убрали строку 01-Private из .stignore -> check краснеет, а починить нечем; повторный
    init отвечает «уже было (не тронуто)» и уходит. Для не-технаря это тупик: инструмент
    говорит «ЧИНИТЬ» и не чинит.

    Правило безопасности: строки только ДОБАВЛЯЕМ. Чужие строки в .stignore не наши,
    удалять их нельзя — человек мог закрыть что-то ещё."""
    if not os.path.exists(root):
        print("НЕТ ВОЛТА: %s — сначала init" % root); return 2
    cmd_init(root, person)                       # вернёт на место пропавшие папки и файлы
    st = os.path.join(root, ".stignore")
    text = io.open(st, encoding="utf-8", errors="replace").read() if os.path.exists(st) else ""
    lines = [l.rstrip("\r\n") for l in text.splitlines()]
    added = [m for m in BOUNDARY_MUST if m not in lines]
    if added:
        if text and not text.endswith("\n"):
            text += "\n"
        text += "".join(m + "\n" for m in added)
        with io.open(st, "w", encoding="utf-8", newline="\n") as f:
            f.write(text)
        print("ГРАНИЦА ВОССТАНОВЛЕНА, дописано в .stignore: %s" % ", ".join(added))
    else:
        print("ГРАНИЦА: и так на месте, дописывать нечего")
    return cmd_check(root)


def _stat_dir(root, sub):
    """-> (сколько заметок, самая свежая дата). Только числа: имён не собираем."""
    n, newest = 0, None
    d = os.path.join(root, sub)
    for dirpath, dirs, names in os.walk(d):
        dirs[:] = [x for x in dirs if not x.startswith(".")]
        for name in names:
            if not name.lower().endswith(".md") or name.startswith("_ЧТО-СЮДА"):
                continue
            n += 1
            ts = os.path.getmtime(os.path.join(dirpath, name))
            newest = ts if newest is None or ts > newest else newest
    date = datetime.datetime.fromtimestamp(newest).strftime("%Y-%m-%d") if newest else "—"
    return n, date


def cmd_check(root):
    """exit 0 = комплект цел; 2 = чего-то нет (тогда печатаем ЧЕГО именно)."""
    problems = []
    if not os.path.exists(os.path.join(root, MARKER)):
        problems.append("нет %s — это не brain_kit-волт" % MARKER)
    for name, _, _, _ in BASKETS:
        if not os.path.isdir(os.path.join(root, name)):
            problems.append("нет корзины %s" % name)
    for f in ("README-ЧИТАЙ-МЕНЯ.md", ".stignore"):
        if not os.path.exists(os.path.join(root, f)):
            problems.append("нет %s" % f)
    st = os.path.join(root, ".stignore")
    if os.path.exists(st):
        text = io.open(st, encoding="utf-8", errors="replace").read()
        for must in BOUNDARY_MUST:
            if must not in text:
                problems.append("граница дырявая: %s не исключён в .stignore" % must)
    for p in problems:
        print("ПРОБЛЕМА: %s" % p)
    print("--- brain_kit check: %s -> %s" % (root, "ГОДЕН" if not problems else "ЧИНИТЬ"))
    return 0 if not problems else 2


def cmd_receipt(root, out=None):
    """Квитанция мозга: только счётчики и даты. Имён файлов и содержимого тут нет
    ПО УСТРОЙСТВУ — _stat_dir возвращает число и дату, названия не собираются вовсе."""
    if not os.path.exists(os.path.join(root, MARKER)):
        print("ERR: %s не найден — сначала init" % MARKER)
        return 2
    meta = json.load(io.open(os.path.join(root, MARKER), encoding="utf-8"))
    rows = [(name, emoji, short) + _stat_dir(root, name) for name, emoji, short, _ in BASKETS]
    ident_n, ident_d = _stat_dir(root, IDENTITY)
    total = sum(r[3] for r in rows) + ident_n

    lines = ["# Квитанция мозга — %s" % meta.get("person", "?"),
             "", "_на %s · только числа, без содержимого_" % _now(), "",
             "| Корзина | Заметок | Последняя запись |", "|---|---|---|"]
    for name, emoji, short, n, d in rows:
        lines.append("| %s %s (`%s`) | %d | %s |" % (emoji, short, name, n, d))
    lines += ["| 📇 про меня (`%s`) | %d | %s |" % (IDENTITY, ident_n, ident_d),
              "| **всего** | **%d** | |" % total, "",
              "Волт заведён: %s · brain_kit v%s" % (meta.get("created", "?"), VERSION),
              "", "> Ни одного названия файла и ни строчки текста в этой квитанции нет —",
              "> так устроен генератор, а не так договорились."]
    text = "\n".join(lines) + "\n"
    if out:
        _write(out, text, force=True)
        print("Квитанция -> %s" % out)
    print(text)
    return 0


def _self_test():
    """Тест обязан КРАСНЕТЬ на сломанном комплекте — иначе он не тест."""
    import tempfile, shutil
    bad = 0
    tmp = tempfile.mkdtemp(prefix="brainkit-test-")
    try:
        root = os.path.join(tmp, "Vault")
        cmd_init(root, "Тестовый Человек")

        for name, _, _, _ in BASKETS:                                    # 1-3
            if not os.path.isdir(os.path.join(root, name)):
                print("  MISS: не создана корзина %s" % name); bad += 1
        if cmd_check(root) != 0:                                          # 4
            print("  MISS: check не принял свежесозданный волт"); bad += 1

        seed = os.path.join(root, "01-Private", "тайное-имя-файла.md")     # 5
        io.open(seed, "w", encoding="utf-8").write("# секрет\nтекст который нельзя показывать\n")
        n, _ = _stat_dir(root, "01-Private")
        if n != 1:
            print("  MISS: счётчик приватной корзины = %d, ждали 1" % n); bad += 1

        buf = io.StringIO(); real = sys.stdout; sys.stdout = buf          # 6-7
        cmd_receipt(root); sys.stdout = real
        r = buf.getvalue()
        if "тайное-имя-файла" in r:
            print("  LEAK: квитанция показала имя файла"); bad += 1
        if "нельзя показывать" in r:
            print("  LEAK: квитанция показала содержимое"); bad += 1

        before = io.open(seed, encoding="utf-8").read()                   # 8
        cmd_init(root, "Тестовый Человек")
        if io.open(seed, encoding="utf-8").read() != before:
            print("  MISS: повторный init затёр живой файл"); bad += 1

        st = io.open(os.path.join(root, ".stignore"), encoding="utf-8").read()  # 9-10
        for must in ("01-Private", "02-Team"):
            if must not in st:
                print("  MISS: %s не закрыт в .stignore" % must); bad += 1

        # --- ЛОМАЕМ НАРОЧНО: тест обязан покраснеть
        os.remove(os.path.join(root, ".stignore"))                        # 11
        if cmd_check(root) == 0:
            print("  BLIND: check не заметил пропажу .stignore"); bad += 1
        _write(os.path.join(root, ".stignore"), "// пусто\n", force=True) # 12
        if cmd_check(root) == 0:
            print("  BLIND: check не заметил дырявую границу"); bad += 1
        shutil.rmtree(os.path.join(root, "02-Team"))                      # 13
        if cmd_check(root) == 0:
            print("  BLIND: check не заметил пропажу корзины"); bad += 1

        # 14-16 — починка. Ломаем границу так, как её сломает живой человек: правкой
        # .stignore руками. Своя строка человека обязана пережить починку.
        _write(os.path.join(root, ".stignore"),
               "\n".join(["// brain_kit", "02-Team", "00-Про-меня", "моя-своя-строка", ""]),
               force=True)
        if cmd_check(root) == 0:
            print("  BLIND: check не заметил дырявую границу (перед fix)"); bad += 1
        cmd_fix(root, "Тестовый Человек")
        if cmd_check(root) != 0:
            print("  MISS: fix не вернул границу на место"); bad += 1
        st = io.open(os.path.join(root, ".stignore"), encoding="utf-8").read()
        if "моя-своя-строка" not in st:
            print("  DAMAGE: fix съел чужую строку в .stignore"); bad += 1
    finally:
        shutil.rmtree(tmp, ignore_errors=True)
    print("SELF-TEST: %s (%d проблем)" % ("PASS" if not bad else "FAIL", bad))
    return 1 if bad else 0


def main(argv):
    ap = argparse.ArgumentParser(prog="brain_kit.py", add_help=True)
    ap.add_argument("cmd", nargs="?", choices=["init", "check", "receipt", "fix"])
    ap.add_argument("--person", default="Владелец")
    ap.add_argument("--root")
    ap.add_argument("--out")
    ap.add_argument("--self-test", action="store_true")
    a = ap.parse_args(argv[1:])
    if a.self_test:
        return _self_test()
    if not a.cmd or not a.root:
        ap.print_help(); print("\n" + __doc__); return 2
    if a.cmd == "init":
        return cmd_init(a.root, a.person)
    if a.cmd == "check":
        return cmd_check(a.root)
    if a.cmd == "fix":
        return cmd_fix(a.root, a.person)
    return cmd_receipt(a.root, a.out)


if __name__ == "__main__":
    sys.exit(main(sys.argv))
