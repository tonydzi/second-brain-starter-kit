#!/bin/bash
# runbook_smoke.sh: дымовая проверка рунбука и набора ВНЕ рабочей копии автора.
#
#   tools/runbook_smoke.sh [--repo <каталог репозитория>] [--ref <коммит или ветка>] [--offline] [--verbose] [--keep]
#                          [--mirror-upstream <путь или URL>] [--mirror-patches <путь или URL>]
#
# Что делает (каждая проверка = PASS, FAIL или SKIP):
#   1 clone      свежий клон репозитория во временный каталог на названном коммите (по умолчанию HEAD рабочей копии;
#                незакоммиченное в клон НЕ попадает, об этом печатается предупреждение)
#   2 arch       ветка по uname -m: на x86_64 проверяется Intel-рунбук; на arm64 явный отказ (код 2) со ссылкой на
#                ONBOARDING-MAC.md; в ONBOARDING-MAC.md обязана стоять обратная ссылка для Intel
#   3 syntax     bash -n всех *.sh набора, py_compile помощников
#   4 identity   поиск констант личности и секретов в файлах набора (пути /Users/…, почта не из example.com, IP не из
#                RFC 5737, Device ID Syncthing, id чатов Telegram, токены, приватные ключи) + свой закрытый список из
#                файла SMOKE_PRIVATE_PATTERNS. Прибор сперва обязан найти подложенные контрольные строки.
#   5 profile    скрипт онбординга без профиля и с профилем-образцом обязан отказаться стартовать (код 3)
#   6 runbook    команды рунбука ДОСЛОВНО, строка за строкой, из корня клона в одноразовом HOME, до маркера
#                «<!-- smoke:stop» (дальше сеть и руки оператора). Единственная подстановка: вместо «человек заполнил
#                профиль» кладётся вымышленный профиль tests/fixtures/profile.smoke.env.
#   7 patches    закреплённые коммиты апстрима и набора патчей читаются из скрипта; git apply --check на них, строго
#                без --3way (сеть или локальные зеркала --mirror-*)
#   8 links      raw-, blob- и tree-ссылки на GitHub в документах: полный адрес (ветка И файл) обязан отвечать 200 (сеть);
#                контроль зрячести: адрес заведомо несуществующего файла в том же репозитории обязан НЕ отвечать 200
#   9 lint       в логин-скриптах нет getpass и input(); гейты и точка выхода (статические сценарии kill_gates)
#  10 gates      tests/kill_gates.sh и tests/test_helpers.sh из клона
#
# Коды: 0 = PASS (ни FAIL, ни SKIP) · 1 = есть FAIL · 2 = не та архитектура (явный отказ) · 4 = INCOMPLETE (есть SKIP:
#       например --offline без зеркал) · 5 = неверный вызов.
# Честная граница: свежий клон на машине автора не доказывает переносимость. Он ловит «работает только из моей
# папки»; машину без следов автора заменяет только прогон на другой учётке или другом узле.
set -o pipefail
g() { LC_ALL=C /usr/bin/grep -a "$@"; }
HERE="$(cd "$(dirname "$0")" && pwd)"; REPO="$(cd "$HERE/.." && pwd)"; REF=""; OFFLINE=0; VERBOSE=0; KEEP=0; MIR_UP=""; MIR_PATCH=""
while [ $# -gt 0 ]; do case "$1" in
  --repo) REPO="$2"; shift 2;; --ref) REF="$2"; shift 2;; --offline) OFFLINE=1; shift;; --verbose) VERBOSE=1; shift;; --keep) KEEP=1; shift;;
  --mirror-upstream) MIR_UP="$2"; shift 2;; --mirror-patches) MIR_PATCH="$2"; shift 2;;
  -h|--help) sed -n '2,29p' "$0"; exit 0;;
  *) echo "runbook_smoke: неизвестный аргумент: $1" >&2; exit 5;; esac; done
