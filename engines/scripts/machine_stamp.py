#!/usr/bin/env python3
"""machine_stamp.py -- ОДНА форма метки «с какой машины это написано».

ПРИКАЗ (anton, голосом, 08.10.2026): «Если агент в Mycroft, Codex, Cursor, Grok
или любом другом инструменте что-то пишет, он всегда должен добавлять: с какой
машины это написано.»

ЗАЧЕМ ПРИБОР, А НЕ ПРОЗА В КАНОНЕ. Урок change_ledger (23.08.2026): правило,
описанное прозой, расползается тем БЫСТРЕЕ, чем лучше его соблюдают -- за сутки
пять честных исполнителей дали 17 строк в 3 диалектах, и журнал «кто это сделал»
перестал отвечать на свой же вопрос. Поэтому метку НЕ СОЧИНЯЮТ: прибор печатает
готовую строку (`line`), исполнитель её вставляет (`apply`), сторож читает факт
(`lint`). Правило кросс-вендорное, поэтому дверь -- shell-скрипт, одинаково
доступный Claude Code, Codex, Cursor, Grok и любому следующему агенту
(канон: «скиллы и двери пишем для ЛЮБОГО агента»).

КАНОНИЧНАЯ ФОРМА (ревью Codex 08.10.2026 = REVISE: не изобретать новый ключ):
    Machine: [машина флота] (Хаб) · Agent: Codex · Operator: Anton · 2026-10-08
Ключ `Machine:` УЖЕ живёт в git-трейлерах, в поле `machine` у change_ledger и в
frontmatter заметок волта. Это ОДИН контракт данных с разными способами
размещения, а не пятый диалект. Первая редакция этого прибора ввела собственный
`written-on:` и была отменена тем же заходом: изобретённый ключ есть ровно та
болезнь, от которой прибор лечит.

Значение берётся СТРОГО из реестра флота (канонический ключ узла), потому что
живой замер Codex на хабе дал `hostname` = `[машина флота]`, а реестр знает
`[машина флота]`: без нормализации два написания одного узла = два диалекта.
Там же вторая улика: `$env:COMPUTERNAME` у его shell оказался ПУСТ, поэтому
лестница определения узла не имеет права упираться в одну переменную.

ЧТО СЧИТАЕТСЯ «НАПИСАЛ» -- артефакт, который можно прочитать ВНЕ живого контекста
сессии: файл, заметка, отчёт, план, черновик, сообщение в шину, коммент, строка в
леджере. Живой диалог в сессии меткой УЖЕ покрыт: первая буква номера сессии
(`H20053`) = машина, её ставит SessionStart-хук.

⛔ ГРАНИЦА (не сужение приказа, а защита от утечки инфраструктуры): в ТЕЛО
исходящего наружу -- письмо лиду, пост, коммент в чужом репозитории -- метка НЕ
идёт; имена наших узлов посторонним не нужны. Там провенанс живёт в НАШЕЙ копии
черновика и в журнале. Решает `--outbound` у `lint`: такие файлы уходят в
«не могу судить» с причиной, а не в нарушения.

⛔ МЕТКА, КОТОРАЯ ВРЁТ, ХУЖЕ ОТСУТСТВУЮЩЕЙ. Поэтому: (1) машину подставляет сам
прибор из реального hostname, руками её не пишут; (2) `lint` проверяет, что
названный узел ВООБЩЕ СУЩЕСТВУЕТ в реестре флота, и валит выдуманные имена;
(3) `unknown`/пусто -- нарушение, а не «ну хоть что-то».

⛔ МЕТКА = КТО ЗАПИСАЛ, НЕ КТО ПРИДУМАЛ (память attribution-trace-lineage-not-machine-tag,
грабли 10.07.2026: манифест приписали Маку [коллега] по machine-тегу, а придумал его
хаб). Прежде чем сказать «это делала машина X», пройди цепочку related/sources до
корневого решения и назови ОБА: идея = Y, запись = X.

Соседи, которых этот прибор НЕ подменяет:
  * git-коммиты с кодом -> 4 трейлера + `code_provenance_lint.py`;
  * правки вне git (n8n/SQLite/конфиги) -> `change_ledger.py add`;
  * заметки сессий в волте -> `machine:` ставит импортёр.
Этот прибор закрывает то, что не покрыл никто: ТЕКСТОВЫЙ артефакт любого вендора.
"""

