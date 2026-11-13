#!/usr/bin/env python3
"""mutants.py: проверка самих проб. Каждый гейт ломается В КОПИИ набора, после чего его проба обязана покраснеть.
Проба, которая остаётся зелёной на сломанном гейте, ничего не доказывает.

  tools/intel-mac/tests/mutants.py [--only <имя мутанта>] [--list]

Боевой скрипт не трогается: набор копируется во временный каталог, правка вносится в копию, пробы
(kill_gates.sh, test_helpers.sh) запускаются на копии. Правка = замена точной строки; строка обязана
встретиться ровно один раз, иначе мутант «не применим» и это ошибка прибора (список отстал от скрипта).

Итог мутанта: KILLED (проба покраснела, код 1) · SURVIVED (проба зелёная: дыра в пробе) · ERROR (проба не отработала).
Коды: 0 = все KILLED · 1 = есть SURVIVED · 2 = есть ERROR или мутант не применим.
"""
import os, shutil, subprocess, sys, tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
TOOLS = HERE.parent.parent           # каталог tools/
S = "intel-mac/onboard-intel-mac.sh"
P = "secret_prompt.sh"

# (имя, файл, [(было, стало), ...], проба, [сценарии], строка, которая обязана появиться в выводе пробы или None)
M = [
 ("profile-missing", S, [('load_profile "$PROFILE"', '[ -z "$PROFILE" ] && P_NODE_DIR="$HOME/lab" && PROFILE=/dev/null; load_profile "$PROFILE"')], "kill", ["s_profile_missing"], None),
 ("profile-placeholder", S, [('case "$val" in *CHANGE_ME*)', 'case "$val" in *NEVER_MATCHES_ANYTHING*)')], "kill", ["s_profile_placeholder"], None),
 ("profile-tracked", S, [('git ls-files --error-unmatch "$(basename "$f")" >/dev/null 2>&1 ); then', 'false ); then')], "kill", ["s_profile_tracked"], None),
 ("profile-keys", S, [('need github GIT_NAME GIT_EMAIL GITHUB_LOGIN || return 1', 'need github GIT_NAME GITHUB_LOGIN || return 1')], "kill", ["s_profile_keys"], None),
 ("intel-guard", S, [('\nguard_intel\n', '\n:\n')], "kill", ["s_intel"], None),
 ("hash-vendor", S, [('  if [ "$got" != "$vendor" ]; then', '  if false; then')], "kill", ["s_hash_vendor"], None),
 ("hash-pin", S, [('  [ "$got" = "$pinned" ] || {', '  true || {')], "kill", ["s_hash_pin"], None),
 ("shared-gate", S, [('  [ "${SHARED_ACCOUNT_OK:-0}" = 1 ] && return 0', '  return 0')], "kill", ["s_shared", "s_park"], None),
 ("gh-account", S, [('  if [ "$who" = "$P_GITHUB_LOGIN" ]; then', '  if true; then')], "kill", ["s_gh_account"], None),
 ("tg-first", S, [('--label mcp || { say "  демон и рельсу без первой сессии не поднимаю"; return 1; }; fi', '--label mcp || true; fi'),
                  ('  [ "$DRY" = 1 ] || [ -f "$STORE/mcp.session.env" ] || {', '  true || {')], "kill", ["s_tg_first"], None),
 ("tg-rail", S, [('TGBUS_DAEMON_PLIST="$plist" step G-TG-RAIL "вторая сессия Telegram (rail)" "$VENV_PY" "$STORE/tg_login_rail.py" || return 1', 'TGBUS_DAEMON_PLIST="$plist" run "$VENV_PY" "$STORE/tg_login_rail.py"'),
                 ('    [ "$DRY" = 1 ] || [ -f "$STORE/rail.session.env" ] || {', '    true || {')], "kill", ["s_tg_rail"], None),
 ("tg-pin", S, [('    pin_repo "$MCP_DIR" "$TGMCP_URL" "$TGMCP_SHA" || return 1', '    true'), ('    pin_repo "$KIT_DIR" "$TGKIT_URL" "$TGKIT_SHA" || return 1', '    true')], "kill", ["s_tg_pin"], None),
 ("tg-conflict-markers", S, [("  if g -q -E '^(<<<<<<<|>>>>>>>)' \"$MCP_DIR/telegram_mcp/tools/messages.py\" \"$MCP_DIR/telegram_mcp/tools/chats.py\" 2>/dev/null; then", "  if false; then")], "kill", ["s_tg_conflict"], None),
 ("park-continues", S, [('  park_starter_law || { say "  папки НЕ принимаю: сперва гейт выше"; return 1; }', '  park_starter_law')], "kill", ["s_park"], None),
 ("stignore-ignored", S, [('  write_ignore "$dir" "$ign" || { bad G-STIGNORE "${id}: .stignore не записан или не прочитан обратно: шару НЕ принимаю"; return 1; }', '  write_ignore "$dir" "$ign"')], "kill", ["s_stignore_write", "s_stignore_readback"], None),
 ("stignore-readback", S, [('  [ -f "$dir/.stignore" ] && [ ! -L "$dir/.stignore" ] && printf \'%s\\n\' "$want" | cmp -s - "$dir/.stignore"; }', '  true; }'),
                           ('  if [ -d "$f" ]; then say "  ! $f это каталог, а нужен файл"; rm -f "$tmp"; return 1; fi\n', ''),
                           (' && chmod "$m" "$f" && cmp -s "$tmp" "$f"; rc=$?', '; rc=$?')], "kill", ["s_stignore_readback"], None),
 ("home-probe", S, [('receiveonly "$(home_probe)"', 'receiveonly "$(home_whitelist)"')], "kill", ["s_home_probe"], None),
 ("home-flag", S, [('  elif [ "${CLAUDE_HOME_WHITELIST_OK:-0}" = 1 ]; then', '  elif true; then')], "kill", ["s_home_flag"], None),
 ("home-whitelist-danger", S, [('    case "$tok" in .|..|projects|', '    case "$tok" in .|..|')], "kill", ["s_home_whitelist"], None),
 ("home-whitelist-glob", S, [('  set -f   # без раскрытия шаблонов', '  :   # без раскрытия шаблонов')], "kill", ["s_home_whitelist"], None),
 ("home-whitelist-star", S, [('    re_ok "$tok" \'[A-Za-z0-9._-]+\' || die 3', '    true || die 3')], "kill", ["s_home_whitelist"], None),
 ("folder-path-accept", S, [('    if [ "$cur_path" != "$dir" ] || [ "$cur_type" != "$type" ]; then', '    if false; then')], "kill", ["s_folder_path_accept"], None),
 ("folder-path-verify", S, [('''    [ "$(printf '%s' "$cfg" | jq -r '.path // empty')" = "$dir" ] && [ "$(printf '%s' "$cfg" | jq -r '.type // empty')" = "$type" ] || return 1''', '    true')], "kill", ["s_folder_path_verify"], None),
 ("merge", S, [(' && [ "${MERGE_OK:-0}" != 1 ]; then', ' && false; then')], "kill", ["s_merge"], None),
 ("sync-dir", S, [('  case "$dir" in "$HOME/Sync"|"$HOME/Sync"/*)', '  case "$dir" in /never/matches)')], "kill", ["s_sync_dir"], None),
 ("hub-id", S, [("  [ -z \"${P_HUB_DEVICE_ID:-}\" ] || re_ok \"$P_HUB_DEVICE_ID\" '[A-Z2-7]{7}(-[A-Z2-7]{7}){7}' || die 3", '  true || die 3')], "kill", ["s_hub_id"], None),
 ("bus-layout-default", S, [('MEMORY_SHARE_SLUG BUS_LAYOUT CLAUDE_HOME_ALLOW || return 1', 'MEMORY_SHARE_SLUG CLAUDE_HOME_ALLOW || return 1')], "kill", ["s_bus_layout"], None),
 ("bus-exclude-first-layer", S, [('"// Раскладка профиля BUS_LAYOUT=separate-share: шина едет ОТДЕЛЬНОЙ шарой и исключена здесь ДО приёма волта." "/$(bus_rel)"; fi', '"// мутант: исключения шины нет"; fi')], "kill", ["s_bus_separate"], "[G-BUS-EXCLUDE]"),
 ("bus-exclude-both-layers", S, [('"// Раскладка профиля BUS_LAYOUT=separate-share: шина едет ОТДЕЛЬНОЙ шарой и исключена здесь ДО приёма волта." "/$(bus_rel)"; fi', '"// мутант: исключения шины нет"; fi'),
                                 ('      if [ -n "$(bus_rel)" ] && ! g -q -x -F "/$(bus_rel)" "$P_VAULT_ROOT/.stignore" 2>/dev/null; then', '      if false; then')], "kill", ["s_bus_separate"], None),
 ("bus-inside-table", S, [('  [ "$P_BUS_LAYOUT" != separate-share ] || printf', '  printf')], "kill", ["s_bus_inside"], None),
 ("bus-inside-accepted", S, [('    if [ "$P_BUS_LAYOUT" = separate-share ]; then\n      # второй слой', '    if true; then\n      # второй слой')], "kill", ["s_bus_inside"], None),
 ("bus-inside-excluded", S, [('  if [ "$P_BUS_LAYOUT" = separate-share ] && [ -n "$(bus_rel)" ]; then', '  if [ -n "$(bus_rel)" ]; then')], "kill", ["s_bus_inside"], None),
 ("f3-one-var", S, [('  if f3_ok; then ok "env F3', '  if g -q \'CLAUDE_OPERATOR=\' "$HOME/.zshrc" 2>/dev/null; then ok "env F3')], "kill", ["s_f3"], None),
 ("vault-root-basename", S, [('"export CLAUDE_VAULT_ROOT=$(shq "$P_VAULT_ROOT")"', '"export CLAUDE_VAULT_ROOT=$(shq "$HOME/Obsidian/$(basename "$P_VAULT_ROOT")")"')], "kill", ["s_vault_root"], None),
 ("memlink-left", S, [('    if [ -L "$proj" ]; then cur="$(readlink "$proj")"', '    if false; then cur="$(readlink "$proj")"'),
                      ('    elif [ -d "$proj" ]; then', '    elif [ -d "$proj" ] && [ ! -L "$proj" ]; then'),
                      ('    [ "$DRY" = 1 ] || [ "$(readlink "$proj")" = "$share" ] || {', '    true || {')], "kill", ["s_memlink"], None),
 ("law-llm-skip", S, [('then skip G-VERIFY-LLM "VERIFY_LLM=0', 'then say "VERIFY_LLM=0')], "kill", ["s_law_llm_skip"], None),
 ("verify-skip-green", S, [('  if [ "${VERIFY_LLM:-1}" = 0 ] || [ "$DRY" = 1 ]; then\n    row_skip "4', '  if false; then\n    row_skip "4')], "kill", ["s_verify_skip"], None),
 ("phase-continues", S, [('следующие фазы не запускаю."; break; fi', 'следующие фазы не запускаю."; fi')], "kill", ["s_phase_stop"], None),
 ("second-exit", S, [('die()  { EXIT_FORCE="$1"; shift;', 'die()  { [ "$1" = 99 ] && exit 0; EXIT_FORCE="$1"; shift;')], "kill", ["s_single_exit"], None),
 ("gate-in-pipe", S, [('  accept_folder "$P_VAULT_FOLDER_ID" "$P_VAULT_ROOT" sendreceive "$(vault_ignore)" || return 1\n', '  vault_ignore | accept_folder "$P_VAULT_FOLDER_ID" "$P_VAULT_ROOT" sendreceive "$(vault_ignore)"\n')], "kill", ["s_no_gate_in_pipe", "s_merge"], None),
 # круг 2: отказ шага внутри фазы, симлинки, бэкап содержимым, строка 19 verify
 ("tools-continues", S, [('    verify_sha "$f" "$(vendor_sha "$DL/node-SHASUMS256-$NODE_VER.txt" "$a.tar.gz")" "$KNOWN_NODE" || return 1\n    unpack node tar -xzf "$f" -C "$OPT" || return 1\n    step G-STEP "симлинк node" ln -sfn "$OPT/$a" "$OPT/node" || return 1; fi', '    verify_sha "$f" "$(vendor_sha "$DL/node-SHASUMS256-$NODE_VER.txt" "$a.tar.gz")" "$KNOWN_NODE" && { unpack node tar -xzf "$f" -C "$OPT" && step G-STEP "симлинк node" ln -sfn "$OPT/$a" "$OPT/node"; }; fi')], "kill", ["s_tools_stop"], None),
 ("syncthing-continues", S, [('  accept_folder claude-skills "$HOME/.claude/skills" receiveonly "$(skills_ignore)" || return 1\n', '  accept_folder claude-skills "$HOME/.claude/skills" receiveonly "$(skills_ignore)"\n')], "kill", ["s_syncthing_stop"], None),
 ("put-through-symlink", S, [('  if [ -L "$f" ]; then say "  ! $f это симлинк', '  if false; then say "  ! $f это симлинк')], "kill", ["s_stignore_symlink"], None),
 ("zprofile-through-symlink", S, [('  elif [ -L "$HOME/.zprofile" ]; then bad G-STEP', '  elif false; then bad G-STEP')], "kill", ["s_zprofile_link"], None),
 ("backup-link-only", S, [('  if [ -L "$1" ] && [ -f "$1" ]; then cp -pL "$1" "$b.content" || return 1; fi; return 0; }', '  return 0; }')], "kill", ["s_gitconfig_link"], None),
 ("second-pass-flag", S, [("  if [ -n \"$prev\" ]; then row \"19 повтор verify\" 'test -n \"$prev\"'", "  if true; then row \"19 повтор verify\" 'true'")], "kill", ["s_second_pass"], None),
 ("bus-before-vault", S, [('  if folder_accepted "$P_VAULT_FOLDER_ID"; then   # шина только', '  if true; then   # шина только')], "kill", ["s_pending_vault"], None),
 ("skip-is-green", S, [('  elif [ "$SKIPS" -gt 0 ]; then code=4;', '  elif false; then code=4;')], "kill", ["s_home_probe", "s_pending", "s_law_llm_skip"], None),
 ("post-fail-ignored", S, [('  st_post /rest/config/folders "$body" || { bad G-ST-POST "${id}: POST /rest/config/folders не прошёл"; return 1; }', '  st_post /rest/config/folders "$body"'),
                           ('|| { bad G-ST-POST "устройство хаба не добавлено"; return 1; }; fi', '|| true; fi')], "kill", ["s_post_fail"], None),
 ("pending-is-ok", S, [('|| { skip G-PENDING "хаб ещё не предложил папку ${id}: не принята"; return 0; }; fi', '|| { warn "хаб ещё не предложил папку"; return 0; }; fi')], "kill", ["s_pending"], None),
 ("plist-write-ignored", S, [('<<EOF || { bad G-STEP "plist Syncthing не записан"; return 1; }', '<<EOF || true')], "kill", ["s_plist_write"], None),
 ("key-in-argv", S, [('st_get() { st_hdr | curl -fsS -m 20 -K - "$ST_URL$1"; }', 'st_get() { curl -fsS -m 20 -H "X-API-Key: $(st_key)" "$ST_URL$1"; }')], "kill", ["s_key_argv"], None),
 ("unknown-gate-id", S, [('bad G-MERGE "${id}:', 'bad G-NOT-IN-TABLE "${id}:')], "kill", ["s_gates_table"], None),
 # дверь ввода и помощники Telegram
 ("prompt-no-format", P, [('if [[ "$v" =~ $FULL ]]; then good=1; break; fi', 'good=1; break')], "helpers", [], "sp-format"),
 ("prompt-no-gui-check", P, [('[ "$gui" = Aqua ] || fail 3', 'true || fail 3')], "helpers", [], "sp-nogui"),
 ("prompt-value-to-stdout", P, [("printf 'secret_prompt: %s ok, длина %d\\n' \"$NAME\" \"${#v}\"", "printf 'secret_prompt: %s ok, значение %s\\n' \"$NAME\" \"$v\"")], "helpers", [], "sp-valid"),
 ("prompt-seam-always", P, [('TEST=0; [ "${SECRET_PROMPT_TEST:-0}" = 1 ] && {', 'TEST=1; true && {')], "helpers", [], "sp-seam"),
 ("prompt-newline", P, [("  case \"$v\" in *$'\\n'*|*$'\\r'*) ;; *) if [[ \"$v\" =~ $FULL ]]; then good=1; break; fi;; esac", '  if [[ "$v" =~ $FULL ]]; then good=1; break; fi')], "helpers", [], "sp-newline"),
 ("prompt-stdout-sink", P, [('  [ "$FD" -ge 3 ] || fail 5', '  true || fail 5')], "helpers", [], "sp-fd"),
 ("tgbus-title", "intel-mac/tgbus/tgbus.py", [('print("rail OK: комната видна" if me and ent else "rail DEAD")', 'print(f"rail OK: комната {ent.title} видна" if me and ent else "rail DEAD")')], "helpers", [], "tgbus-title"),
 ("login-telethon-first", "intel-mac/tgbus/tg_login_first.py", [('from secret_dialog import ask\n', 'from secret_dialog import ask\nfrom telethon.sync import TelegramClient\n')], "helpers", [], "login-format"),
 ("login-getpass", "intel-mac/tgbus/tg_login_rail.py", [('from secret_dialog import ask\n', 'from secret_dialog import ask\nimport getpass\n')], "helpers", [], "lint-getpass"),
 ("dialog-multiline", "intel-mac/tgbus/secret_dialog.py", [('    if len([x for x in lines if x]) > 1 or "\\r" in val:', '    if False:')], "helpers", [], "dialog-oneline"),
 ("dialog-no-recheck", "intel-mac/tgbus/secret_dialog.py", [('    if p.returncode != 0 or val is None or not re.fullmatch(regex, val):', '    if p.returncode != 0:')], "helpers", [], "dialog-recheck"),
]