PASS=0; FAIL=0; SKIP=0
pass() { printf 'PASS  %-9s %s\n' "$1" "$2"; PASS=$((PASS+1)); }
fail() { printf 'FAIL  %-9s %s\n' "$1" "$2"; FAIL=$((FAIL+1)); }
skp()  { printf 'SKIP  %-9s %s\n' "$1" "$2"; SKIP=$((SKIP+1)); }
finish() { [ "$KEEP" = 1 ] || { chmod -R u+rwX "$TMP" 2>/dev/null; rm -rf "$TMP"; }
  local code=0 word=PASS; [ "$SKIP" = 0 ] || { code=4; word="INCOMPLETE (есть SKIP)"; }; [ "$FAIL" = 0 ] || { code=1; word=FAIL; }
  printf '\nrunbook_smoke: %s · PASS=%d FAIL=%d SKIP=%d · код %d\n' "$word" "$PASS" "$FAIL" "$SKIP" "$code"; exit "$code"; }
TMP="$(mktemp -d "${TMPDIR:-/tmp}/runbook_smoke.XXXXXX")" || exit 5   # шаблон: на macOS «mktemp -d» без него игнорирует TMPDIR
RUNBOOK=ONBOARDING-MAC-INTEL.md; KIT=tools/intel-mac; SCRIPT="$KIT/onboard-intel-mac.sh"
SCOPE="$RUNBOOK tools/intel-mac tools/runbook_smoke.sh tools/secret_prompt.sh"   # файлы Intel-набора для поиска констант личности (остальной репозиторий вне этой проверки)

# ---------- 1 clone ----------
git -C "$REPO" rev-parse --git-dir >/dev/null 2>&1 || { echo "runbook_smoke: $REPO не git-репозиторий" >&2; rm -rf "$TMP"; exit 5; }
[ -n "$REF" ] || REF="$(git -C "$REPO" rev-parse HEAD)"
SHA="$(git -C "$REPO" rev-parse --verify -q "$REF^{commit}")" || { echo "runbook_smoke: нет коммита $REF" >&2; rm -rf "$TMP"; exit 5; }
echo "runbook_smoke: коммит $SHA · $(date -u +%Y-%m-%dT%H:%M:%SZ) · uname -m = $(uname -m)"
[ -z "$(git -C "$REPO" status --porcelain 2>/dev/null)" ] || echo "ВНИМАНИЕ: в рабочей копии есть незакоммиченное; проверяется только коммит ${SHA:0:12}"
C="$TMP/clone"; H="$TMP/home"; mkdir -p "$H"
if git clone -q --no-hardlinks "$REPO" "$C" 2>"$TMP/clone.err" && git -C "$C" checkout -q "$SHA" 2>>"$TMP/clone.err"; then pass clone "свежий клон на ${SHA:0:12}"
else fail clone "клон не удался: $(head -1 "$TMP/clone.err")"; finish; fi
cd "$C" || finish

# ---------- 2 arch ----------
ARCH="${SMOKE_UNAME_M:-$(uname -m)}"   # SMOKE_UNAME_M: подмена для проверки самой ветки отказа
case "$ARCH" in
  x86_64) pass arch "x86_64: проверяется $RUNBOOK";;
  arm64) echo "ОТКАЗ: это Apple Silicon (arm64). $RUNBOOK и $SCRIPT написаны для Intel и здесь не проверяются. Рунбук для этой машины: ONBOARDING-MAC.md"; KEEP=0; chmod -R u+rwX "$TMP"; rm -rf "$TMP"; exit 2;;
  *) echo "ОТКАЗ: архитектура ${ARCH} не поддержана: нужен Mac на x86_64 (Intel) или arm64 (ONBOARDING-MAC.md)"; rm -rf "$TMP"; exit 2;;
esac
if g -F 'x86_64' ONBOARDING-MAC.md 2>/dev/null | g -F "$RUNBOOK" | g -q -e 'топ' -e 'top'; then pass arch "ONBOARDING-MAC.md отправляет Intel (x86_64) в $RUNBOOK"
else fail arch "в ONBOARDING-MAC.md нет явной развилки «x86_64 = стоп, иди в ${RUNBOOK}»"; fi
[ -f "$RUNBOOK" ] && [ -f "$SCRIPT" ] || { fail clone "в клоне нет $RUNBOOK или $SCRIPT"; finish; }

