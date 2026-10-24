#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""СЧЁТЧИК ИСПОЛЬЗОВАНИЯ СКИЛЛОВ -- кто из пиров какой скилл зовёт и сколько раз.

ЗАЧЕМ (приказ anton 04.08.2026). «Добавить счётчик использования для КАЖДОГО СКИЛЛА по
использованию его КАЖДЫМ ПИРОМ, и сколько РАЗ -- так проще следить за используемостью и
причинением пользы каждым скиллом.» Прямое приложение §5.8 (счётчик = третий обязательный
атрибут детали после теста и дока) к самому многочисленному классу деталей: скиллов 136,
и до сегодня мы НЕ знали, сколько из них живые.

Класс уже стоил нам разов: `/release-slice` существовал 32 дня, был сломан непортируемым
путём и не запускался ни с одного узла кроме хаба -- никто не заметил, потому что «скилл
есть» и «скиллом пользуются» никто не различал (память ship-skill-was-windows-only).
Соседи по слепоте: 107/346 чипов не нажаты, 218 ДР в synthesized, 70 капч в воронке.

ЧТО СЧИТАЕМ. Одну строку на КАЖДЫЙ вызов скилла:
  {ts, machine, actor, skill, args_len, outcome, source}
  actor    : оператор узла (кто за рулём), из CLAUDE_OPERATOR/реестра, иначе "unknown"
  outcome  : ok | fail   (fail = харнес вернул ошибку на вызове скилла)
  source   : hook | manual   (hook = автоматом из PostToolUse, manual = позвали log() сами)

ГДЕ ЛЕЖИТ. Пер-машинный шард в шине -> флот агрегируется без общего писателя:
  $MACHINE_BUS_DIR/_metrics/skill-usage/<machine>.jsonl
Один писатель на файл = свой узел, поэтому sync-conflict невозможен по построению
(класс two-channels-one-file-race). Шины нет -> локальный запас
~/.claude/_metrics/skill-usage/<machine>.jsonl, отчёт читает ОБА корня.

КТО ПИШЕТ. hooks/skill_usage_hook.py (PostToolUse на туле Skill) -- автоматически, на
каждом узле. Ручная запись не выживает, поэтому её и не предполагаем.

КАК ЧИТАТЬ:
  python3 ~/.claude/scripts/_shared/skill_usage_log.py --report
  python3 ~/.claude/scripts/_shared/skill_usage_log.py --report --days 30 --by-node
  python3 ~/.claude/scripts/_shared/skill_usage_log.py --report --dead   # 0 вызовов
  python3 ~/.claude/scripts/_shared/skill_usage_log.py --report --json

ЧТО ЛОМАЕТСЯ И КАК ПОНЯТЬ. Молчание счётчика != «скиллами не пользовались»: сперва
`--report --raw` -- есть ли вообще файлы шардов и с каких узлов. Узел без хука пишет
ноль и выглядит как узел без работы; список узлов-писателей печатается в отчёте именно
поэтому (класс blind-watchdog-must-not-cry-wolf).

⚠️ ЧЕСТНАЯ ГРАНИЦА ЗАМЕРА. Считается ВЫЗОВ, а не польза. Скилл с 40 вызовами может быть
40 раз бесполезен. Ноль вызовов -- сильный сигнал (кандидат в Dead-Code на /retro),
ненулевой -- слабый. Не выдавать эти цифры за метрику пользы.

ГРАНИЦА ПРИВАТНОСТИ. Пишем ИМЯ скилла и ДЛИНУ аргументов, никогда сами аргументы: в них
попадают имена лидов, ссылки, куски текстов. Секреты сюда не попадают по построению.

