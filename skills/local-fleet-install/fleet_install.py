# -*- coding: utf-8 -*-
"""fleet_install.py -- доставить деталь на КАЖДЫЙ узел флота и доказать применение фактом.

Приказ Антона 29.07: «разослали всем "почините у себя" и решили, что дело сделано. Никто не
починил». Этот движок существует, чтобы слова «раскатал» больше нельзя было сказать без таблицы.

ЧТО ДЕЛАЕТ на каждом достижимом узле, по порядку:
  1. КОПИРУЕТ файлы (scp), сверяет md5 источника и приёмника -- доставка доказана хэшем;
  2. ПРОГОНЯЕТ тест, если он передан (--test) -- красный тест = узел не считается применённым;
  3. APPLY -- команда установки (обычно `<деталь> --install`);
  4. VERIFY -- машинная проверка (exit 0), проза не принимается;
  5. РЕГИСТРИРУЕТ применение (`deploy_apply.py <id>`), чтобы табло паритета увидело факт.
Недостижимые узлы НЕ замалчиваются: кладёт посылку в `_transit`, шлёт TASK по шине и пишет их
поимённо в отчёт как ОТСТАВШИХ. Тишина узла никогда не считается успехом.

⛔ ЧЕГО НЕ ДЕЛАЕТ: не трогает receive-only канон-шары на чужих узлах молча (файл кладётся туда,
куда указал вызывающий), не решает за Tier-2, не публикует наружу.

Usage:
  python3 fleet_install.py --id <deploy-id> --file <path> [--file <path2>]
                           --apply "<cmd>" --verify "<cmd>" [--test "<cmd>"]
                           [--dest-posix DIR] [--dest-win DIR] [--only NODE,NODE] [--dry-run]

Пути назначения по умолчанию: POSIX `~/.claude/scripts/`, Windows `[путь владельца]`.
`{f}` в командах разворачивается в имя первого файла без пути.

Exit: 0 = применено на ВСЕХ достижимых · 1 = есть отставшие (норма, если узлы офлайн) · 2 = ни один
узел не применил · 4 = сам упал (crash-guard).

Паспорт починки: один файл, stdlib + ssh/scp. Диагноз узла руками:
  ssh <узел> "<verify>"; echo $?    -- 0 значит деталь живёт.
"""
import os, sys, json, socket, argparse, subprocess, hashlib

HOME = os.path.expanduser("~")
SCRIPTS = os.path.join(HOME, ".claude", "scripts")
REGISTRY = os.path.join(HOME, ".claude", "fleet_nodes.json")
TRANSIT_CANDIDATES = [
    os.path.join(HOME, "Obsidian", "Anton-Knowledge", "[шина]", "_transit"),
    os.path.join(os.environ.get("OBSIDIAN_VAULT", ""), "[шина]", "_transit"),
]


def md5(path):
    h = hashlib.md5()
    with open(path, "rb") as fh:
        for chunk in iter(lambda: fh.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()


def run(cmd, timeout=180):
    r = subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8",
                       errors="replace", timeout=timeout)
    return r.returncode, (r.stdout or "") + (r.stderr or "")


def this_node():
    raw = (os.environ.get("MACHINE_KEY") or socket.gethostname() or "").split(".")[0]
    for key, v in load_nodes().items():
        names = {key.upper(), str(v.get("hostname", "")).upper(), str(v.get("code", "")).upper()}
        names |= {str(a).upper() for a in v.get("aliases", [])}
        if raw.upper() in names:
            return key
    return raw


def load_nodes():
    try:
        with open(REGISTRY, encoding="utf-8") as fh:
            return json.load(fh).get("nodes", {})
    except Exception:
        return {}


def reachable(node, info):
    """ssh-достижимость. Возвращает (ok, ssh_target). Пробуем алиас, потом tailnet-IP."""
    for target in (str(info.get("code", "")).lower(), node.lower(),
                   str(info.get("hostname", "")), info.get("tailnet_ip") or ""):
        if not target:
            continue
        code, _ = run(["ssh", "-o", "ConnectTimeout=8", "-o", "BatchMode=yes",
                       target, "echo ok"], timeout=25)
        if code == 0:
            return True, target
    return False, None


def remote_is_windows(target):
    code, out = run(["ssh", "-o", "ConnectTimeout=8", target, "echo $env:OS"], timeout=25)
    return "Windows" in out