from __future__ import annotations

import argparse
import datetime as _dt
import os
import platform
import re
import socket
import sys
from pathlib import Path

_SCRIPTS_DIR = Path(__file__).resolve().parent
if str(_SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(_SCRIPTS_DIR))

# Канон: сосед ищется от realpath(__file__), а не от ~ (правило §5.5).
try:
    import fleet_nodes as _fleet
except Exception:  # pragma: no cover - реестр недоступен
    _fleet = None

# Канон-ключ `Machine:`. Написание `written[-_]on` читается ТОЛЬКО как наследие
# первой редакции этого прибора (08.10.2026, отменена ревью Codex) -- чтобы уже
# проштампованное не читалось как нарушение. Новое пишется всегда `Machine:`.
MARKER_RE = re.compile(
    r"^[\s#>*<!-]*(?:Machine|written[-_]on)\s*:", re.IGNORECASE | re.MULTILINE
)
# ⚠️ MULTILINE обязателен. Без него `$` совпадает только в конце ВСЕГО текста, и
# метка, лежащая полем frontmatter в середине файла, извлекалась с ПУСТЫМ именем
# узла -- то есть законная метка объявлялась врущей. Живой прогон 08.10 поймал
# это на 4 реальных артефактах; ложноположительный вердикт хуже пропуска.
STAMP_RE = re.compile(
    r"(?:Machine|written[-_]on)\s*:\s*\"?(?P<machine>[^·\n\"(]+?)\s*(?:\(|·|\"|$)",
    re.IGNORECASE | re.MULTILINE,
)

# Расширения, которые вообще имеет смысл судить.
TEXT_SUFFIXES = {".md", ".txt", ".html", ".json", ".jsonl", ".csv", ".yml", ".yaml"}


def host() -> str:
    """Реальное имя узла. Лестница та же, что у change_ledger._host()."""
    for src in (os.environ.get("COMPUTERNAME"), os.environ.get("MACHINE_KEY"),
                platform.node(), socket.gethostname()):
        if src and src.strip():
            return src.strip().split(".")[0]
    raise RuntimeError("machine hostname is unavailable")


def friendly_of(hostname: str) -> str:
    """Понятное имя узла из реестра; нет реестра -> сам hostname."""
    if _fleet is None:
        return hostname
    try:
        name = _fleet.friendly(hostname)
        return name or hostname
    except Exception:
        return hostname


def canonical_key(hostname: str) -> tuple[str, bool]:
    """Канонический ключ узла из реестра + резолвился ли он.

    Нормализация обязательна: замер Codex 08.10 дал `hostname` = `[машина флота]`
    при реестровом `[машина флота]`. Без неё один узел печатался бы двумя
    написаниями, и метка перестала бы быть машиночитаемой.

    Не резолвится -> отдаём сырое имя и ЧЕСТНЫЙ флаг False: прибор не выдумывает
    принадлежность узла (возражение Codex про веб-двери и удалённые инструменты).
    """
    if _fleet is None:
        return hostname, False
    try:
        key = _fleet.key_of(hostname)
        if key:
            return key, True
    except Exception:
        pass
    return hostname, False


def known_node(name: str) -> bool:
    """Существует ли такой узел в реестре флота. Защита от ВРУЩЕЙ метки."""
    if _fleet is None:
        return True  # не можем судить -> не клевещем
    probe = name.strip().strip("()").split("(")[0].strip()
    for cand in (probe, probe.upper(), probe.lower()):
        try:
            if _fleet.key_of(cand):
                return True
        except Exception:
            pass
    # ⚠️ all_nodes() отдаёт DICT (ключ -> узел). Первая редакция итерировала его
    # напрямую, получала строки-ключи, падала на str.get() и уходила в `except:
    # return True` -- то есть ЛЮБОЕ выдуманное имя узла признавалось законным.
    # Сторож поймал это сразу (проверка «lint назвал выдуманный узел врущей»).
    try:
        raw = _fleet.all_nodes()
        nodes = list(raw.values()) if isinstance(raw, dict) else list(raw)
        keys = list(raw.keys()) if isinstance(raw, dict) else []
        for k in keys:
            if str(k).strip().lower() == probe.lower():
                return True
        for node in nodes:
            if not isinstance(node, dict):
                continue
            vals = [str(node.get(f, "")) for f in ("code", "friendly", "hostname")]
            vals += [str(a) for a in (node.get("aliases") or [])]
            if any(v and v.strip().lower() == probe.lower() for v in vals):
                return True
    except Exception:
        # Не смогли опросить реестр -> не клевещем, но и не молчим: это «не могу
        # судить», и lint обязан напечатать его в строке покрытия.
        return True
    return False