Тест: scripts/_test_skill_usage_log.py
"""
from __future__ import annotations

import argparse
import json
import os
import re
import sys
import time
import uuid
from datetime import datetime, timedelta, timezone

_HERE = os.path.dirname(os.path.abspath(__file__))
if _HERE not in sys.path:
    sys.path.insert(0, _HERE)

OUTCOMES = ("ok", "fail")
KINDS = ("skill", "part")
SUBDIR = os.path.join("_metrics", "skill-usage")          # kind=skill (историческое имя)
SUBDIR_PART = os.path.join("_metrics", "part-usage")      # kind=part


def subdir_of(kind: str) -> str:
    """Шарды РАЗНЫХ видов лежат в РАЗНЫХ каталогах.

    Почему не один файл с полем-фильтром: у скилл-счётчика уже есть читатели, и
    строка про деталь (`day-ledger`) выглядела бы для них скиллом, которого нет в
    ~/.claude/skills -- то есть попала бы в `--dead` как «молчащий скилл». Разные
    каталоги = старый читатель новых строк не видит вообще (класс
    one-file-two-schemas).
    """
    return SUBDIR_PART if kind == "part" else SUBDIR


def _machine() -> str:
    """Имя узла через ЕДИНСТВЕННУЮ дверь (класс bare-env закрыт 01.08)."""
    try:
        import menv  # type: ignore
        return menv.machine_key("unknown")
    except Exception:
        return (os.environ.get("COMPUTERNAME")
                or os.environ.get("MACHINE_KEY")
                or os.uname().nodename if hasattr(os, "uname") else "unknown")


def _actor() -> str:
    """Кто за рулём. Явная переменная бьёт догадку; неизвестно -- так и пишем."""
    a = (os.environ.get("CLAUDE_OPERATOR") or "").strip()
    if a:
        return a
    op = os.path.expanduser("~/.claude/operator.txt")
    try:
        with open(op, encoding="utf-8") as fh:
            v = fh.read().strip()
            if v:
                return v
    except OSError:
        pass
    return "unknown"


def _bus_dir() -> str | None:
    d = os.environ.get("MACHINE_BUS_DIR")
    return d if d and os.path.isdir(d) else None


def roots(for_write: bool = False, kind: str = "skill") -> list[str]:
    """Куда писать / откуда читать. Шина первой, локальный запас всегда."""
    sub = subdir_of(kind)
    out = []
    bus = _bus_dir()
    if bus:
        out.append(os.path.join(bus, sub))
    out.append(os.path.expanduser(os.path.join("~/.claude", sub)))
    if for_write:
        return out[:1] or out
    return out


def _shard(root: str, machine: str) -> str:
    return os.path.join(root, "%s.jsonl" % machine)


def log(skill: str, outcome: str = "ok", args_len: int = 0,
        source: str = "hook", kind: str = "skill", extra: dict | None = None) -> bool:
    """Записать один вызов. Никогда не бросает: счётчик не смеет ломать работу.

    kind="part" -- та же механика для НЕ-скилловых деталей (скрипт, рутина, дашборд):
    §5.8 требует счётчик у каждой живой детали, а не только у скиллов. Имя детали
    кладётся в то же поле `skill` (историческое), различает виды поле `kind`.
    """
    skill = (skill or "").strip()
    if not skill:
        return False
    if outcome not in OUTCOMES:
        outcome = "ok"
    if kind not in KINDS:
        kind = "skill"
    row = {
        # Свой id у каждой записи. Дедуп при чтении обязан различать «одна строка,
        # прочитанная из двух корней» и «два реальных вызова». Тройки (ts, узел, скилл)
        # для этого мало: два вызова одного скилла в одну секунду -- обычное дело
        # (цепочка скиллов внутри задачи), и они схлопывались в один. Поймано T2.
        "id": uuid.uuid4().hex[:12],
        "ts": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "machine": _machine(),
        "actor": _actor(),
        "skill": skill,
        "kind": kind,
        "args_len": int(args_len or 0),
        "outcome": outcome,
        "source": source,
    }
    # extra -- метки атрибуции (session, routine), 08.10.2026: без них потребитель
    # (rail_plan.py verdict) не мог отличить свой вызов от вызова соседнего прогона
    # того же узла и засчитывал обещанию чужие вызовы дня. Пустые значения не пишем,
    # основные поля строки extra перезаписать не может.
    for k, v in (extra or {}).items():
        if v and k not in row:
            row[k] = v
    line = json.dumps(row, ensure_ascii=False) + "\n"
    wrote = False
    # Пишем в шину И в локальный запас: шард в шине может быть недоступен (нет синка),
    # а потерянный вызов уже не восстановить. Дедуп при чтении по (ts, machine, skill).
    for root in (roots(for_write=True, kind=kind)
                 + [os.path.expanduser(os.path.join("~/.claude", subdir_of(kind)))]):
        try:
            os.makedirs(root, exist_ok=True)
            with open(_shard(root, row["machine"]), "a", encoding="utf-8") as fh:
                fh.write(line)
            wrote = True
        except OSError:
            continue
    return wrote


# --------------------------------------------------------------------------
# СКАН ТРАНСКРИПТОВ (origin: приказ Антона 05.08.2026, «строй ночного считальщика»)
#
# ЗАЧЕМ. Хук ловит ТОЛЬКО вызов инструмента `Skill`. Рутина, которой сказано
# «читай SKILL.md первым», исполняет скилл целиком и не оставляет ни одной записи:
# замер 05.08 - книжный прогон вёл `journey` весь день, счётчик показал 0.
# Вердикт «молчит» на таких данных снёс бы именно рутинные скиллы.
#
# ДВА РАЗНЫХ СОБЫТИЯ, НЕ СМЕШИВАТЬ (иначе повторим тот же грех - меряем не то):
#   mode="invoked" - блок tool_use с name="Skill"                 (вызван кнопкой)
#   mode="read"    - tool_use Read по .../skills/<имя>/SKILL.md   (прочитан и исполнен)
# Оба - СТРУКТУРНЫЕ поля JSON, не текстовый поиск по прозе: имя скилла, упомянутое
# в разговоре, использованием НЕ считается (иначе этот самый разбор засчитал бы
# все 144 скилла разом).
#
# ИДЕМПОТЕНТНОСТЬ: ключ дедупа = id блока tool_use. Повторный скан не удваивает.
SKILL_PATH_RE = re.compile(r"[\\/]skills[\\/]([A-Za-z0-9_.-]+)[\\/]SKILL\.md$", re.I)
TRANSCRIPT_ROOT = os.path.expanduser("~/.claude/projects")


# ⚠️ Каталог ~/.claude/projects СИНКАЕТСЯ между машинами: на хабе лежат транскрипты
# [машина флота], Mac-2019 и ноутбука. Первая версия скана (05.08.2026, 21:0x) штамповала все
# 1022 строки как [машина флота] - то есть приписывала хабу чужую работу и ломала
# отчёт --by-node. Машину выводим из имени каталога проекта (оно кодирует рабочий
# путь), а где не уверены - пишем "unknown", а не догадку: прибор, который не смог
# измерить, обязан отвечать «не знаю», а не «хаб».
def _origin_from_project(dirname: str) -> str:
    # Имена каталогов проектов зависят от ТВОИХ машин: допиши свои ветки под свой реестр.
    # Пока не уверены, отвечаем "unknown", а не догадкой.
    return "origin:unknown"


def _iter_transcripts(root: str, cutoff_ts: float):
    for dirpath, _dirs, files in os.walk(root):
        for fn in files:
            if not fn.endswith(".jsonl"):
                continue
            p = os.path.join(dirpath, fn)
            try:
                if os.path.getmtime(p) < cutoff_ts:
                    continue
            except OSError:
                continue
            yield p


def _failed_tool_use_ids(path: str) -> set:
    """id вызовов, на которые харнес вернул ОШИБКУ (`tool_result.is_error`).

    ЗАЧЕМ (замер 10.09.2026, хаб): сканер ставил `outcome: "ok"` ВСЕМ найденным вызовам,
    не читая результат. Отбитый вызов `hunt-a-handle` (скилл закрыт флагом
    `disable-model-invocation`, харнес отказал) приехал в счётчик как успешное
    использование. Скилл, который позвать НЕВОЗМОЖНО, выглядел живым -- а на этой цифре
    стоит решение «живой или в утиль» (§5.8). Хук такого не делает: у PostToolUse есть
    tool_response, и он честно пишет fail; врал только сканер транскриптов.
    """
    bad = set()
    try:
        with open(path, encoding="utf-8", errors="replace") as fh:
            for line in fh:
                if '"is_error"' not in line or '"tool_result"' not in line:
                    continue  # дешёвый фильтр до json.loads
                try:
                    rec = json.loads(line)
                except ValueError:
                    continue
                content = (rec.get("message") or {}).get("content")
                if not isinstance(content, list):
                    continue
                for blk in content:
                    if (isinstance(blk, dict) and blk.get("type") == "tool_result"
                            and blk.get("is_error") and blk.get("tool_use_id")):
                        bad.add(blk["tool_use_id"])
    except OSError:
        pass
    return bad


def scan_transcripts(days: int = 60, root: str | None = None,
                     dry_run: bool = False) -> dict:
    """Пройти транскрипты и дописать пропущенные использования скиллов."""
    root = root or TRANSCRIPT_ROOT
    known_names = set(_installed_skills())
    seen_ids = {r.get("id") for r in read_all(None, kind="skill")}
    cutoff_ts = time.time() - days * 86400

    found: list[dict] = []
    n_files = 0
    for p in _iter_transcripts(root, cutoff_ts):
        n_files += 1
        # Сутки события берём по mtime транскрипта: сессия живёт внутри одного дня.
        day_ts = datetime.fromtimestamp(os.path.getmtime(p), timezone.utc)
        origin = _origin_from_project(os.path.basename(os.path.dirname(p)))
        error_ids = _failed_tool_use_ids(p)
        try:
            with open(p, encoding="utf-8", errors="replace") as fh:
                for line in fh:
                    # Дешёвый фильтр ДО json.loads: разбирать гигабайты построчно дорого.
                    if '"tool_use"' not in line:
                        continue
                    if '"Skill"' not in line and "SKILL.md" not in line:
                        continue
                    try:
                        rec = json.loads(line)
                    except ValueError:
                        continue
                    content = (rec.get("message") or {}).get("content")
                    if not isinstance(content, list):
                        continue
                    for blk in content:
                        if not isinstance(blk, dict) or blk.get("type") != "tool_use":
                            continue
                        inp = blk.get("input") or {}
                        if not isinstance(inp, dict):
                            continue
                        name, mode = None, None
                        if blk.get("name") == "Skill":
                            name = str(inp.get("skill") or "").strip()
                            mode = "invoked"
                        elif blk.get("name") in ("Read", "read_file"):
                            m = SKILL_PATH_RE.search(str(inp.get("file_path") or ""))
                            if m:
                                name, mode = m.group(1), "read"
                        if not name or not mode:
                            continue
                        # Плагинные имена "plugin:skill" сводим к правой части.
                        if ":" in name:
                            name = name.split(":")[-1]
                        bid = blk.get("id") or ""
                        if not bid or bid in seen_ids:
                            continue
                        seen_ids.add(bid)
                        found.append({
                            "id": bid,
                            "ts": day_ts.isoformat(timespec="seconds"),
                            "machine": origin,
                            "scanned_by": _machine(),
                            "actor": "unknown",
                            "skill": name,
                            "kind": "skill",
                            "args_len": 0,
                            "outcome": "fail" if bid in error_ids else "ok",
                            "source": "transcript",
                            "mode": mode,
                            "known": name in known_names,
                        })
        except OSError:
            continue

    summary = {
        "files": n_files, "new_rows": len(found),
        "invoked": sum(1 for r in found if r["mode"] == "invoked"),
        "read": sum(1 for r in found if r["mode"] == "read"),
        "unknown_names": sorted({r["skill"] for r in found if not r["known"]})[:20],
        "dry_run": dry_run,
    }
    if dry_run or not found:
        return summary

    written = 0
    for troot in (roots(for_write=True, kind="skill")
                  + [os.path.expanduser(os.path.join("~/.claude", subdir_of("skill")))]):
        try:
            os.makedirs(troot, exist_ok=True)
            with open(_shard(troot, _machine()), "a", encoding="utf-8") as fh:
                for r in found:
                    fh.write(json.dumps(r, ensure_ascii=False) + "\n")
            written += 1
        except OSError:
            continue
    summary["shards_written"] = written
    return summary


def read_all(days: int | None = None, kind: str = "skill") -> list[dict]:
    seen, rows = set(), []
    cutoff = None
    if days:
        cutoff = datetime.now(timezone.utc) - timedelta(days=days)
    for root in roots(kind=kind):
        if not os.path.isdir(root):
            continue
        for name in sorted(os.listdir(root)):
            if not name.endswith(".jsonl"):
                continue
            try:
                with open(os.path.join(root, name), encoding="utf-8") as fh:
                    for line in fh:
                        line = line.strip()
                        if not line:
                            continue
                        try:
                            r = json.loads(line)
                        except ValueError:
                            continue
                        # id есть у новых строк; у древних (до 04.08) его нет --
                        # для них падаем на старую тройку, чтобы не потерять историю.
                        key = r.get("id") or (r.get("ts"), r.get("machine"),
                                              r.get("skill"), r.get("outcome"))
                        if key in seen:
                            continue
                        seen.add(key)
                        if cutoff:
                            try:
                                if datetime.fromisoformat(r["ts"]) < cutoff:
                                    continue
                            except (KeyError, ValueError, TypeError):
                                pass
                        rows.append(r)
            except OSError:
                continue
    return _drop_hook_twins(rows)


_ORIGIN_TO_NODE = {}  # origin:<код> -> имя узла из твоего реестра


def norm_node(name: str) -> str:
    """Одно ИМЯ на узел: хук подписывается ключом флота, сканер -- меткой origin:*.

    ЗАМЕР 10.09.2026: `/retro` показывал `[машина флота]: 78` И `origin:hub: 76` -- это
    ОДИН узел, разъехавшийся на две строки, потому что писатели называют его по-разному.
    Из-за этого (а) отчёт двоил вклад узла, (б) схлопывание близнецов не срабатывало:
    ключ дедупа содержит машину, а машины «не совпадали». `origin:unknown` не
    сопоставляется ничему и остаётся как есть -- честная дырка лучше выдуманного узла.
    """
    return _ORIGIN_TO_NODE.get((name or "").strip().lower(), name)


def _drop_hook_twins(rows: list[dict]) -> list[dict]:
    """Убрать двойной счёт: один вызов пишут ДВА писателя с разными схемами id.

    ЗАМЕР 10.09.2026 (хаб): `find-hidden-subdomains` позвали ОДИН раз, в отчёте 2.
    Хук пишет строку со своим id (`45174c526f25`), ночной скан транскриптов -- со своим
    (`toolu_018SSb...`). Дедуп в `read_all` идёт по id, поэтому строки разных писателей
    не схлопываются НИКОГДА, и каждый интерактивный вызов с 05.08 считался дважды.
    Перекос не равномерный: рутинные прогоны хук не видит вовсе, их считает только скан,
    -- то есть интерактив был раздут вдвое ОТНОСИТЕЛЬНО фона, и «живой/мёртвый» решалось
    по кривой шкале.

    Правило схлопывания: скан транскриптов -- НАДМНОЖЕСТВО (он читает транскрипт каждой
    сессии, и живой, и роботной), поэтому в сутках, где по скиллу есть строки сканера,
    строки хука отбрасываются. Где сканер ещё не проходил (сегодняшний день до ночного
    прогона) -- живут строки хука, иначе свежий вызов пропал бы из отчёта.
    """
    def day_of(r):
        return str(r.get("ts") or "")[:10]

    covered = {(norm_node(r.get("machine")), r.get("skill"), day_of(r))
               for r in rows if r.get("source") == "transcript"}
    return [r for r in rows
            if r.get("source") != "hook"
            or (norm_node(r.get("machine")), r.get("skill"), day_of(r)) not in covered]


def summarize(rows: list[dict]) -> dict:
    per_skill: dict[str, dict] = {}
    nodes: set[str] = set()
    for r in rows:
        s = r.get("skill") or "?"
        m = norm_node(r.get("machine") or "?")
        nodes.add(m)
        d = per_skill.setdefault(s, {"total": 0, "fail": 0, "by_node": {}})
        d["total"] += 1
        if r.get("outcome") == "fail":
            d["fail"] += 1
        d["by_node"][m] = d["by_node"].get(m, 0) + 1
    return {"per_skill": per_skill, "nodes": sorted(nodes), "rows": len(rows)}


def _installed_skills() -> list[str]:
    """Скилл = каталог, в котором ЛЕЖИТ SKILL.md. Раньше считался любой подкаталог,
    и в списке «молчащих скиллов» висели `.git`, `.stfolder`, `.stversions` —
    служебные папки git и Syncthing. Мусор в знаменателе занижает долю живых и делает
    отчёт поводом ему не верить (класс shrinking-denominator-metric)."""
    root = os.path.expanduser("~/.claude/skills")
    try:
        return sorted(d for d in os.listdir(root)
                      if not d.startswith(".")
                      and os.path.isfile(os.path.join(root, d, "SKILL.md")))
    except OSError:
        return []



# §5.8 говорит «0 вызовов за 30д = кандидат в утиль». Значит вердикт «молчит»
# имеет силу ТОЛЬКО если счётчик реально измерял эти 30 дней. Замер 05.08.2026:
# отчёт печатал «за 30 дн» имея 2 суток данных (4 записи), из чего следовал вывод
# «142 скилла мёртвые» -- вывод, не подкреплённый ничем. Прибор обязан сообщать
# возраст собственных данных рядом с числом, иначе он врёт полнотой.
MIN_VERDICT_DAYS = 30


def data_age_days(kind: str = "skill"):
    """Сколько суток счётчик реально пишет. None = данных нет вовсе."""
    first = None
    for row in read_all(None, kind=kind):
        ts = row.get("ts")
        if not ts:
            continue
        try:
            t = datetime.fromisoformat(ts)
        except ValueError:
            continue
        if t.tzinfo is None:
            t = t.replace(tzinfo=timezone.utc)
        if first is None or t < first:
            first = t
    if first is None:
        return None
    return max(0.0, (datetime.now(timezone.utc) - first).total_seconds() / 86400.0)


def _age_line(days: int, kind: str = "skill"):
    """Строка про возраст данных + флаг, можно ли выносить вердикт «молчит»."""
    age = data_age_days(kind)
    if age is None:
        return "возраст данных: ПУСТО -- счётчик не написал ни строки", False
    covered = min(age, days)
    ok = age >= MIN_VERDICT_DAYS
    line = "возраст данных: %.1f сут (запрошено окно %d дн, реально покрыто %.1f)" % (
        age, days, covered)
    if not ok:
        line += "\n  !! ВЕРДИКТ «МОЛЧИТ» НЕ ВЫНОСИТСЯ: нужно %d сут наблюдения, есть %.1f." % (
            MIN_VERDICT_DAYS, age)
        line += "\n     Ноль вызовов сейчас значит «мы столько не смотрели», а не «скилл мёртв»."
    return line, ok


def _runbook_skills() -> set:
    """Скиллы-РАНБУКИ: ноль вызовов у них -- норма по назначению, не смерть.

    Список лежит в текстовом файле рядом (runbook_skills.txt), чтобы его правил
    человек блокнотом, а не код. Файла нет -> пустое множество и обычное поведение.
    """
    p = os.path.join(_HERE, "runbook_skills.txt")
    out = set()
    try:
        with open(p, encoding="utf-8") as fh:
            for ln in fh:
                ln = ln.split("#", 1)[0].strip()
                if ln:
                    out.add(ln)
    except OSError:
        pass
    return out


def _report(days: int, as_json: bool, by_node: bool, dead: bool, raw: bool,
            kind: str = "skill") -> int:
    rows = read_all(days, kind=kind)
    s = summarize(rows)
    age_line, verdict_ok = _age_line(days, kind)
    if as_json:
        s["data_age_days"] = data_age_days(kind)
        s["verdict_allowed"] = verdict_ok
        s["min_verdict_days"] = MIN_VERDICT_DAYS
    if raw:
        for root in roots(kind=kind):
            exists = os.path.isdir(root)
            files = sorted(os.listdir(root)) if exists else []
            print("root %-60s exists=%s files=%s" % (root, exists, files))
        return 0
    if as_json:
        print(json.dumps(s, ensure_ascii=False, indent=2))
        return 0

    # Список «что установлено» есть только у скиллов (каталог ~/.claude/skills).
    # У деталей такого реестра нет, поэтому для kind=part молчащих не выводим:
    # напечатать «молчат: 0» там значило бы соврать полнотой (класс
    # blind-watchdog-must-not-cry-wolf).
    installed = _installed_skills() if kind == "skill" else []
    used = s["per_skill"]
    print("== использование %s за %d дн ==" % ("скиллов" if kind == "skill" else "деталей", days))
    print("  " + age_line)
    print("узлы-писатели: %s" % (", ".join(s["nodes"]) or "НИ ОДНОГО"))
    if not s["nodes"]:
        print("  !! ноль строк. Это может значить «не пользовались», а может -- «хук не")
        print("     раскатан ни на один узел». Проверь: --report --raw")
    print()
    if dead:
        if kind != "skill":
            print("у деталей нет реестра «что установлено» -- список молчащих собрать")
            print("не из чего. Ноль строк по имени детали = деталь не звали.")
            return 0
        silent = [k for k in installed if k not in used]
        # ВТОРОЙ этаж того же корня: скилл, который МОЛОЖЕ окна вердикта, физически
        # не мог набрать вызовов за это окно. Замер 05.08.2026: из 64 молчащих 63
        # оказались моложе 30 суток (часть - созданные в тот же день), по-настоящему
        # старым и молчащим был ОДИН. Список без этого фильтра предлагал снести
        # то, что мы построили накануне.
        # ⚠️ Честная оговорка: mtime у SKILL.md - «последняя правка», а не «дата
        # рождения». Правка омолаживает файл, поэтому фильтр КОНСЕРВАТИВЕН: он
        # может придержать реально старый скилл, но не выдаст молодой за зрелый.
        runbooks = _runbook_skills()
        mature, young, insurance = [], [], []
        now = time.time()
        for k in silent:
            if k in runbooks:
                insurance.append(k)
                continue
            p = os.path.expanduser(os.path.join("~/.claude/skills", k, "SKILL.md"))
            try:
                age = (now - os.path.getmtime(p)) / 86400.0
            except OSError:
                age = None
            (mature if (age is not None and age >= MIN_VERDICT_DAYS) else young).append((k, age))
        label = "МОЛЧАТ" if verdict_ok else "БЕЗ ВЫЗОВОВ (это НЕ вердикт, см. возраст данных)"
        print("скиллов установлено: %d · с вызовами: %d · %s: %d"
              % (len(installed), len(used), label, len(silent)))
        print()
        if insurance:
            print("  РАНБУКИ (ноль вызовов = норма, вопрос не «звали?», а «ещё работает?»): %d"
                  % len(insurance))
            for k in sorted(insurance):
                print("   -  %s" % k)
            print()
        print("  КАНДИДАТЫ В УТИЛЬ (старше %d сут И ноль вызовов): %d"
              % (MIN_VERDICT_DAYS, len(mature)))
        for k, age in sorted(mature, key=lambda kv: -(kv[1] or 0)):
            print("   0  %-28s правился %.0f сут назад" % (k, age or 0))
        print()
        print("  МОЛОЖЕ ОКНА, вердикт неприменим по определению: %d" % len(young))
        for k, age in sorted(young, key=lambda kv: (kv[1] if kv[1] is not None else 1e9)):
            print("   0  %-28s %s" % (
                k, ("правился %.1f сут назад" % age) if age is not None else "файла нет"))
        if not verdict_ok:
            print()
            print("  ⛔ Список выше НЕЛЬЗЯ использовать как основание сносить скиллы.")
            print("     Вернись к нему, когда возраст данных дойдёт до %d сут." % MIN_VERDICT_DAYS)
        return 0
    order = sorted(used.items(), key=lambda kv: -kv[1]["total"])
    for name, d in order:
        line = "%5d  %-28s" % (d["total"], name)
        if d["fail"]:
            line += "  fail=%d" % d["fail"]
        if by_node:
            line += "  " + " ".join("%s:%d" % (m, c)
                                    for m, c in sorted(d["by_node"].items()))
        print(line)
    if installed:
        print()
        print("установлено %d скиллов, звали %d, молчат %d (список: --dead)"
              % (len(installed), len(used), len(installed) - len(used)))
    return 0


def _cli() -> int:
    p = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    p.add_argument("--report", action="store_true")
    p.add_argument("--days", type=int, default=30)
    p.add_argument("--json", action="store_true")
    p.add_argument("--by-node", action="store_true")
    p.add_argument("--dead", action="store_true", help="скиллы с НУЛЁМ вызовов")
    p.add_argument("--raw", action="store_true", help="какие шарды вообще видны")
    p.add_argument("--log", metavar="SKILL", help="записать вызов вручную")
    p.add_argument("--outcome", default="ok", choices=list(OUTCOMES))
    p.add_argument("--kind", default="skill", choices=list(KINDS),
                   help="skill = скиллы (дефолт) · part = прочие детали (скрипт/рутина/дашборд)")
    p.add_argument("--scan-transcripts", action="store_true",
                   help="добрать использования из транскриптов сессий (хук видит "
                        "только вызов инструмента Skill и слеп к рутинам)")
    p.add_argument("--dry-run", action="store_true",
                   help="со --scan-transcripts: только посчитать, ничего не писать")
    a = p.parse_args()
    if a.scan_transcripts:
        s = scan_transcripts(days=max(a.days, 1), dry_run=a.dry_run)
        print("скан транскриптов: файлов %d · новых событий %d "
              "(вызовов %d, чтений скилла %d)%s"
              % (s["files"], s["new_rows"], s["invoked"], s["read"],
                 " [СУХОЙ ПРОГОН, не записано]" if s.get("dry_run") else ""))
        if s.get("unknown_names"):
            print("  имена вне каталога ~/.claude/skills (встроенные/плагинные): %s"
                  % ", ".join(s["unknown_names"]))
        return 0
    if a.log:
        ok = log(a.log, outcome=a.outcome, source="manual", kind=a.kind)
        print("logged" if ok else "NOT WRITTEN")
        return 0 if ok else 1
    return _report(a.days, a.json, a.by_node, a.dead, a.raw, kind=a.kind)


if __name__ == "__main__":
    sys.exit(_cli())