# ---------- 3 syntax ----------
bad=""; for f in $(git ls-files 'tools/*.sh' 'tools/**/*.sh'); do bash -n "$f" 2>/dev/null || bad="$bad $f"; done
[ -z "$bad" ] && pass syntax "bash -n: $(git ls-files 'tools/*.sh' 'tools/**/*.sh' | wc -l | tr -d ' ') файлов" || fail syntax "bash -n падает:$bad"
PY="$(command -v python3 2>/dev/null)"
if [ -n "$PY" ]; then bad=""; for f in $(git ls-files "$KIT/*.py" "$KIT/**/*.py"); do "$PY" -c 'import sys,ast; ast.parse(open(sys.argv[1],encoding="utf-8").read())' "$f" 2>/dev/null || bad="$bad $f"; done
  [ -z "$bad" ] && pass syntax "python: $(git ls-files "$KIT/*.py" "$KIT/**/*.py" | wc -l | tr -d ' ') файлов разобраны" || fail syntax "python не разбирается:$bad"
else skp syntax "python3 не найден: помощники Telegram не разобраны"; fi

# ---------- 4 identity ----------
scan() { # scan <каталог> <файлы...>: печатает «класс<TAB>файл:строка:совпадение». Значения совпадений видны только с --verbose.
  local root="$1"; shift; local f
  ( cd "$root" && for f in "$@"; do [ -f "$f" ] || continue
    g -n -o -E '/Users/[A-Za-z0-9._-]+' "$f" | sed "s#^#home-path	$f:#"
    g -n -o -E '[A-Za-z0-9._%+-]+@[A-Za-z0-9-]+(\.[A-Za-z0-9-]+)*\.[A-Za-z]{2,}' "$f" | g -v -E '@example\.com$' | g -v -E ':git@github\.com$' | sed "s#^#email	$f:#"
    g -n -o -E '(^|[^0-9.])[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}([^0-9.]|$)' "$f" | g -v -E '[^0-9.]?(127\.0\.0\.1|0\.0\.0\.0|192\.0\.2\.[0-9]+|198\.51\.100\.[0-9]+|203\.0\.113\.[0-9]+)[^0-9.]?$' | sed "s#^#ip	$f:#"
    g -n -o -E '[A-Z2-7]{7}(-[A-Z2-7]{7}){7}' "$f" | g -v -E ':(A{7}-B{7}-C{7}-D{7}-E{7}-F{7}-G{7}-H{7}|Z{7}(-Z{7}){7})$' | sed "s#^#device-id	$f:#"
    g -n -o -E -e '-100[0-9]{10}([^0-9]|$)' -e '(^|[^0-9A-Za-z-])-[0-9]{9,}([^0-9]|$)' "$f" | sed "s#^#chat-id	$f:#"
    g -n -o -E -e 'gh[pousr]_[A-Za-z0-9]{20,}' -e 'github_pat_[A-Za-z0-9_]{20,}' -e 'sk-[A-Za-z0-9_-]{20,}' -e 'xox[abp]-[A-Za-z0-9-]{10,}' -e '[0-9]{8,10}:[A-Za-z0-9_-]{35}' -e '-----BEGIN [A-Z ]*PRIVATE KEY-----' -e 'TELEGRAM_SESSION_STRING=1[A-Za-z0-9+/=_-]{40,}' "$f" | sed "s#^#secret	$f:#"
    if [ -n "${SMOKE_PRIVATE_PATTERNS:-}" ] && [ -f "$SMOKE_PRIVATE_PATTERNS" ]; then g -v -e '^#' -e '^$' "$SMOKE_PRIVATE_PATTERNS" >"$TMP/private.pat"; [ -s "$TMP/private.pat" ] && g -n -o -i -F -f "$TMP/private.pat" "$f" | sed "s#^#private	$f:#"; fi
  done ); return 0; }