def detect_agent() -> str:
    """Какой агент пишет. Угадываем по env; не смогли -> зовём назвать явно."""
    env = os.environ
    if env.get("CLAUDECODE") or env.get("CLAUDE_CODE_SESSION_ID"):
        return "Claude Code"
    if any(k.startswith("CODEX_") for k in env):
        return "Codex"
    if env.get("CURSOR_TRACE_ID") or any(k.startswith("CURSOR_") for k in env):
        return "Cursor"
    if any(k.startswith("GROK_") for k in env):
        return "Grok"
    return ""


def detect_operator() -> str:
    """Человек за рулём. Реестр узла -> env -> пусто (не угадываем по косвенным)."""
    op = os.environ.get("CLAUDE_OPERATOR") or os.environ.get("OPERATOR")
    if op and op.strip():
        return op.strip()
    if _fleet is not None:
        try:
            node = _fleet.node(host())
            owner = (node or {}).get("owner")
            if owner and str(owner).strip():
                return str(owner).strip()
        except Exception:
            pass
    return ""


def build_line(agent: str = "", operator: str = "", day: str = "",
               prefix: str = "") -> str:
    """Готовая каноничная строка метки. Её ВСТАВЛЯЮТ, а не пересказывают."""
    key, resolved = canonical_key(host())
    nice = friendly_of(key)
    machine = f"{key} ({nice})" if resolved and nice and nice != key else key
    if not resolved:
        # Честнее сказать «узла нет в реестре», чем выдать выдуманную принадлежность.
        machine = f"{key} (узла нет в реестре флота)"
    agent = (agent or detect_agent()).strip()
    if not agent:
        raise SystemExit(
            "⛔ не знаю, какой агент пишет: назови явно `--agent \"Codex\"`.\n"
            "   Угадывать нельзя: метка, которая врёт, хуже отсутствующей."
        )
    parts = [f"Machine: {machine}", f"Agent: {agent}"]
    operator = (operator or detect_operator()).strip()
    if operator:
        parts.append(f"Operator: {operator}")
    parts.append(day or _dt.date.today().isoformat())
    return f"{prefix}{' · '.join(parts)}"


def has_stamp(text: str) -> bool:
    return bool(MARKER_RE.search(text))


def stamped_machine(text: str) -> str:
    m = STAMP_RE.search(text)
    return (m.group("machine").strip() if m else "")


def _frontmatter_bounds(lines: list[str]) -> tuple[int, int] | None:
    """Границы YAML-frontmatter, если он есть: (первая ---, закрывающая ---)."""
    if not lines or lines[0].strip() != "---":
        return None
    for i in range(1, len(lines)):
        if lines[i].strip() in ("---", "..."):
            return (0, i)
    return None


def same_node(named: str) -> bool:
    """Названный в метке узел -- это узел, на котором мы прямо сейчас?"""
    probe = (named or "").strip().strip('"').split("(")[0].strip()
    if not probe:
        return False
    here, _ = canonical_key(host())
    there, _ = canonical_key(probe)
    return there.strip().lower() == here.strip().lower()