def run_mutant(m, work):
    name, rel, edits, kind, scenarios, expect = m
    kit = work / name / "tools"
    shutil.copytree(TOOLS, kit, ignore=shutil.ignore_patterns("__pycache__"))
    f = kit / rel
    s = f.read_text(encoding="utf-8")
    for old, new in edits:
        if s.count(old) != 1:
            return "ERROR", f"мутант не применим: строка встречается {s.count(old)} раз(а): {old[:60]!r}"
        s = s.replace(old, new)
    f.write_text(s, encoding="utf-8")
    env = dict(os.environ, KG_TMP=str(work / name / "tmp"))
    out = ""; reds = 0
    if kind == "kill":
        for sc in scenarios:
            p = subprocess.run(["/bin/bash", str(kit / "intel-mac/tests/kill_gates.sh"), "--only", sc], capture_output=True, text=True, env=env)
            out += p.stdout + p.stderr
            if p.returncode == 2: return "ERROR", f"проба {sc} не отработала: {(p.stdout + p.stderr).strip().splitlines()[-1][:120]}"
            reds += p.returncode == 1
        if reds != len(scenarios): return "SURVIVED", f"зелёными остались сценарии: {len(scenarios) - reds} из {len(scenarios)}"
    else:
        p = subprocess.run(["/bin/bash", str(kit / "intel-mac/tests/test_helpers.sh")], capture_output=True, text=True, env=env)
        out = p.stdout + p.stderr
        if p.returncode == 2: return "ERROR", "test_helpers не отработал"
        if p.returncode != 1: return "SURVIVED", "test_helpers зелёный"
        if expect and not any(l.startswith("  RED") and expect in l for l in out.splitlines()):
            return "SURVIVED", f"красное есть, но не в проверке «{expect}»"
        expect = None
    if expect:   # вывод самого скрипта под мутантом лежит в <KG_TMP>/<сценарий>/out.txt
        script_out = "".join(f.read_text(encoding="utf-8", errors="replace") for f in (work / name / "tmp").glob("*/out.txt"))
        if expect not in script_out: return "SURVIVED", f"проба покраснела, но в выводе скрипта нет «{expect}»"
    red_lines = [l.strip() for l in out.splitlines() if l.startswith("  RED")]
    return "KILLED", red_lines[0][:150] if red_lines else ""

def main():
    args = sys.argv[1:]
    if "--list" in args: print("\n".join(m[0] for m in M)); return 0
    only = args[args.index("--only") + 1] if "--only" in args else None
    todo = [m for m in M if not only or m[0] == only]
    if not todo: print("нет такого мутанта"); return 2
    work = Path(tempfile.mkdtemp(prefix="mutants-", dir=os.environ.get("KG_TMP") or None))
    counts = {"KILLED": 0, "SURVIVED": 0, "ERROR": 0}
    for m in todo:
        st, note = run_mutant(m, work)
        counts[st] += 1
        print(f"  {st:<8} {m[0]:<26} {note}", flush=True)
    subprocess.run(["chmod", "-R", "u+rwX", str(work)]); shutil.rmtree(work, ignore_errors=True)
    print(f"\nmutants: всего {len(todo)} · KILLED {counts['KILLED']} · SURVIVED {counts['SURVIVED']} · ERROR {counts['ERROR']}")
    return 2 if counts["ERROR"] else 1 if counts["SURVIVED"] else 0

sys.exit(main())