def install_on(node, target, files, args):
    """Вернуть (статус, строка-доказательство). Статус: applied|test_failed|verify_failed|error."""
    win = remote_is_windows(target)
    dest = (args.dest_win or "[путь владельца]") if win else \
           (args.dest_posix or "~/.claude/scripts/")
    proof = []

    # 1. доставка + сверка хэшем
    for f in files:
        code, out = run(["scp", "-o", "ConnectTimeout=15", f, "%s:%s" % (target, dest)], timeout=300)
        if code != 0:
            return "error", "scp упал: " + out.strip()[:120]
    base = os.path.basename(files[0])
    if win:
        cmd = ("(Get-FileHash '%s%s' -Algorithm MD5).Hash.ToLower()" % (dest, base))
    else:
        cmd = ("(md5 -q %s%s 2>/dev/null || md5sum %s%s | cut -d' ' -f1)" % (dest, base, dest, base))
    code, out = run(["ssh", target, cmd], timeout=60)
    # ssh печатает свои баннеры в тот же поток -- берём строку, которая ЯВЛЯЕТСЯ хэшем,
    # а не последнюю попавшуюся (замер 29.07: на хабе в сравнение уехало "** The s")
    want = md5(files[0])
    got = ""
    for ln in out.splitlines():
        cand = ln.strip().lower()
        if len(cand) == 32 and all(c in "[id]abcdef" for c in cand):
            got = cand
            break
    if got != want:
        return "error", ("md5 разошёлся: у нас %s, там %s" % (want[:8], got[:8] or "хэш не найден")
                         + (" | " + out.strip().replace("\n", " ")[-70:] if not got else ""))
    proof.append("md5 " + want[:8])

    py = "python" if win else "python3"
    workdir = dest.rstrip("/")

    def rcmd(template):
        c = template.replace("{f}", base).replace("{py}", py).replace("{dir}", workdir)
        return ["ssh", target, ("cd %s; %s" % (workdir, c)) if not win
                else ("cd '%s'; %s; exit $LASTEXITCODE" % (workdir, c))]

    # 2. тест (если задан) -- красный тест останавливает узел
    if args.test:
        code, out = run(rcmd(args.test), timeout=600)
        lines = [l.strip() for l in out.splitlines() if l.strip()]
        # ssh-баннеры лезут в тот же поток -- ищем строку с итогом теста, иначе последнюю
        tail = next((l for l in reversed(lines) if "passed" in l or "PASS" in l or "FAIL" in l),
                    lines[-1] if lines else "")[:60]
        if code != 0:
            return "test_failed", "тест красный: " + tail
        proof.append("тест " + tail)

    # 3. apply
    code, out = run(rcmd(args.apply), timeout=600)
    if code != 0:
        return "error", "apply exit=%d %s" % (code, out.strip()[-100:])

    # 4. verify -- машинная, exit 0
    code, out = run(rcmd(args.verify), timeout=300)
    if code != 0:
        return "verify_failed", "verify exit=%d %s" % (code, out.strip()[-80:])
    proof.append("verify exit 0")

    # 5. регистрация факта
    code, out = run(rcmd("%s %s/deploy_apply.py %s" % (py, workdir, args.id)), timeout=300)
    proof.append("deploy_apply " + ("ok" if code == 0 else "НЕ записан"))
    return "applied", " · ".join(proof)


def drop_parcel(files, args, laggards):
    """Посылка + TASK по шине для тех, до кого не достучались."""
    transit = next((t for t in TRANSIT_CANDIDATES if t and os.path.isdir(t)), None)
    if not transit:
        return "транзит не найден -- посылка НЕ положена"
    for f in files:
        try:
            import shutil
            shutil.copy2(f, os.path.join(transit, "DEPLOY-" + os.path.basename(f)))
        except Exception as e:
            return "копия в транзит не удалась: %r" % e
    msg = ("TASK: %s -- установить на своём узле. Файлы в _transit/DEPLOY-%s. "
           "Установка: скопировать в ~/.claude/scripts/ затем `%s`, доказать `%s`, "
           "затем `deploy_apply.py %s`. ОТСТАЮТ: %s"
           % (args.id, os.path.basename(files[0]),
              args.apply.replace("{f}", os.path.basename(files[0])),
              args.verify.replace("{f}", os.path.basename(files[0])),
              args.id, ", ".join(laggards)))
    code, _ = run([sys.executable, os.path.join(SCRIPTS, "bus_send.py"), "ALL", msg], timeout=180)
    return "посылка в транзите + TASK по шине " + ("доставлен" if code == 0 else "НЕ УШЁЛ")


def main(argv):
    ap = argparse.ArgumentParser()
    ap.add_argument("--id", required=True)
    ap.add_argument("--file", action="append", required=True)
    ap.add_argument("--apply", required=True)
    ap.add_argument("--verify", required=True)
    ap.add_argument("--test")
    ap.add_argument("--dest-posix")
    ap.add_argument("--dest-win")
    ap.add_argument("--only")
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args(argv)

    files = [os.path.abspath(os.path.expanduser(f)) for f in args.file]
    for f in files:
        if not os.path.exists(f):
            print("НЕТ ФАЙЛА: " + f)
            return 2

    nodes = load_nodes()
    me = this_node()
    only = {x.strip().upper() for x in args.only.split(",")} if args.only else None
    targets = {k: v for k, v in nodes.items()
               if k != me and (not only or k.upper() in only)}

    print("деталь: %s (md5 %s)" % (", ".join(os.path.basename(f) for f in files), md5(files[0])[:8]))
    print("этот узел: %s · целей: %d\n" % (me, len(targets)))
    if args.dry_run:
        for k in targets:
            print("  DRY -> " + k)
        return 0

    results = {}
    for node, info in sorted(targets.items()):
        ok, target = reachable(node, info)
        if not ok:
            results[node] = ("unreachable", "офлайн (ssh не отвечает)")
            print("  %-18s ⏳ офлайн" % node)
            continue
        status, proof = install_on(node, target, files, args)
        results[node] = (status, proof)
        icon = {"applied": "✅", "test_failed": "❌", "verify_failed": "❌"}.get(status, "⚠️")
        print("  %-18s %s %s" % (node, icon, proof))

    laggards = [n for n, (s, _) in results.items() if s != "applied"]
    print()
    if laggards:
        print("ОТСТАЮТ (%d): %s" % (len(laggards), ", ".join(laggards)))
        print("  " + drop_parcel(files, args, laggards))
    applied = [n for n, (s, _) in results.items() if s == "applied"]
    print("\nИТОГО: применено %d из %d достижимых+недостижимых целей (+ этот узел отдельно)"
          % (len(applied), len(targets)))
    if not applied and targets:
        return 2
    return 1 if laggards else 0


if __name__ == "__main__":
    try:
        sys.exit(main(sys.argv[1:]))
    except SystemExit:
        raise
    except BaseException as e:
        print("CRASH: %r" % e)
        sys.exit(4)