def apply_stamp(path: Path, agent: str = "", operator: str = "",
                day: str = "", dry: bool = False, force: bool = False) -> str:
    """Вставить метку в артефакт. Идемпотентно: вторая метка не плодится.

    ⛔ ЧУЖАЯ МЕТКА НЕ ПРОХОДИТ МОЛЧА (дыра, найденная ревью Codex 08.10.2026):
    самый простой способ заставить метку врать -- скопировать хабовый шаблон на
    другой узел, поменять текст и сохранить СТАРУЮ подпись. Первая редакция в этом
    случае отвечала «already» и оставляла курьера автором. Теперь такой файл
    получает вердикт `foreign`, а перештамповку делает только явный `--force`.
    """
    text = path.read_text(encoding="utf-8", errors="replace")
    if has_stamp(text):
        named = stamped_machine(text)
        if named and not same_node(named):
            if not force:
                return f"foreign({named.strip()})"
            if not dry:
                line = build_line(agent, operator, day)
                # ⚠️ Внутри frontmatter ключ обязан остаться в НИЖНЕМ регистре:
                # для YAML `Machine` и `machine` -- разные ключи, а парсеры волта
                # и импортёр заметок читают именно `machine`. Перештамповка с
                # большой буквы тихо осиротила бы поле.
                lines_all = text.splitlines()
                fm = _frontmatter_bounds(lines_all)
                in_fm = False
                if fm is not None:
                    head = "\n".join(lines_all[: fm[1] + 1])
                    in_fm = bool(MARKER_RE.search(head))
                if in_fm:
                    # ⚠️ Значение ОБЯЗАНО быть в кавычках: внутри него двоеточия
                    # («Agent: Claude Code»), и без кавычек YAML падает с
                    # ScannerError «mapping values are not allowed here». Живой
                    # прогон 08.10 поймал это на первом же перештампованном
                    # артефакте: прибор, портящий frontmatter, хуже отсутствия метки.
                    repl = 'machine: "' + line.replace("Machine: ", "", 1) + '"'
                else:
                    repl = line
                new = re.sub(
                    r"(?:Machine|written[-_]on)\s*:[^\n]*",
                    repl.replace("\\", "\\\\"),
                    text,
                    count=1,
                    flags=re.IGNORECASE,
                )
                path.write_text(new, encoding="utf-8")
            return "restamped"
        return "already"

    lines = text.splitlines()
    bounds = _frontmatter_bounds(lines)
    if bounds is not None:
        # В артефакте с frontmatter метка живёт полем `machine` -- тем же, что уже
        # ставит импортёр заметок волта. Один контракт, разные места размещения.
        line = build_line(agent, operator, day)
        field = line.replace("Machine: ", "", 1)
        _, close = bounds
        lines.insert(close, f'machine: "{field}"')
        new = "\n".join(lines) + ("\n" if text.endswith("\n") else "")
    else:
        comment = path.suffix.lower() in {".md", ".html"}
        line = build_line(agent, operator, day)
        body = f"<!-- {line} -->" if comment else f"# {line}"
        sep = "" if text.endswith("\n") else "\n"
        new = f"{text}{sep}\n{body}\n"

    if dry:
        return "would-stamp"
    path.write_text(new, encoding="utf-8")
    return "stamped"


def _iter_targets(paths: list[str]) -> list[Path]:
    out: list[Path] = []
    for raw in paths:
        p = Path(raw)
        if p.is_dir():
            for f in sorted(p.rglob("*")):
                if f.is_file() and f.suffix.lower() in TEXT_SUFFIXES:
                    out.append(f)
        elif p.is_file():
            out.append(p)
    return out


def cmd_lint(args: argparse.Namespace) -> int:
    """Читает ФАКТ. Печатает покрытие -- прибор не имеет права быть слепым."""
    targets = _iter_targets(args.paths)
    if not targets:
        print("⛔ нечего судить: ни одного файла по заданным путям")
        return 1

    outbound = {Path(p).resolve() for p in (args.outbound or [])}
    ok: list[Path] = []
    missing: list[Path] = []
    lying: list[tuple[Path, str]] = []
    unjudged: list[tuple[Path, str]] = []

    for f in targets:
        if f.resolve() in outbound:
            unjudged.append((f, "исходящее наружу: метка в теле запрещена"))
            continue
        try:
            text = f.read_text(encoding="utf-8", errors="replace")
        except Exception as e:
            unjudged.append((f, f"не прочёл: {e}"))
            continue
        if not text.strip():
            unjudged.append((f, "файл пустой"))
            continue
        if not has_stamp(text):
            missing.append(f)
            continue
        named = stamped_machine(text)
        if not named or named.strip().lower() in {"unknown", "none", "null", "-", "n/a"}:
            lying.append((f, f"имя узла пустое/{named.strip() or 'пусто'}"))
        elif not known_node(named):
            lying.append((f, f"узла «{named.strip()}» нет в реестре флота"))
        elif args.expect_here and not same_node(named):
            # Локально рождённый артефакт с меткой ЧУЖОГО узла = след копирования
            # шаблона (дыра из ревью Codex): курьер записан автором.
            lying.append((f, f"метка чужого узла «{named.strip()}», а правили здесь"))
        else:
            ok.append(f)

    total = len(targets)
    judged = len(ok) + len(missing) + len(lying)
    print(f"метка машины: ✅ {len(ok)} · ⛔ нет {len(missing)} · 🤥 врёт {len(lying)}")
    print(f"не могу судить {len(unjudged)} из {total}"
          + (f" (причины: {', '.join(sorted({r for _, r in unjudged}))})" if unjudged else ""))

    if judged and (judged / total) < 0.9:
        print(f"⚠️ покрытие {judged}/{total} < 90% -- прибор полуслепой на этом наборе")

    # Честная граница прибора (ревью Codex 08.10): допустимое имя узла НЕ
    # доказывает происхождение текста. Скопированный шаблон с чужой подписью
    # ловится только флагом --expect-here, а подмену окружения писателя и
    # присвоение чужого текста импортёром этот сторож не видит в принципе.
    print("🔍 имя узла из реестра НЕ доказывает происхождение: копию шаблона с "
          "чужой подписью ловит только --expect-here"
          + ("" if args.expect_here else " (сейчас ВЫКЛЮЧЕН)"))

    for f, why in lying:
        print(f"  🤥 {f}: {why}")
    if args.verbose:
        for f in missing:
            print(f"  ⛔ {f}")

    if lying:
        return 1
    if missing and not args.allow_missing:
        return 1
    return 0