# контроль зрячести: подложенный файл с одной строкой на каждый класс (значения собраны из кусков, чтобы сам этот файл не совпал)
mkdir -p "$TMP/ctl"; { printf '%s\n' "path /Us""ers/controlname/x" "mail control""@""corp.invalid" "ip 10.""11.12.13" "id ABCDEFG""-2345672-ABCDEFG-2345672-ABCDEFG-2345672-ABCDEFG-2345672" "chat -10""01234567890" "key gh""p_0123456789abcdefghijABCDEFGHIJ"; } >"$TMP/ctl/control.txt"
ctl="$(scan "$TMP/ctl" control.txt | cut -f1 | LC_ALL=C sort -u | tr '\n' ' ')"
if [ "$ctl" = "chat-id device-id email home-path ip secret " ]; then pass identity "прибор зрячий: в контрольном файле найдены все 6 классов"
else fail identity "прибор слеп: в контрольном файле найдено только: ${ctl:-ничего}"; fi
FILES="$(git ls-files $SCOPE)"
g -q -F 'onboard-intel-mac' $RUNBOOK 2>/dev/null && [ -n "$FILES" ] && pass identity "контрольная строка в рунбуке найдена; файлов набора: $(printf '%s\n' "$FILES" | wc -l | tr -d ' ')" || fail identity "контрольная строка в рунбуке не найдена: поиск ничего не доказывает"
scan "$C" $FILES >"$TMP/identity.txt"
n="$(wc -l <"$TMP/identity.txt" | tr -d ' ')"
if [ "$n" = 0 ]; then pass identity "констант личности и секретов в файлах набора: 0"
else fail identity "констант личности и секретов: $n (по классам: $(cut -f1 "$TMP/identity.txt" | LC_ALL=C sort | uniq -c | awk '{printf "%s=%s ", $2, $1}'))"
  if [ "$VERBOSE" = 1 ]; then cat "$TMP/identity.txt"; else cut -f2 "$TMP/identity.txt" | cut -d: -f1 | LC_ALL=C sort | uniq -c | sed 's/^/        /'; fi; fi
[ -n "${SMOKE_PRIVATE_PATTERNS:-}" ] && [ -f "${SMOKE_PRIVATE_PATTERNS}" ] && pass identity "закрытый список подключён: $(g -c -v -e '^#' -e '^$' "$SMOKE_PRIVATE_PATTERNS") строк" || skp identity "закрытый список имён (SMOKE_PRIVATE_PATTERNS) не подключён: проверены только общие классы"

# ---------- 5 profile ----------
run_kit() { env -i HOME="$H" PATH=/usr/bin:/bin:/usr/sbin:/sbin LANG=en_US.UTF-8 "$@" >"$TMP/kit.out" 2>&1; }
run_kit /bin/bash "$SCRIPT" --dry-run github; rc=$?
[ "$rc" = 3 ] && pass profile "без профиля скрипт не стартует (код 3)" || fail profile "без профиля код $rc (ждали 3): скрипт стартует на значениях по умолчанию"
if [ -f "$KIT/profile.example.env" ]; then run_kit /bin/bash "$SCRIPT" --profile "$KIT/profile.example.env" --dry-run github; rc=$?
  [ "$rc" = 3 ] && pass profile "профиль-образец отвергнут (код 3)" || fail profile "профиль-образец принят: код $rc (ждали 3)"
else fail profile "нет $KIT/profile.example.env"; fi

