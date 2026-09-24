# -*- coding: utf-8 -*-
"""_test_fleet_install.py -- офлайн-тест раскатчика: НИЧЕГО не отправляет и никуда не ходит.

Проверяет ровно то, что может тихо соврать: сверку md5, разворачивание плейсхолдеров в командах,
исключение своего узла из целей, honest-exit при недостижимых, и что --dry-run не трогает сеть.
Run: python3 _test_fleet_install.py -> exit 0 = всё зелёное.
"""
import os, sys, json, tempfile

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import fleet_install as fi

FAILS = []
N = [0]


def check(name, cond):
    N[0] += 1
    print(("PASS " if cond else "FAIL ") + name)
    if not cond:
        FAILS.append(name)


def run():
    # md5 считается по содержимому и меняется при правке
    with tempfile.NamedTemporaryFile("w", suffix=".py", delete=False) as fh:
        fh.write("print('a')\n")
        p = fh.name
    h1 = fi.md5(p)
    open(p, "a").write("# tail\n")
    h2 = fi.md5(p)
    check("md5 меняется при правке файла", h1 != h2 and len(h1) == 32)

    # реестр узлов читается и свой узел вычисляется
    nodes = fi.load_nodes()
    check("реестр узлов прочитан", isinstance(nodes, dict) and len(nodes) >= 3)
    me = fi.this_node()
    check("свой узел определён, не пустой", bool(me) and me.lower() != "unknown")
    check("свой узел -- канонический ключ реестра", me in nodes or not nodes)

    # свой узел НЕ попадает в цели (иначе раскатка сама себе по ssh)
    targets = {k: v for k, v in nodes.items() if k != me}
    check("свой узел исключён из целей", me not in targets and len(targets) == len(nodes) - 1)

    # сеть недоступна при dry-run: подменяем run() на бомбу
    [человек] = {"called": False}
    real = fi.run
    fi.run = lambda *a, **k: ([человек].__setitem__("called", True), (0, ""))[1]
    try:
        code = fi.main(["--id", "test-x", "--file", p, "--apply", "{py} {f} --install",
                        "--verify", "{py} {f} --verify", "--dry-run"])
    finally:
        fi.run = real
    check("--dry-run не делает ни одного вызова наружу", not [человек]["called"])
    check("--dry-run возвращает 0", code == 0)

    # несуществующий файл -> честный выход 2, а не тихий успех
    code = fi.main(["--id", "t", "--file", "/nope/missing.py", "--apply", "x", "--verify", "y"])
    check("нет файла -> exit 2", code == 2)

    # плейсхолдеры разворачиваются в командах
    tmpl = "{py} {f} --install && {py} {dir}/deploy_apply.py id"
    got = tmpl.replace("{f}", "proc_patrol.py").replace("{py}", "python3").replace("{dir}", "/x")
    check("плейсхолдеры {f}/{py}/{dir} разворачиваются",
          "proc_patrol.py" in got and "python3" in got and "/x/deploy_apply.py" in got)

    os.unlink(p)
    print("\n%d/%d passed" % (N[0] - len(FAILS), N[0]))
    return 1 if FAILS else 0


if __name__ == "__main__":
    sys.exit(run())