# --- ВИДИМАЯ ПОДПИСЬ СООБЩЕНИЯ (приказ anton 12.10.2026, голосом) -----------------
# «Каждый раз, когда флот кому-то что-то пишет, снаружи или внутри, должна быть
# подпись, видная человеческому глазу: иконка машины, буква, модель, номер сессии.»
# Зачем: в WhatsApp пишет «кто-то», а на какой машине он крутится и чьи лимиты
# сгорают, не видно. Криптоподпись (fleet_sign) остаётся отдельно, это для глаза.
# Форма: `🏛H · Fable 5.1 · 56901`  (иконка+буква узла · модель · цифры сессии;
# цифры диктуются как «сессия 56901», `session_code.py find 56901`).
NODE_ICONS = {  # буква из fleet_nodes.json -> иконка
    "H": "\U0001F3DB",         # хаб
    "Z": "\U0001F4BC",         # [машина флота]
    "A": "\U0001F34E",         # [машина флота]
    "M": "\U0001F5FC",         # Маяк
    "N": "\U0001F338",         # ноут [коллега]
    "R": "\U0001F98B",         # MacBook [коллега]
    "P": "\U0001F5A5\uFE0F",  # MacPro
    "E": "\u270F\uFE0F",      # ноут [коллега]
}


def node_letter(key: str) -> str:
    """Буква узла из реестра; нет в реестре -> '?' (видно, не выдумываем)."""
    if _fleet is not None:
        try:
            node = _fleet.node(key) or {}
            lt = str(node.get("letter") or "").strip().upper()
            if len(lt) == 1 and lt.isalpha():
                return lt
        except Exception:
            pass
    return "?"


def detect_model() -> str:
    """Модель: явные env, иначе алиас из settings.json с тильдой (= догадка, видно)."""
    for var in ("FLEET_MODEL", "ANTHROPIC_MODEL", "CLAUDE_MODEL"):
        v = os.environ.get(var, "").strip()
        if v:
            return v
    try:
        import json
        st = json.loads((Path.home() / ".claude" / "settings.json").read_text("utf-8"))
        v = str(st.get("model") or "").strip()
        if v:
            return "~" + v
    except Exception:
        pass
    return "?"


def detect_session() -> str:
    """Цифры короткого номера сессии: env CLAUDE_CODE_SESSION_ID -> session_code."""
    sid = os.environ.get("CLAUDE_CODE_SESSION_ID", "").strip()
    if not sid:
        return "?"
    try:
        import session_code as _sc
        row = _sc.code_of(sid)
        code = (row or {}).get("code") or ""
    except Exception:
        code = ""
    digits = re.sub(r"\D", "", code)
    return digits or "?"