# ---------- 6 runbook ----------
MARK='<!-- smoke:stop'
g -q -F -e "$MARK" "$RUNBOOK" && pass runbook "маркер границы «${MARK}» есть" || fail runbook "в рунбуке нет маркера «${MARK}»: неизвестно, где кончаются команды без сети (выполняю только до первого вызова скрипта онбординга)"
awk -v mark="$MARK" 'index($0, mark){exit} /^```bash[[:space:]]*$/{inb=1; next} /^```[[:space:]]*$/{inb=0; next} inb{print}' "$RUNBOOK" >"$TMP/cmds.txt"
total=0; ran=0; stop=""
while IFS= read -r line || [ -n "$line" ]; do
  [ -n "${line//[[:space:]]/}" ] || continue; case "$line" in '#'*) continue;; esac
  total=$((total+1))
  # до границы допустимы только команды без сети и без изменений вне одноразового HOME
  if printf '%s\n' "$line" | g -q -E '(^|[;&|[:space:]])(sudo|curl|brew|npm|open|launchctl|git[[:space:]]+clone|gh[[:space:]]+auth)([[:space:]]|$)'; then fail runbook "команда $total до границы трогает сеть или систему, не выполняю: ${line:0:80}"; stop=deny; break; fi
  if printf '%s\n' "$line" | g -q -F 'onboard-intel-mac.sh' && ! printf '%s\n' "$line" | g -q -e '--dry-run'; then fail runbook "команда $total до границы запускает онбординг без --dry-run, не выполняю: ${line:0:80}"; stop=deny; break; fi
  ( cd "$C" && env -i HOME="$H" PATH=/usr/bin:/bin:/usr/sbin:/sbin LANG=en_US.UTF-8 /bin/zsh -f -c "$line" ) >"$TMP/cmd.out" 2>&1; rc=$?
  ran=$((ran+1))
  [ "$VERBOSE" = 1 ] && { printf '    $ %s\n' "$line"; sed 's/^/      /' "$TMP/cmd.out"; }
  if [ "$rc" != 0 ]; then fail runbook "команда $total упала с кодом $rc: ${line:0:100}"; printf '        %s\n' "$(g -v '^$' "$TMP/cmd.out" | tail -1 | sed "s#$TMP#<tmp>#g")"; stop=fail; break; fi
  # единственная подстановка: «человек заполнил профиль»
  if printf '%s\n' "$line" | g -q -F 'profile.example.env' && [ -f "$KIT/tests/fixtures/profile.smoke.env" ]; then
    dst="$(find "$H" -maxdepth 1 -name '*.env' -newer "$TMP/cmds.txt" | head -1)"; [ -n "$dst" ] && cp "$KIT/tests/fixtures/profile.smoke.env" "$dst"; fi
  if ! g -q -F -e "$MARK" "$RUNBOOK" && printf '%s\n' "$line" | g -q -F 'onboard-intel-mac.sh'; then break; fi
done <"$TMP/cmds.txt"
if [ -z "$stop" ]; then [ "$ran" -gt 0 ] && pass runbook "команд до границы: $total, выполнено дословно: $ran, все с кодом 0" || fail runbook "до границы нет ни одной команды: рунбук не проверен"; fi

# ---------- 7 patches ----------
val() { sed -n "s/^$1=\\([^ ;#]*\\).*/\\1/p" "$SCRIPT" | head -1; }
UP_URL="$(val TGMCP_URL)"; UP_SHA="$(val TGMCP_SHA)"; PT_URL="$(val TGKIT_URL)"; PT_SHA="$(val TGKIT_SHA)"; PT_FILE="$(val TGKIT_PATCH)"
if ! printf '%s\n%s\n' "$UP_SHA" "$PT_SHA" | g -c -x -E '[0-9a-f]{40}' | g -q -x 2; then fail patches "в скрипте нет закреплённых коммитов апстрима и набора патчей (TGMCP_SHA, TGKIT_SHA): патч накладывается на что придётся"
else pass patches "коммиты закреплены: апстрим ${UP_SHA:0:12}, патчи ${PT_SHA:0:12}"
  src_up="${MIR_UP:-$UP_URL}"; src_pt="${MIR_PATCH:-$PT_URL}"
  if [ "$OFFLINE" = 1 ] && { [ -z "$MIR_UP" ] || [ -z "$MIR_PATCH" ]; }; then skp patches "--offline без зеркал: git apply --check на закреплённых коммитах не выполнен"
  elif git clone -q "$src_up" "$TMP/up" 2>"$TMP/git.err" && git -C "$TMP/up" checkout -q "$UP_SHA" 2>>"$TMP/git.err" && git clone -q "$src_pt" "$TMP/pt" 2>>"$TMP/git.err" && git -C "$TMP/pt" checkout -q "$PT_SHA" 2>>"$TMP/git.err"; then
    # строго без --3way: «git apply --check --3way» отвечает 0 и там, где настоящее наложение оставляет маркеры конфликта
    if git -C "$TMP/up" apply --check --include='telegram_mcp/tools/chats.py' --include='telegram_mcp/tools/messages.py' "$TMP/pt/$PT_FILE" 2>"$TMP/apply.err"; then pass patches "git apply --check: $PT_FILE ложится чисто на ${UP_SHA:0:12} (chats.py, messages.py)"
    else fail patches "патч $PT_FILE НЕ ложится чисто на ${UP_SHA:0:12}: $(head -1 "$TMP/apply.err" | sed 's/^error: //')"; fi
  else fail patches "закреплённый коммит не получен: $(tail -1 "$TMP/git.err")"; fi; fi