def build_sig(model: str = "", session: str = "") -> str:
    key, resolved = canonical_key(host())
    lt = node_letter(key) if resolved else "?"
    icon = NODE_ICONS.get(lt, "\u2753")
    model = (model or detect_model()).strip()
    session = re.sub(r"\D", "", session) if session else detect_session()
    if not session or session == "?":
        # \u0431\u0435\u0437\u043b\u044e\u0434\u043d\u044b\u0439 \u0441\u043a\u0440\u0438\u043f\u0442 (\u0434\u0440\u0438\u043f, \u0440\u0443\u0442\u0438\u043d\u0430): \u0441\u0435\u0441\u0441\u0438\u0438 \u043d\u0435\u0442, \u0438 \u044d\u0442\u043e \u043f\u0440\u0430\u0432\u0434\u0430, \u0430 \u043d\u0435 "?"
        if model in ("", "?"):
            return f"{icon}{lt} \u00b7 robot"
        return f"{icon}{lt} \u00b7 {model}"
    return f"{icon}{lt} \u00b7 {model} \u00b7 {session}"


def cmd_sig(args: argparse.Namespace) -> int:
    print(build_sig(args.model, args.session))
    return 0


def cmd_line(args: argparse.Namespace) -> int:
    print(build_line(args.agent, args.operator, args.day, args.prefix))
    return 0


def cmd_apply(args: argparse.Namespace) -> int:
    rc = 0
    for f in _iter_targets(args.paths):
        try:
            verdict = apply_stamp(f, args.agent, args.operator, args.day,
                                  args.dry_run, args.force)
        except SystemExit:
            raise
        except Exception as e:
            print(f"⛔ {f}: {e}")
            rc = 1
            continue
        print(f"{verdict:24} {f}")
        if verdict.startswith("foreign"):
            # Молчать нельзя: это и есть случай «курьер записан автором».
            print("   🤥 метка ЧУЖОГО узла. Правил этот текст здесь -> "
                  "перештампуй явно: --force")
            rc = 1
    return rc


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(
        description="ОДНА форма метки «с какой машины это написано» (приказ anton 08.10.2026)"
    )
    sub = ap.add_subparsers(dest="cmd", required=True)

    common = dict(agent="", operator="", day="")
    pl = sub.add_parser("line", help="печатает готовую строку метки -- вставляй её, не сочиняй")
    pl.add_argument("--agent", default=common["agent"], help='кто пишет: "Codex", "Cursor", "Grok"')
    pl.add_argument("--operator", default=common["operator"])
    pl.add_argument("--day", default=common["day"], help="дата YYYY-MM-DD (по умолчанию сегодня)")
    pl.add_argument("--prefix", default="", help='напр. "<!-- " не нужен: apply сам обернёт')
    pl.set_defaults(func=cmd_line)

    pg = sub.add_parser("sig", help="видимая подпись сообщения: иконка+буква узла, модель, номер сессии")
    pg.add_argument("--model", default="", help='"Fable 5.1", "Codex GPT-5.5", "Grok 4"; не задана -> env или ~алиас')
    pg.add_argument("--session", default="", help="цифры номера сессии; не задан -> из CLAUDE_CODE_SESSION_ID")
    pg.set_defaults(func=cmd_sig)

    pa = sub.add_parser("apply", help="вставить метку в файл/папку (идемпотентно)")
    pa.add_argument("paths", nargs="+")
    pa.add_argument("--agent", default=common["agent"])
    pa.add_argument("--operator", default=common["operator"])
    pa.add_argument("--day", default=common["day"])
    pa.add_argument("--dry-run", action="store_true")
    pa.add_argument("--force", action="store_true",
                    help="перештамповать артефакт с меткой ЧУЖОГО узла (копия шаблона)")
    pa.set_defaults(func=cmd_apply)

    ll = sub.add_parser("lint", help="читает факт: есть ли метка и не врёт ли она")
    ll.add_argument("paths", nargs="+")
    ll.add_argument("--outbound", nargs="*", default=[],
                    help="файлы, уезжающие НАРУЖУ: метка в теле запрещена, судить нельзя")
    ll.add_argument("--allow-missing", action="store_true",
                    help="отсутствие метки не валит (для замера, не для гейта)")
    ll.add_argument("--expect-here", action="store_true",
                    help="артефакты рождены на ЭТОМ узле: метка чужого узла = след копирования")
    ll.add_argument("-v", "--verbose", action="store_true")
    ll.set_defaults(func=cmd_lint)

    args = ap.parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())