# ---------- 8 links ----------
# Проверяется ПОЛНЫЙ адрес: и ветка, и файл (blob/HEAD с несуществующим файлом даёт 404 так же, как неверная ветка).
url_ok() { [ "$(curl -s -o /dev/null -L -m 20 -w '%{http_code}' "$1" 2>/dev/null)" = 200 ]; }
git ls-files '*.md' | while IFS= read -r f; do g -o -E 'https://(raw\.githubusercontent\.com/[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+/[A-Za-z0-9_./%-]+|github\.com/[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+/(blob|tree)/[A-Za-z0-9_./%-]+)' "$f"; done | sed 's/[.]*$//' | LC_ALL=C sort -u >"$TMP/links.txt"
nl="$(wc -l <"$TMP/links.txt" | tr -d ' ')"
if [ "$nl" = 0 ]; then pass links "ссылок на файлы GitHub в документах: 0"
elif [ "$OFFLINE" = 1 ]; then skp links "--offline: $nl ссылок не проверены"
else ctl="$(head -1 "$TMP/links.txt" | sed -E 's#^https://github\.com/([^/]+)/([^/]+)/.*#https://github.com/\1/\2/blob/HEAD/__runbook_smoke_control_missing__.md#; s#^https://raw\.githubusercontent\.com/([^/]+)/([^/]+)/.*#https://raw.githubusercontent.com/\1/\2/HEAD/__runbook_smoke_control_missing__.md#')"
  if url_ok "$ctl"; then fail links "прибор слеп: адрес заведомо несуществующего файла отвечает 200 ($ctl)"
  else badl=""; while IFS= read -r u; do url_ok "$u" || badl="$badl $u"; done <"$TMP/links.txt"
    [ -z "$badl" ] && pass links "все $nl ссылок отвечают 200 (ветка и файл); контроль: несуществующий файл не 200" || fail links "ссылка не открывается (ветки или файла нет у адресата):$badl"; fi; fi

# ---------- 9 lint ----------
logins="$(git ls-files "$KIT/tgbus/tg_login_*.py")"
if [ -z "$logins" ]; then fail lint "логин-скрипты не найдены: проверять нечего"
else
  miss=""; for f in $logins; do g -q -F 'secret_dialog' "$f" || miss="$miss $f"; done   # контроль: дверь ввода обязана быть в каждом
  hits="$(g -n -E '(^|[^A-Za-z_])(getpass|input[[:space:]]*\()' $logins | g -v -E ':[[:space:]]*#' | g -v -E '"""|^[^:]*:[0-9]+:[^=(]*(запрещено|нельзя)' )"
  [ -z "$miss" ] && pass lint "каждый логин-скрипт берёт ввод через secret_dialog (окно macOS)" || fail lint "логин-скрипты без secret_dialog:$miss"
  [ -z "$hits" ] && pass lint "getpass и input( в логин-скриптах: 0" || { fail lint "чтение из терминала в логин-скриптах: $(printf '%s\n' "$hits" | wc -l | tr -d ' ') строк"; printf '%s\n' "$hits" | cut -d: -f1,2 | sed 's/^/        /'; }; fi
[ -x tools/secret_prompt.sh ] && pass lint "tools/secret_prompt.sh на месте" || fail lint "нет tools/secret_prompt.sh: шаги с руками оператора без двери ввода"
[ -f "$KIT/gates.tsv" ] && pass lint "список гейтов $KIT/gates.tsv на месте: $(g -c -v -e '^#' -e '^$' "$KIT/gates.tsv") строк" || fail lint "нет списка гейтов $KIT/gates.tsv"

# ---------- 10 gates ----------
for t in kill_gates.sh test_helpers.sh; do
  if [ -f "$KIT/tests/$t" ]; then KG_TMP="$TMP/kg-$t" /bin/bash "$KIT/tests/$t" >"$TMP/$t.out" 2>&1; rc=$?
    [ "$rc" = 0 ] && pass gates "$t из клона: $(tail -1 "$TMP/$t.out")" || { fail gates "$t из клона: код $rc · $(tail -1 "$TMP/$t.out")"; g -e '^  RED' -e '^  ERR' "$TMP/$t.out" | head -20 | sed 's/^/      /'; }
  else fail gates "нет $KIT/tests/$t"; fi; done
finish
