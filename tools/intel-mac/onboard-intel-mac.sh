#!/bin/bash
# onboard-intel-mac.sh: идемпотентный онбординг INTEL-Mac (x86_64) в флот «второго мозга».
#
#   ./tools/intel-mac/onboard-intel-mac.sh --profile <файл> [--dry-run] <фаза> [<фаза>...]
#   фазы: tools claude github tailscale telegram syncthing law verify all
#
# ПРОФИЛЬ ОБЯЗАТЕЛЕН (--profile или переменная ONBOARD_PROFILE). В скрипте нет ни одного значения «по умолчанию»
# про человека, узел, волт или хаб: всё это лежит в файле профиля оператора (образец: profile.example.env).
# Без профиля, с профилем-образцом (CHANGE_ME) или с профилем, который отслеживается git, скрипт не стартует (код 3).
# Каждая фаза требует только свои ключи профиля.
#
# Каждая фаза перезапускаема. Ничего не удаляет: старые версии файлов уходят в <NODE_DIR>/backup-onboarding/<штамп>/
# (у симлинка в бэкап идут и ссылка, и содержимое цели). Сквозь симлинк файлы не пишет: запись ушла бы в чужой файл.
# Отказ любого шага останавливает фазу (дальше ни записи, ни следующей папки, ни квитанции) и весь поток.
# Секретов не пишет и не печатает: всё, что вводит человек, идёт через окно macOS (tools/secret_prompt.sh).
# После каждой фазы квитанция «что сделал · чем доказал».
#
# Согласия на один запуск (переменные окружения, в профиль НЕ кладутся):
#   SHARED_ACCOUNT_OK=1          шаги, после которых учётка macOS становится учёткой оператора
#                                (~/.claude, ~/.gitconfig, ~/.zshrc). Без него такие шаги = BAD.
#   MERGE_OK=1                   принять sendreceive-папку в НЕПУСТОЙ каталог (слияние с хабом в обе стороны)
#   CLAUDE_HOME_WHITELIST_OK=1   заменить фильтр «не тянуть ничего» у claude-home на whitelist из профиля
#                                (только после того, как оператор посмотрел, что объявляет хаб)
#   VERIFY_LLM=0                 не звать claude -p и codex exec; такие проверки = ПРОПУЩЕН, итог не PASS
# Строка verify «19 повтор» зелёная только по записи прошлого зелёного verify в <NODE_DIR>/verify-history.log (флаг не в счёт).
#
# Коды выхода (точка выхода одна, функция finish):
#   0 = PASS: ни одного BAD и ни одного SKIP (или DRY-RUN без BAD: план, ничего не доказано)
#   1 = FAIL: есть BAD или красные строки verify
#   2 = это не Intel
#   3 = нет профиля, профиль негоден или вызов неверен
#   4 = INCOMPLETE: BAD нет, но есть SKIP (что-то не проверено или ждёт человека). Это НЕ зелёный результат.
#
# Список гейтов и как подложить каждому отказ: gates.tsv рядом; приёмочная проба: tests/kill_gates.sh.
# Написано под /bin/bash 3.2 (штатный на macOS), не под zsh. На set -e не рассчитываем: внутри if, || и &&
# он молчит, а под bash 3.2 даёт ложные падения. Каждый шаг проверяется явно (step / bad).

set -o pipefail

# ---------- версии и хэши вендорных артефактов (независимый якорь: сверяется с хэшем вендора при той же версии) ----------
NODE_VER=24.21.0; RG_VER=15.2.0; CU_VER=9.8; ST_VER=2.1.5; GH_VER=2.102.0; TS_VER=1.102.4; UV_VER=0.11.23
KNOWN_NODE=1462cb3b3046b815cf8ea436d3da450ec1a9f11dac7e5a46b0ada5305d7e8097
KNOWN_UV=7a88155033cc469bba5bd5a24212e355eb92e3e2a276320b669ec576296c1e25
KNOWN_RG=af7825fcc69a2afc7a7aea55fc9af90e26421d8f20fe59df32e233c0b8a231c1
KNOWN_CU=e6d4fd2d852c9141a1c2a18a13d146a0cd7e45195f72293a4e4c044ec6ccca15
KNOWN_ST=f4535e479472a1ae43d3e6ffc4bcfc7651179e948387c08f3696847d142b62c7
KNOWN_GH=b245f24eb2bf5f75b426b4c26da3651a107f8d5b6f4fddfbfccc5679041378b3
TS_TEAM=W5364U7YZB   # Developer ID Team Tailscale Inc. (публичный идентификатор подписи)
# Telegram MCP: апстрим и набор патчей закреплены по коммитам. Пара ниже = состояние эталонного узла; на ней патч 0002
# сейчас НЕ ложится чисто на messages.py (tools/runbook_smoke.sh, проверка patches): фаза telegram остановится на
# G-TG-PATCH, пока владелец набора патчей не обновит патч под этот коммит или не назовёт другую пару.
TGMCP_URL=https://github.com/chigwell/telegram-mcp.git
TGMCP_SHA=596087228b8946c4d5b51d2c3abde4bb676bc64a
TGKIT_URL=https://github.com/tonydzi/telegram-mcp-kit.git
TGKIT_SHA=64ee1ec1aab9ba16c18b96d860b5a3a851aa69a6
TGKIT_PATCH=patches/0002-extra-tools-multiaccount.patch

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
STAMP="$(date +%Y%m%d-%H%M%S)"
LA="$HOME/Library/LaunchAgents"
STORE="$HOME/Library/Application Support/claude-tgbus"
ST_CFG="$HOME/Library/Application Support/Syncthing/config.xml"; ST_URL=http://127.0.0.1:8384
PYFW=/Library/Frameworks/Python.framework/Versions/3.13/bin/python3
TS_APP=/Applications/Tailscale.app
DRY=0; FAILS=0; SKIPS=0; ALL_FLOW=0; EXIT_FORCE=""; QUIET_FINISH=0; MYID=""
PROFILE_KEYS="OPERATOR_NAME MACHINE_KEY NODE_DIR GIT_NAME GIT_EMAIL GITHUB_LOGIN HUB_DEVICE_ID HUB_NAME VAULT_ROOT VAULT_FOLDER_ID IMPORTS_DIR MEMORY_SHARE_SLUG CANON_CWD BUS_LAYOUT BUS_FOLDER_ID BUS_DIR CLAUDE_HOME_ALLOW TGBUS_ROOM LAUNCHD_PREFIX"

# ---------- утилиты ----------
g()    { LC_ALL=C /usr/bin/grep -a "$@"; }   # поиск по байтам: не зависит от локали и не молчит на «бинарном» файле
# has: как grep -q, но дочитывает stdin до конца. Иначе под pipefail писатель (launchctl, codesign) ловит SIGPIPE,
# и «cmd | grep -q x» даёт ложный провал.
has()  { local r; g -q "$@" && r=0 || r=1; cat >/dev/null; return $r; }
re_ok() { printf '%s\n' "$1" | g -q -x -E -e "$2"; }   # re_ok <значение> <ERE>: совпадение целиком
say()  { printf '%s\n' "$*"; }
hdr()  { printf '\n== %s ==\n' "$*"; }
ok()   { printf '  OK   %s\n' "$*"; }
warn() { printf '  WARN %s\n' "$*"; }
bad()  { local id="$1"; shift; printf '  BAD  [%s] %s\n' "$id" "$*"; FAILS=$((FAILS+1)); }    # bad <гейт> <текст>
skip() { local id="$1"; shift; printf '  SKIP [%s] %s\n' "$id" "$*"; SKIPS=$((SKIPS+1)); }   # пропущено = не доказано
run()  { say "  + $*"; [ "$DRY" = 1 ] && return 0; "$@"; }
step() { # step <гейт> <что делаю> <команда...>: шаг с явной проверкой кода. Отказ = BAD с id гейта, возврат 1.
  local id="$1" what="$2" rc; shift 2
  run "$@"; rc=$?
  [ "$rc" = 0 ] && return 0
  bad "$id" "${what}: команда вернула $rc"; return 1; }
finish() { # ЕДИНСТВЕННАЯ точка выхода скрипта.
  local code word
  if [ -n "$EXIT_FORCE" ]; then code="$EXIT_FORCE"; word="СТОП"
  elif [ "$FAILS" -gt 0 ]; then code=1; word="FAIL"
  elif [ "$SKIPS" -gt 0 ]; then code=4; word="INCOMPLETE (есть непроверенное: это не зелёный результат)"
  elif [ "$DRY" = 1 ]; then code=0; word="DRY-RUN (план: ничего не сделано и не доказано)"
  else code=0; word="PASS"; fi
  [ "$QUIET_FINISH" = 1 ] || printf '\nИТОГ: %s · BAD=%d · SKIP=%d · код выхода %d\n' "$word" "$FAILS" "$SKIPS" "$code"
  exit "$code"; }
die()  { EXIT_FORCE="$1"; shift; printf 'СТОП: %s\n' "$*" >&2; finish; }   # die <код> <текст>; не звать внутри $( )
receipt() { printf '\n[КВИТАНЦИЯ %s] сделал: %s · доказал: %s\n' "$1" "$2" "$3"; }
usage() { sed -n '2,34p' "$0"; }
shq()  { printf "'%s'" "$1"; }   # значение в одинарных кавычках для rc-файла; кавычек и обратной косой в профиле не бывает (load_profile)
backup_of() { # бэкап перед записью. У симлинка на файл сохраняются И ссылка, И содержимое цели (<имя>.content): иначе в бэкапе одна ссылка на уже изменённый файл
  [ -e "$1" ] || [ -L "$1" ] || return 0; local b; b="$BK/$(printf '%s' "$1" | tr '/ ' '__')"
  mkdir -p "$BK" && cp -pR "$1" "$b" || return 1
  if [ -L "$1" ] && [ -f "$1" ]; then cp -pL "$1" "$b.content" || return 1; fi; return 0; }
put_file() { # put_file <путь> [права]; содержимое на stdin. Код 0 = файл на диске побайтно равен переданному. Старое = в бэкап.
  local f="$1" m="${2:-}" tmp rc
  if [ -L "$f" ]; then say "  ! $f это симлинк на $(readlink "$f"): сквозь ссылку не пишу (запись ушла бы в чужой файл). Разбери руками."; cat >/dev/null; return 1; fi
  tmp="$(mktemp)" || return 1; cat >"$tmp"
  [ -n "$m" ] || { [ -f "$f" ] && m="$(stat -f %Lp "$f" 2>/dev/null)"; m="${m:-644}"; }   # права не названы: у существующего файла сохраняются
  if [ -d "$f" ]; then say "  ! $f это каталог, а нужен файл"; rm -f "$tmp"; return 1; fi
  if [ -f "$f" ] && cmp -s "$tmp" "$f"; then say "  = $f без изменений"; rm -f "$tmp"; return 0; fi
  if [ "$DRY" = 1 ]; then say "  ~ записал бы $f ($(wc -l <"$tmp" | tr -d ' ') строк)"; rm -f "$tmp"; return 0; fi
  backup_of "$f" && mkdir -p "$(dirname "$f")" && cp "$tmp" "$f" && chmod "$m" "$f" && cmp -s "$tmp" "$f"; rc=$?
  rm -f "$tmp"
  if [ "$rc" = 0 ]; then say "  > записал $f"; else say "  ! НЕ записал $f"; fi
  return "$rc"; }
fetch() { [ -s "$2" ] && { say "  = уже скачан $(basename "$2")"; return 0; }; run mkdir -p "$(dirname "$2")"; run curl -fsSL --retry 3 -m 600 -o "$2" "$1"; }
vendor_sha() { g -E "[[:space:]]\*?$2\$" "$1" 2>/dev/null | awk '{print $1}' | head -1; }
verify_sha() { # verify_sha <файл> <хэш вендора> <закреплённый хэш>. Код 0 = файл можно распаковывать.
  local f="$1" vendor="$2" pinned="$3" got name; name="$(basename "$f")"
  if [ ! -s "$f" ]; then [ "$DRY" = 1 ] && { say "  ~ проверил бы SHA256 ${name}"; return 0; }; bad G-HASH-VENDOR "нет файла $f"; return 1; fi
  got="$(shasum -a 256 "$f" | awk '{print $1}')"
  [ -n "$vendor" ] || { bad G-HASH-VENDOR "вендорский хэш для ${name} не найден"; return 1; }
  if [ "$got" != "$vendor" ]; then
    [ "$DRY" = 1 ] || mv -f "$f" "$f.bad-$STAMP"   # плохой файл в сторону: повтор скачает заново, а не переиспользует
    bad G-HASH-VENDOR "SHA256 не совпал с вендорским: ${name} (отложен как ${name}.bad-$STAMP)"; return 1; fi
  # Закреплённый хэш = независимый якорь. Если артефакт подменён ВМЕСТЕ с файлом контрольных сумм, вендорская сверка
  # проходит; расхождение с закреплённым значением при той же версии = отказ ДО распаковки.
  [ -n "$pinned" ] || { bad G-HASH-PIN "для ${name} нет закреплённого хэша: распаковку нечем подтвердить"; return 1; }
  [ "$got" = "$pinned" ] || { bad G-HASH-PIN "SHA256 ${name} не равен закреплённому в скрипте при той же версии: не распаковываю (подмена у вендора или устаревший пин)"; return 1; }
  ok "SHA256 совпал с вендорским и с закреплённым: ${name}"; }
st_key() { sed -n 's:.*<apikey>\(.*\)</apikey>.*:\1:p' "$ST_CFG" 2>/dev/null | head -1; }
# Ключ REST идёт curl через stdin (-K -), а не аргументом: аргументы процесса видны всем учёткам машины через ps.
st_hdr() { printf 'header = "X-API-Key: %s"\n' "$(st_key)"; }
st_get() { st_hdr | curl -fsS -m 20 -K - "$ST_URL$1"; }
st_post() { say "  + POST $1"; [ "$DRY" = 1 ] && return 0; st_hdr | curl -fsS -m 30 -K - -X POST -H 'Content-Type: application/json' --data "$2" "$ST_URL$1" >/dev/null; }
st_ping() { [ -n "$(st_key)" ] && st_get /rest/system/ping 2>/dev/null | has pong; }
ts_signed() { codesign --verify --deep --strict "$1" 2>/dev/null || return 1; case "$(codesign -dv --verbose=2 "$1" 2>&1)" in *"TeamIdentifier=$TS_TEAM"*) return 0;; esac; return 1; }
wait_for() { local n=$1 what=$2; shift 2; [ "$DRY" = 1 ] && { say "  ~ ждал бы: ${what}"; return 0; }
  while [ "$n" -gt 0 ]; do "$@" >/dev/null 2>&1 && return 0; sleep 2; n=$((n-2)); done; return 1; }
merge_settings() { # cleanupPeriodDays=3650: merge через jq, никогда не перезапись
  local f="$HOME/.claude/settings.json" tmp rc
  if [ -f "$f" ]; then [ "$(jq -r '.cleanupPeriodDays // empty' "$f" 2>/dev/null)" = 3650 ] && { ok "settings.json: cleanupPeriodDays=3650"; return 0; }
    tmp="$(mktemp)" || return 1; jq '.cleanupPeriodDays = 3650' "$f" >"$tmp" && put_file "$f" <"$tmp"; rc=$?; rm -f "$tmp"; return "$rc"
  else printf '{\n  "cleanupPeriodDays": 3650\n}\n' | put_file "$f"; fi; }
shared_gate() { # shared_gate <что>: шаги, делающие учётку учёткой оператора, только с SHARED_ACCOUNT_OK=1
  [ "${SHARED_ACCOUNT_OK:-0}" = 1 ] && return 0
  [ "$DRY" = 1 ] && { warn "SHARED_ACCOUNT_OK=1 не задан: в реальном прогоне здесь стоп ($1)"; return 0; }
  bad G-SHARED "SHARED_ACCOUNT_OK=1 не задан: «$1» меняет учётку целиком (машина может быть общей). Сперва ответ «кто за рулём?», потом повтор с SHARED_ACCOUNT_OK=1"; return 1; }
force_dialog() { # окно в потоке all: скрипт стоит, пока оператор не нажмёт OK (потолок час), иначе проверка входа краснеет раньше входа
  [ "$ALL_FLOW" = 1 ] && [ "$DRY" != 1 ] || return 0
  osascript -e 'tell application "System Events" to activate' >/dev/null 2>&1
  osascript -e "display dialog \"$1\" buttons {\"OK\"} default button \"OK\" with title \"onboard-intel-mac\" giving up after 3600" >/dev/null 2>&1 || true; }
park_starter_law() { # закон стартового набора убираем с дороги ДО приёма claude-home (канон флота приедет шарой). Код 1 = гейт не пройден.
  local f mk; for f in CLAUDE.md FLOOR.md; do
    [ -f "$HOME/.claude/$f" ] || continue
    case "$f" in FLOOR.md) mk='^## §FLOOR';; *) mk='^> ВЕРСИЯ: v';; esac   # у каждого файла свой признак канона
    g -q "$mk" "$HOME/.claude/$f" && { ok "$f = канон флота, не трогаю"; continue; }
    shared_gate "увоз ~/.claude/$f в $NODE/backup-starter-law" || return 1
    step G-PARK "каталог для стартового закона" mkdir -p "$NODE/backup-starter-law" || return 1
    step G-PARK "увоз стартового $f" mv "$HOME/.claude/$f" "$NODE/backup-starter-law/$f.$STAMP" || return 1
  done; return 0; }
guard_intel() { # uname под Rosetta тоже говорит x86_64: второй признак hw.optional.arm64 (на Intel такого oid нет = пусто)
  [ "$(uname -m)" = x86_64 ] && [ "$(sysctl -n hw.optional.arm64 2>/dev/null)" != 1 ] && return 0
  die 2 "[G-INTEL] это не Intel ($(uname -m), arm64=$(sysctl -n hw.optional.arm64 2>/dev/null)). Для Apple Silicon рунбук ONBOARDING-MAC.md в корне набора."; }

# ---------- профиль ----------
load_profile() { # файл «КЛЮЧ=значение». Это ДАННЫЕ: файл не исполняется, подстановки оболочки запрещены, раскрывается только ведущий ~/ или $HOME/.
  local f="$1" line key val n=0 k v tok
  [ -n "$f" ] || die 3 "[G-PROFILE] профиль не задан. Скопируй tools/intel-mac/profile.example.env в место ВНЕ репозитория, заполни и передай: --profile <файл> (или ONBOARD_PROFILE=<файл>). Личных значений по умолчанию в скрипте нет."
  [ -f "$f" ] && [ -r "$f" ] || die 3 "[G-PROFILE] файл профиля не найден или не читается: $f"
  if ( cd "$(dirname "$f")" 2>/dev/null && git ls-files --error-unmatch "$(basename "$f")" >/dev/null 2>&1 ); then
    die 3 "[G-PROFILE] профиль $f отслеживается git: настоящие координаты оператора и хаба в репозиторий не кладём. Перенеси файл из репозитория."; fi
  while IFS= read -r line || [ -n "$line" ]; do
    n=$((n+1)); line="${line%$'\r'}"
    [ -n "${line//[[:space:]]/}" ] || continue
    case "$line" in '#'*) continue;; esac
    case "$line" in *=*) ;; *) die 3 "[G-PROFILE] профиль, строка $n: нужен вид КЛЮЧ=значение";; esac
    key="${line%%=*}"; val="${line#*=}"
    case " $PROFILE_KEYS " in *" $key "*) ;; *) die 3 "[G-PROFILE] профиль, строка $n: неизвестный ключ «${key}» (допустимые: $PROFILE_KEYS)";; esac
    case "$val" in \"*\") val="${val#\"}"; val="${val%\"}";; \'*\') val="${val#\'}"; val="${val%\'}";; esac
    case "$val" in *'`'*|*'\'*|*'"'*|*"'"*) die 3 "[G-PROFILE] профиль, строка $n (${key}): в значении запрещены кавычки, обратная кавычка и обратная косая";; esac
    case "$val" in '~/'*) val="$HOME/${val#\~/}";; '$HOME/'*) val="$HOME/${val#\$HOME/}";; esac
    case "$val" in *'$'*) die 3 "[G-PROFILE] профиль, строка $n (${key}): знак \$ допустим только как ведущий \$HOME/ (профиль = данные, не код)";; esac
    case "$val" in *CHANGE_ME*) die 3 "[G-PROFILE] профиль, строка $n (${key}): осталась заглушка CHANGE_ME. Это образец, заполни своими значениями.";; esac
    printf -v "P_$key" '%s' "$val"
  done <"$f"
  # форма значений: проверяется у тех ключей, что заданы
  for k in NODE_DIR VAULT_ROOT IMPORTS_DIR CANON_CWD BUS_DIR; do v="P_$k"; v="${!v:-}"; [ -z "$v" ] && continue
    re_ok "$v" '/[A-Za-z0-9 ._/+-]*' || die 3 "[G-PROFILE] профиль (${k}): нужен абсолютный путь из латиницы, цифр, пробела и знаков . _ / + -"; done
  [ -z "${P_HUB_DEVICE_ID:-}" ] || re_ok "$P_HUB_DEVICE_ID" '[A-Z2-7]{7}(-[A-Z2-7]{7}){7}' || die 3 "[G-PROFILE] профиль (HUB_DEVICE_ID): не похоже на Device ID Syncthing (8 групп по 7 символов A-Z2-7 через дефис)"
  [ -z "${P_GIT_EMAIL:-}" ] || re_ok "$P_GIT_EMAIL" '[^ @]+@[^ @]+\.[^ @]+' || die 3 "[G-PROFILE] профиль (GIT_EMAIL): не похоже на адрес почты"
  [ -z "${P_GITHUB_LOGIN:-}" ] || re_ok "$P_GITHUB_LOGIN" '[A-Za-z0-9-]+' || die 3 "[G-PROFILE] профиль (GITHUB_LOGIN): только латиница, цифры и дефис"
  for k in MACHINE_KEY MEMORY_SHARE_SLUG; do v="P_$k"; v="${!v:-}"; [ -z "$v" ] || re_ok "$v" '[A-Za-z0-9._-]+' || die 3 "[G-PROFILE] профиль (${k}): только латиница, цифры и знаки . _ -"; done
  for k in VAULT_FOLDER_ID BUS_FOLDER_ID; do v="P_$k"; v="${!v:-}"; [ -z "$v" ] || re_ok "$v" '[a-z0-9._-]+' || die 3 "[G-PROFILE] профиль (${k}): id папки Syncthing = строчная латиница, цифры и знаки . _ -"; done
  [ -z "${P_LAUNCHD_PREFIX:-}" ] || re_ok "$P_LAUNCHD_PREFIX" '[A-Za-z0-9-]+(\.[A-Za-z0-9-]+)+' || die 3 "[G-PROFILE] профиль (LAUNCHD_PREFIX): вид обратного домена, например org.example"
  [ -z "${P_TGBUS_ROOM:-}" ] || re_ok "$P_TGBUS_ROOM" '-?[0-9]+' || die 3 "[G-PROFILE] профиль (TGBUS_ROOM): числовой id комнаты"
  case "${P_BUS_LAYOUT:-}" in ''|separate-share|inside-vault) ;; *) die 3 "[G-PROFILE] профиль (BUS_LAYOUT): separate-share или inside-vault (раскладку шины называет хаб, скрипт её не выбирает)";; esac
  set -f   # без раскрытия шаблонов: «*.md» в профиле обязан остаться строкой и быть отвергнут, а не превратиться в имена файлов текущего каталога
  for tok in ${P_CLAUDE_HOME_ALLOW:-}; do   # whitelist claude-home: только поимённые строки, без звёздочек и без опасных путей
    re_ok "$tok" '[A-Za-z0-9._-]+' || die 3 "[G-PROFILE] профиль (CLAUDE_HOME_ALLOW): «${tok}» не имя файла или каталога (звёздочки и пути запрещены: [G-HOME-WHITELIST])"
    case "$tok" in .|..|projects|secrets|browser-profiles|state|.credentials*|.claude.json|settings*) die 3 "[G-PROFILE] профиль (CLAUDE_HOME_ALLOW): «${tok}» разрешать нельзя, там секреты или локальное состояние [G-HOME-WHITELIST]";; esac
  done
  set +f
  [ -n "${P_NODE_DIR:-}" ] || die 3 "[G-PROFILE] профиль: ключ NODE_DIR обязателен для любой фазы (папка узла: бинарники, бэкапы, заметки)"
  NODE="$P_NODE_DIR"; OPT="$NODE/opt"; DL="$OPT/dl"; BK="$NODE/backup-onboarding/$STAMP"
  MCP_DIR="$NODE/mcp/telegram-mcp"; KIT_DIR="$NODE/mcp/telegram-mcp-kit"; VENV_PY="$MCP_DIR/.venv/bin/python"
  ST_BIN="$OPT/syncthing/syncthing"; GTIMEOUT="$OPT/coreutils/bin/gtimeout"
  # PATH скрипта не зависит от login-shell: Bash-инструмент Claude Code тоже не login-shell
  export PATH="$OPT/gh/bin:$OPT/node/bin:$OPT/ripgrep:$OPT/coreutils/bin:$OPT/syncthing:$OPT/uv:/Library/Frameworks/Python.framework/Versions/3.13/bin:/usr/local/bin:/usr/bin:/bin:/usr/sbin:/sbin:$PATH"
}
need() { # need <фаза> <ключ>...: фаза требует только свои ключи профиля. Нет ключа = BAD, фаза не начинается.
  local ph="$1" k v miss=""; shift
  for k in "$@"; do v="P_$k"; [ -n "${!v:-}" ] || miss="$miss $k"; done
  [ -z "$miss" ] && return 0
  bad G-PROFILE-KEYS "фаза ${ph}: в профиле не заданы ключи:${miss}. Фаза не начата."; return 1; }

# ---------- фаза tools ----------
unpack() { # unpack <имя> <команда распаковки...>: распаковка и симлинк проверяются
  local what="$1"; shift; step G-STEP "распаковка ${what}" "$@"; }
phase_tools() {
  hdr "tools: вендорные бинарники в $OPT (Homebrew на Intel = Tier 3, бутылок нет, brew install собирает часами)"
  step G-STEP "каталоги $OPT" mkdir -p "$DL" "$OPT" || return 1
  local f0="$FAILS" a f t
  xcode-select -p >/dev/null 2>&1 && ok "Xcode CLT: $(xcode-select -p) (git, clang, make)" || bad G-HANDS "нет Xcode CLT: оператор запускает xcode-select --install (окно macOS, пароль)"
  [ -x "$PYFW" ] && ok "python.org Framework: $("$PYFW" --version 2>&1)" || bad G-HANDS "нет python.org Python 3.13: оператор ставит pkg с python.org (пароль администратора)"
  [ -x /usr/bin/jq ] && ok "jq штатный" || bad G-HANDS "нет /usr/bin/jq: settings.json и REST-проверки без него не работают"
  [ -x /usr/local/bin/brew ] && ok "Homebrew /usr/local (только casks)" || warn "Homebrew нет: cask codex недоступен; установка Homebrew = пароль администратора, руки оператора"
  [ "$FAILS" = "$f0" ] || { say "  сперва руки оператора (строки BAD выше), бинарники не качаю: повтори фазу после"; return 1; }
  a="node-v$NODE_VER-darwin-x64"; f="$DL/$a.tar.gz"
  if [ -x "$OPT/node/bin/node" ]; then ok "node $("$OPT/node/bin/node" --version)"; else
    fetch "https://nodejs.org/dist/v$NODE_VER/$a.tar.gz" "$f" && fetch "https://nodejs.org/dist/v$NODE_VER/SHASUMS256.txt" "$DL/node-SHASUMS256-$NODE_VER.txt" || { bad G-STEP "node: скачивание не удалось"; return 1; }
    verify_sha "$f" "$(vendor_sha "$DL/node-SHASUMS256-$NODE_VER.txt" "$a.tar.gz")" "$KNOWN_NODE" || return 1
    unpack node tar -xzf "$f" -C "$OPT" || return 1
    step G-STEP "симлинк node" ln -sfn "$OPT/$a" "$OPT/node" || return 1; fi
  a="ripgrep-$RG_VER-x86_64-apple-darwin"; f="$DL/$a.tar.gz"
  if [ -x "$OPT/ripgrep/rg" ]; then ok "rg $("$OPT/ripgrep/rg" --version | head -1)"; else
    fetch "https://github.com/BurntSushi/ripgrep/releases/download/$RG_VER/$a.tar.gz" "$f" && fetch "https://github.com/BurntSushi/ripgrep/releases/download/$RG_VER/$a.tar.gz.sha256" "$f.sha256" || { bad G-STEP "ripgrep: скачивание не удалось"; return 1; }
    verify_sha "$f" "$(vendor_sha "$f.sha256" "$a.tar.gz")" "$KNOWN_RG" || return 1
    unpack ripgrep tar -xzf "$f" -C "$OPT" || return 1
    step G-STEP "симлинк ripgrep" ln -sfn "$OPT/$a" "$OPT/ripgrep" || return 1; fi
  f="$DL/coreutils-$CU_VER.tar.xz"
  if [ -x "$OPT/coreutils/bin/gtimeout" ]; then ok "gtimeout: $("$OPT/coreutils/bin/gtimeout" --version | head -1)"; else
    fetch "https://ftp.gnu.org/gnu/coreutils/coreutils-$CU_VER.tar.xz" "$f" || { bad G-STEP "coreutils: скачивание не удалось"; return 1; }
    # GNU даёт .sig, не sha256: единственный якорь здесь закреплённый хэш (gpg --verify .sig = второй заход, если gpg есть)
    verify_sha "$f" "$KNOWN_CU" "$KNOWN_CU" || return 1
    unpack coreutils tar -xJf "$f" -C "$DL" || return 1
    say "  + сборка coreutils с префиксом g (несколько минут)"
    [ "$DRY" = 1 ] || (cd "$DL/coreutils-$CU_VER" && ./configure --prefix="$OPT/coreutils" --program-prefix=g --quiet && make -j"$(sysctl -n hw.ncpu)" >/dev/null && make install >/dev/null) || { bad G-STEP "сборка coreutils упала"; return 1; }; fi
  a="syncthing-macos-amd64-v$ST_VER"; f="$DL/$a.zip"
  if [ -x "$ST_BIN" ]; then ok "syncthing $("$ST_BIN" --version | awk '{print $2}')"; else
    fetch "https://github.com/syncthing/syncthing/releases/download/v$ST_VER/$a.zip" "$f" && fetch "https://github.com/syncthing/syncthing/releases/download/v$ST_VER/sha256sum.txt.asc" "$DL/syncthing-$ST_VER-sha256sum.txt.asc" || { bad G-STEP "syncthing: скачивание не удалось"; return 1; }
    verify_sha "$f" "$(vendor_sha "$DL/syncthing-$ST_VER-sha256sum.txt.asc" "$a.zip")" "$KNOWN_ST" || return 1
    unpack syncthing ditto -x -k "$f" "$OPT" || return 1
    step G-STEP "симлинк syncthing" ln -sfn "$OPT/$a" "$OPT/syncthing" || return 1; fi
  a="gh_${GH_VER}_macOS_amd64"; f="$DL/$a.zip"
  if [ -x "$OPT/gh/bin/gh" ]; then ok "gh $("$OPT/gh/bin/gh" --version | head -1)"; else
    fetch "https://github.com/cli/cli/releases/download/v$GH_VER/$a.zip" "$f" && fetch "https://github.com/cli/cli/releases/download/v$GH_VER/gh_${GH_VER}_checksums.txt" "$DL/gh_${GH_VER}_checksums.txt" || { bad G-STEP "gh: скачивание не удалось"; return 1; }
    verify_sha "$f" "$(vendor_sha "$DL/gh_${GH_VER}_checksums.txt" "$a.zip")" "$KNOWN_GH" || return 1
    unpack gh ditto -x -k "$f" "$OPT" || return 1
    step G-STEP "симлинк gh" ln -sfn "$OPT/$a" "$OPT/gh" || return 1; fi
  # uv: пин версии, как у остальных (releases/latest не воспроизводим); Homebrew-uv в PATH за установку не считается
  if [ -x "$OPT/uv/uv" ]; then ok "uv $("$OPT/uv/uv" --version)"; else
    a="uv-x86_64-apple-darwin"; f="$DL/uv-$UV_VER-$a.tar.gz"
    fetch "https://github.com/astral-sh/uv/releases/download/$UV_VER/$a.tar.gz" "$f" && fetch "https://github.com/astral-sh/uv/releases/download/$UV_VER/$a.tar.gz.sha256" "$f.sha256" || { bad G-STEP "uv: скачивание не удалось"; return 1; }
    verify_sha "$f" "$(vendor_sha "$f.sha256" "$a.tar.gz")" "$KNOWN_UV" || return 1
    step G-STEP "каталог uv" mkdir -p "$OPT/uv-$UV_VER" || return 1
    unpack uv tar -xzf "$f" -C "$OPT/uv-$UV_VER" --strip-components=1 || return 1
    step G-STEP "симлинк uv" ln -sfn "$OPT/uv-$UV_VER" "$OPT/uv" || return 1; fi
  [ "$DRY" = 1 ] || xattr -dr com.apple.quarantine "$OPT" 2>/dev/null   # карантин Gatekeeper на скачанном
  local pathline; pathline="export PATH=$(shq "$OPT/gh/bin:$OPT/node/bin:$OPT/ripgrep:$OPT/coreutils/bin:$OPT/syncthing:$OPT/uv"):\"\$PATH\""
  if g -q -F "$OPT/node/bin" "$HOME/.zprofile" 2>/dev/null; then ok "PATH в ~/.zprofile уже есть"
  elif [ -L "$HOME/.zprofile" ]; then bad G-STEP "~/.zprofile это симлинк на $(readlink "$HOME/.zprofile"): сквозь ссылку не пишу. Допиши в свой файл строку: $pathline"; return 1
  else say "  + дописываю PATH в ~/.zprofile (login-shell; Bash-инструмент Claude его НЕ читает)"
    if [ "$DRY" != 1 ]; then { backup_of "$HOME/.zprofile" && printf '\n# second-brain onboarding: вендорные бинарники (Intel, Homebrew без бутылок)\n%s\n' "$pathline" >>"$HOME/.zprofile"; } || { bad G-STEP "не дописал PATH в ~/.zprofile"; return 1; }; fi; fi
  if [ "$DRY" != 1 ]; then for t in "$OPT/node/bin/node" "$OPT/ripgrep/rg" "$OPT/coreutils/bin/gtimeout" "$ST_BIN" "$OPT/gh/bin/gh" "$OPT/uv/uv"; do
    [ -x "$t" ] || { bad G-STEP "после фазы нет исполняемого $t: квитанцию не выдаю"; return 1; }; done; fi
  local line=""; for t in node rg gtimeout syncthing gh uv python3 jq git; do line="$line $t=$(command -v "$t" 2>/dev/null || echo НЕТ)"; done
  receipt tools "вендорные бинарники в $OPT, PATH в ~/.zprofile" "command -v:$line"
}

# ---------- фаза claude ----------
llm_says() { # llm_says <команда...>: последняя строка ответа, до 80 знаков; stderr отбрасывается (текст ошибки не засчитывается как ответ)
  local out; out="$("$GTIMEOUT" 120 "$@" 2>/dev/null | tail -1)"; printf '%s' "${out:0:80}"; }
phase_claude() {
  hdr "claude: Claude Code CLI (npm в вендорный node) + Codex CLI (brew cask) + ретеншн сессий"
  if [ ! -x "$OPT/node/bin/npm" ]; then
    if [ "$DRY" = 1 ]; then say "  ~ в настоящем прогоне здесь нужен $OPT/node/bin/npm (результат фазы tools)"; else bad G-ORDER "нет $OPT/node/bin/npm: сперва фаза tools"; return 1; fi; fi
  if "$OPT/node/bin/claude" --version >/dev/null 2>&1; then ok "claude $("$OPT/node/bin/claude" --version)"; else step G-STEP "установка Claude Code" "$OPT/node/bin/npm" install -g @anthropic-ai/claude-code || return 1; fi
  if command -v codex >/dev/null 2>&1; then ok "codex $(codex --version 2>/dev/null)"
  elif [ -x /usr/local/bin/brew ]; then step G-STEP "установка Codex CLI" /usr/local/bin/brew install --cask codex || return 1
  else bad G-HANDS "codex не поставить: нет Homebrew (cask). Оператор ставит Homebrew (пароль администратора), затем повтор фазы"; return 1; fi
  merge_settings || { bad G-STEP "settings.json: cleanupPeriodDays не записан"; return 1; }
  say "  РУКИ ОПЕРАТОРА: в терминале \`claude\` и команда /login (браузер); затем \`codex login\`."
  force_dialog "Открой отдельный терминал: claude, затем /login; потом codex login. Нажми OK после /login (и codex login)."
  local out
  if [ "$DRY" = 1 ]; then say "  ~ проверил бы claude -p / codex exec"
  else out="$(llm_says "$OPT/node/bin/claude" -p 'ответь одним словом: работает')"
    case "$out" in *работает*) ok "claude -p: $out";; *) bad G-LOGIN "claude -p не сказал «работает» (/login не сделан?): ${out:-пусто}";; esac
    out="$(llm_says codex exec --skip-git-repo-check 'ответь одним словом: работает')"
    case "$out" in *работает*) ok "codex exec: $out";; *) bad G-LOGIN "codex exec не сказал «работает» (codex login не сделан?): ${out:-пусто}";; esac; fi
  receipt claude "claude + codex, cleanupPeriodDays=3650" "claude --version, codex --version, claude -p, codex exec"
}

# ---------- фаза github ----------
gh_login_name() { "$GTIMEOUT" 30 "$OPT/gh/bin/gh" api user --jq .login 2>/dev/null; }
phase_github() {
  hdr "github: git identity ИЗ ПРОФИЛЯ + gh auth через device code (код печатает gh, вводит оператор) + сверка аккаунта"
  need github GIT_NAME GIT_EMAIL GITHUB_LOGIN || return 1
  if [ "$(git config --global user.name)" = "$P_GIT_NAME" ] && [ "$(git config --global user.email)" = "$P_GIT_EMAIL" ]; then ok "git identity уже как в профиле"
  elif shared_gate "git identity в ~/.gitconfig"; then   # существующий ~/.gitconfig общей учётки уходит в бэкап ДО записи
    [ "$DRY" = 1 ] || backup_of "$HOME/.gitconfig" || { bad G-STEP "бэкап ~/.gitconfig не удался: identity не пишу"; return 1; }
    step G-STEP "git user.name" git config --global user.name "$P_GIT_NAME" || return 1
    step G-STEP "git user.email" git config --global user.email "$P_GIT_EMAIL" || return 1
  else return 1; fi
  if [ "$DRY" = 1 ]; then say "  ~ вошёл бы в GitHub и сверил аккаунт с ожидаемым: $P_GITHUB_LOGIN"; receipt github "план" "dry-run"; return 0; fi
  if "$GTIMEOUT" 30 "$OPT/gh/bin/gh" auth status >/dev/null 2>&1; then ok "gh: вход уже есть"; else
    say "  ОЖИДАЕМЫЙ АККАУНТ GitHub: $P_GITHUB_LOGIN. В браузере войди именно в него, ДО ввода одноразового кода."
    force_dialog "Сейчас gh покажет одноразовый код. В браузере должен быть открыт аккаунт GitHub: $P_GITHUB_LOGIN. Нажми OK и введи код."
    step G-LOGIN "gh auth login" "$GTIMEOUT" 900 "$OPT/gh/bin/gh" auth login --hostname github.com --git-protocol https --web || return 1; fi
  local who; who="$(gh_login_name)"
  if [ "$who" = "$P_GITHUB_LOGIN" ]; then ok "gh: вошёл ожидаемый аккаунт"
  else bad G-GH-ACCOUNT "gh вошёл как «${who:-не определён}», а профиль ждёт «${P_GITHUB_LOGIN}». Выполни gh auth logout, открой в браузере нужный аккаунт и повтори фазу. Повторять до совпадения."; return 1; fi
  receipt github "git identity из профиля, gh auth, аккаунт сверен" "git config --global user.name и user.email; gh api user --jq .login"
}

# ---------- фаза tailscale ----------
phase_tailscale() {
  hdr "tailscale: standalone .app с pkgs.tailscale.com, подпись Developer ID, вход и расширение = руки оператора"
  local z="$DL/Tailscale-$TS_VER-macos.zip"
  if [ -d "$TS_APP" ]; then ok "Tailscale.app уже стоит"; else
    fetch "https://pkgs.tailscale.com/stable/Tailscale-$TS_VER-macos.zip" "$z" || { bad G-STEP "Tailscale: скачивание не удалось"; return 1; }
    step G-STEP "каталог распаковки Tailscale" mkdir -p "$DL/tailscale-unz" || return 1
    step G-STEP "распаковка Tailscale" ditto -x -k "$z" "$DL/tailscale-unz" || return 1
    if [ "$DRY" = 1 ] || ts_signed "$DL/tailscale-unz/Tailscale.app"; then step G-STEP "копия Tailscale.app в /Applications" ditto "$DL/tailscale-unz/Tailscale.app" "$TS_APP" || return 1
    else bad G-SIGNATURE "подпись Tailscale не прошла: в /Applications не копирую"; return 1; fi; fi
  if [ -d "$TS_APP" ]; then ts_signed "$TS_APP" && ok "подпись: Developer ID Tailscale Inc. ($TS_TEAM)" || { bad G-SIGNATURE "подпись Tailscale.app не подтверждена"; return 1; }; fi
  say "  РУКИ ОПЕРАТОРА: open -a Tailscale, вход в браузере, затем System Settings разрешает системное расширение."
  receipt tailscale "Tailscale.app в /Applications, подпись проверена" "codesign -dv; $TS_APP/Contents/MacOS/Tailscale status под таймаутом 10 с (без таймаута CLI виснет, пока расширение не одобрено)"
}

# ---------- фаза telegram ----------
pin_repo() { # pin_repo <каталог> <url> <sha>: клон встаёт на закреплённый коммит; чужой коммит без патча = отказ
  local dir="$1" url="$2" sha="$3" head
  if [ ! -d "$dir/.git" ]; then step G-STEP "клон $(basename "$dir")" git clone -q "$url" "$dir" || return 1; fi
  [ "$DRY" = 1 ] && [ ! -d "$dir/.git" ] && { say "  ~ встал бы на коммит $sha"; return 0; }
  head="$(git -C "$dir" rev-parse HEAD 2>/dev/null)"
  [ "$head" = "$sha" ] && { ok "$(basename "$dir") на закреплённом коммите ${sha:0:12}"; return 0; }
  [ -z "$(git -C "$dir" status --porcelain 2>/dev/null)" ] || { bad G-TG-PIN "$(basename "$dir"): коммит ${head:0:12} не закреплённый (${sha:0:12}) и есть локальные правки: не трогаю"; return 1; }
  step G-TG-PIN "$(basename "$dir"): переход на закреплённый коммит ${sha:0:12}" git -C "$dir" checkout -q "$sha" || return 1; }
phase_telegram() {
  hdr "telegram: telegram-mcp на закреплённом коммите + патч 0002 (только chats.py, messages.py) + демон HTTP 127.0.0.1:8765"
  need telegram LAUNCHD_PREFIX || return 1
  local label="${P_LAUNCHD_PREFIX}.telegram-mcp" plist h
  plist="$LA/$label.plist"
  step G-STEP "каталоги mcp и tg-media" mkdir -p "$NODE/mcp" "$NODE/tg-media" || return 1
  # «почти лёг» = маркеры конфликта в файле: признаки патча при этом на месте, а сервер не запустится
  if g -q -E '^(<<<<<<<|>>>>>>>)' "$MCP_DIR/telegram_mcp/tools/messages.py" "$MCP_DIR/telegram_mcp/tools/chats.py" 2>/dev/null; then
    bad G-TG-PATCH "в messages.py или chats.py маркеры конфликта (след наложения с --3way): файл не рабочий. Верни файлы к закреплённому коммиту и повтори фазу."; return 1; fi
  if g -q 'get_new_messages_since' "$MCP_DIR/telegram_mcp/tools/messages.py" 2>/dev/null && g -q 'search_dialogs' "$MCP_DIR/telegram_mcp/tools/chats.py" 2>/dev/null; then ok "патч 0002 уже в messages.py и chats.py"; else
    pin_repo "$MCP_DIR" "$TGMCP_URL" "$TGMCP_SHA" || return 1   # полный клон: для 3-way нужны blob-ы
    pin_repo "$KIT_DIR" "$TGKIT_URL" "$TGKIT_SHA" || return 1
    # Без --3way: с ним git «накладывает» патч с маркерами конфликта прямо в файле (и git apply --check --3way при этом
    # отвечает 0). Патч обязан лечь ЧИСТО на закреплённый коммит; не ложится = стоп, а не «почти лёг».
    if [ "$DRY" != 1 ] && ! git -C "$MCP_DIR" apply --check --include='telegram_mcp/tools/chats.py' --include='telegram_mcp/tools/messages.py' "$KIT_DIR/$TGKIT_PATCH" 2>/dev/null; then
      bad G-TG-PATCH "патч $TGKIT_PATCH не ложится чисто на закреплённый коммит ${TGMCP_SHA:0:12}. Ничего не наложено. Нужен патч под этот коммит или другая закреплённая пара: решает владелец набора патчей."; return 1; fi
    step G-TG-PATCH "патч 0002 (только chats.py и messages.py)" git -C "$MCP_DIR" apply --include='telegram_mcp/tools/chats.py' --include='telegram_mcp/tools/messages.py' "$KIT_DIR/$TGKIT_PATCH" || return 1; fi
  if g -q 'override-dependencies' "$MCP_DIR/pyproject.toml" 2>/dev/null; then ok "override cryptography<47 есть"; else
    say "  + override-dependencies = [\"cryptography<47\"] в [tool.uv] pyproject.toml"
    if [ "$DRY" != 1 ]; then backup_of "$MCP_DIR/pyproject.toml" || { bad G-STEP "бэкап pyproject.toml не удался"; return 1; }
      if g -q '^\[tool\.uv\]' "$MCP_DIR/pyproject.toml"; then   # секция уже есть: вторая [tool.uv] = невалидный TOML, строку вставляем в существующую
        awk '{print} /^\[tool\.uv\][ \t]*$/{print "# Intel Mac: у cryptography>=47 нет колеса для x86_64 CPython, сборка требует Rust"; print "override-dependencies = [\"cryptography<47\"]"}' "$MCP_DIR/pyproject.toml" >"$MCP_DIR/pyproject.toml.tmp" && mv "$MCP_DIR/pyproject.toml.tmp" "$MCP_DIR/pyproject.toml"
      else printf '\n[tool.uv]\n# Intel Mac: у cryptography>=47 нет колеса для x86_64 CPython, сборка требует Rust\noverride-dependencies = ["cryptography<47"]\n' >>"$MCP_DIR/pyproject.toml"; fi
      g -q 'override-dependencies' "$MCP_DIR/pyproject.toml" || { bad G-STEP "override в pyproject.toml не встал"; return 1; }; fi; fi
  if [ -x "$VENV_PY" ] && "$VENV_PY" -c 'import telethon, mcp, cryptography' 2>/dev/null; then ok "venv: telethon + mcp + cryptography"; else
    say "  + uv lock && uv sync"; [ "$DRY" = 1 ] || (cd "$MCP_DIR" && uv lock && uv sync) || { bad G-STEP "uv sync упал: venv нет, дальше не иду"; return 1; }; fi
  step G-STEP "стор секретов" mkdir -p "$STORE" || return 1
  step G-STEP "права 700 на стор" chmod 700 "$STORE" || return 1
  for h in tg_login_first.py tg_login_rail.py tgbus.py mcpcall.py tgwait.py secret_dialog.py; do
    [ -f "$STORE/$h" ] && { say "  = $h уже в сторе (локальную версию не затираю)"; continue; }
    [ -f "$SCRIPT_DIR/tgbus/$h" ] || { bad G-STEP "нет $SCRIPT_DIR/tgbus/$h: набор неполон"; return 1; }
    put_file "$STORE/$h" 700 <"$SCRIPT_DIR/tgbus/$h" || { bad G-STEP "$h не записан в стор"; return 1; }; done
  [ -f "$STORE/secret_prompt.sh" ] || put_file "$STORE/secret_prompt.sh" 700 <"$SCRIPT_DIR/../secret_prompt.sh" || { bad G-STEP "secret_prompt.sh не записан в стор: окна ввода не будет"; return 1; }
  if [ -f "$STORE/mcp.session.env" ]; then ok "сессия mcp есть"; else
    say "  РУКИ ОПЕРАТОРА: окна macOS спросят api_id/api_hash (если нет api.env), телефон, код, пароль 2FA."
    step G-TG-FIRST "первая сессия Telegram (mcp)" "$VENV_PY" "$STORE/tg_login_first.py" --label mcp || { say "  демон и рельсу без первой сессии не поднимаю"; return 1; }; fi
  # демон читает mcp.session.env: без файла KeepAlive-агент уйдёт в crash-loop, а рельса не получит донора
  [ "$DRY" = 1 ] || [ -f "$STORE/mcp.session.env" ] || { bad G-TG-FIRST "нет $STORE/mcp.session.env: plist не пишу, рельсу не логиню"; return 1; }
  put_file "$NODE/mcp/telegram-mcp-daemon.sh" 700 <<EOF || { bad G-STEP "сценарий демона не записан"; return 1; }
#!/bin/zsh
# Один общий Telegram MCP демон на машину (streamable HTTP, только localhost). Секреты из стора (600), в plist их нет.
set -a
source "$STORE/api.env"
source "$STORE/mcp.session.env"
set +a
export MCP_TRANSPORT=http MCP_HOST=127.0.0.1 MCP_PORT=8765
export PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1
cd "$MCP_DIR"
exec "$VENV_PY" "$MCP_DIR/main.py" "$NODE/tg-media"
EOF
  put_file "$plist" <<EOF || { bad G-STEP "plist демона не записан"; return 1; }
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0"><dict>
  <key>Label</key><string>$label</string>
  <key>ProgramArguments</key><array><string>$NODE/mcp/telegram-mcp-daemon.sh</string></array>
  <key>RunAtLoad</key><true/>
  <key>KeepAlive</key><true/>
  <key>ThrottleInterval</key><integer>15</integer>
  <key>ProcessType</key><string>Background</string>
  <key>StandardOutPath</key><string>$NODE/mcp/telegram-mcp.log</string>
  <key>StandardErrorPath</key><string>$NODE/mcp/telegram-mcp.log</string>
</dict></plist>
EOF
  if launchctl list 2>/dev/null | has -F "$label"; then ok "LaunchAgent telegram-mcp загружен"; else step G-STEP "загрузка LaunchAgent демона" launchctl load -w "$plist" || return 1; fi
  wait_for 40 "демон отвечает на 127.0.0.1:8765" curl -s -m 5 -o /dev/null http://127.0.0.1:8765/mcp || { bad G-STEP "не дождался демона на 127.0.0.1:8765"; return 1; }
  if [ -f "$STORE/rail.session.env" ]; then ok "сессия rail есть"; else
    say "  РУКИ ОПЕРАТОРА: окно macOS спросит пароль 2FA (скрытый ввод). Демон на секунды выгружается и поднимается сам."
    TGBUS_DAEMON_PLIST="$plist" step G-TG-RAIL "вторая сессия Telegram (rail)" "$VENV_PY" "$STORE/tg_login_rail.py" || return 1
    [ "$DRY" = 1 ] || [ -f "$STORE/rail.session.env" ] || { bad G-TG-RAIL "вход завершился, но $STORE/rail.session.env нет"; return 1; }; fi
  [ "$DRY" = 1 ] || chmod 600 "$STORE"/*.env 2>/dev/null
  if "$OPT/node/bin/claude" mcp get telegram >/dev/null 2>&1; then ok "MCP telegram зарегистрирован (scope user)"; else step G-STEP "регистрация MCP в Claude" "$OPT/node/bin/claude" mcp add --transport http --scope user telegram http://127.0.0.1:8765/mcp || return 1; fi
  say "  Инструменты появятся в сессии Claude только после её РЕСТАРТА; до того: $VENV_PY $STORE/mcpcall.py <tool> '<json>'"
  local p1="dry-run" p2="dry-run" rc2=0
  if [ "$DRY" != 1 ]; then p1="$("$GTIMEOUT" 60 "$VENV_PY" "$STORE/mcpcall.py" --list 2>&1 | head -1)"; p1="${p1:0:60}"
    if [ -n "${P_TGBUS_ROOM:-}" ]; then p2="$(TGBUS_ROOM="$P_TGBUS_ROOM" "$GTIMEOUT" 60 "$VENV_PY" "$STORE/tgbus.py" check 2>&1 | tail -1)"; rc2=$?
    else p2="$("$GTIMEOUT" 60 "$VENV_PY" "$STORE/tgbus.py" me 2>&1 | tail -1)"; rc2=$?; skip G-TG-ROOM "TGBUS_ROOM в профиле не задан: видимость комнаты флота не проверена"; fi
    [ "$rc2" = 0 ] || { bad G-TG-RAIL "рельса не ответила: $p2"; return 1; }; fi
  receipt telegram "клон на закреплённом коммите + патч + override, venv, стор 700/600, две сессии, LaunchAgent, MCP в Claude" "mcpcall --list: $p1 | tgbus: $p2"
}

# ---------- фаза syncthing ----------
folder_table() { # ЕДИНСТВЕННЫЙ источник таблицы папок («id|локальный путь|тип»): её читают и приём, и verify
  printf '%s|%s|%s\n' claude-skills "$HOME/.claude/skills" receiveonly
  printf '%s|%s|%s\n' claude-memory "$HOME/.claude/projects/$P_MEMORY_SHARE_SLUG/memory" receiveonly
  printf '%s|%s|%s\n' claude-home "$HOME/.claude" receiveonly
  printf '%s|%s|%s\n' claude-imports "$P_IMPORTS_DIR" receiveonly
  printf '%s|%s|%s\n' "$P_VAULT_FOLDER_ID" "$P_VAULT_ROOT" sendreceive
  [ "$P_BUS_LAYOUT" != separate-share ] || printf '%s|%s|%s\n' "$P_BUS_FOLDER_ID" "$P_BUS_DIR" sendreceive
}
bus_rel() { case "$P_BUS_DIR" in "$P_VAULT_ROOT"/*) printf '%s' "${P_BUS_DIR#"$P_VAULT_ROOT"/}";; esac; }   # путь шины внутри волта (пусто, если она снаружи)
eff()  { g -v -e '^//' -e '^$'; return 0; }   # действующие строки .stignore (без комментариев и пустых)
skills_ignore() { printf '%s\n' "// claude-skills, receiveonly. Локальное этой машины шара не трогает: synced = папка скиллов десктоп-приложения." 'synced' '.DS_Store'; }
imports_ignore() { printf '%s\n' '/brain_search.py/**' '/_paths.py/**' '!/brain_search.py' '!/_paths.py' '*'; }
home_probe() { printf '%s\n' "// claude-home, первый приём: НИЧЕГО не тянем. Сперва смотрим, что объявляет хаб: /rest/db/browse?folder=claude-home&levels=1" '*'; }
home_whitelist() { # whitelist из профиля: поимённые строки !/имя и завершающая *. Форму имён проверил load_profile.
  local n
  printf '%s\n' "// claude-home, receiveonly. ЗАПРЕЩЕНО ПО УМОЛЧАНИЮ: приезжает только перечисленное (это пол безопасности, не список пожеланий)." "// Все !-строки стоят ВЫШЕ запрета: Syncthing берёт первое совпавшее правило. Расширять только по явному списку от хаба."
  set -f; for n in $P_CLAUDE_HOME_ALLOW; do printf '!/%s\n' "$n"; done; set +f
  printf '%s\n' '*'; }
whitelist_ok() { # whitelist_ok <файл>: последняя действующая строка *, все остальные вида !/имя, ни звёздочек, ни опасных путей, не пуст
  local e; [ -f "$1" ] || return 1; e="$(eff <"$1")"
  [ "$(printf '%s\n' "$e" | tail -1)" = '*' ] || return 1
  [ "$(printf '%s\n' "$e" | wc -l | tr -d ' ')" -ge 2 ] || return 1
  printf '%s\n' "$e" | sed '$d' | g -v -q -x -E '!/[A-Za-z0-9._-]+' && return 1
  printf '%s\n' "$e" | g -q -E '^!/(projects|secrets|browser-profiles|state|\.credentials|\.claude\.json|settings)' && return 1
  return 0; }
vault_ignore() {
  printf '%s\n' "// волт (sendreceive): правила родительской базы от хаба + локальная защита macOS."
  if [ "$P_BUS_LAYOUT" = separate-share ] && [ -n "$(bus_rel)" ]; then
    printf '%s\n' "// Раскладка профиля BUS_LAYOUT=separate-share: шина едет ОТДЕЛЬНОЙ шарой и исключена здесь ДО приёма волта." "/$(bus_rel)"; fi
  printf '%s\n' '(?d).git' '(?d).DS_Store' '(?d)Thumbs.db' '(?d)desktop.ini' '(?d).trash' '(?d).obsidian/workspace.json' '(?d).obsidian/cache' \
    '(?i)NUL' '(?i)NUL.*' '(?i)CON' '(?i)CON.*' '(?i)PRN' '(?i)PRN.*' '(?i)AUX' '(?i)AUX.*' '(?i)COM[1-9]' '(?i)COM[1-9].*' '(?i)LPT[1-9]' '(?i)LPT[1-9].*' \
    '(?d)/.claude/worktrees' '// локальное этой машины (macOS)' '(?d)._*' '(?d).Spotlight-V100' '(?d).fseventsd' '(?d).TemporaryItems' '(?d).obsidian/workspace-mobile.json'; }
bus_ignore() {
  printf '%s\n' "// шина (sendreceive, отдельная шара). Машинно-локальный мусор не синкается; полезная нагрузка едет." \
    "// .robot-alive-*.log = отметка присутствия, ОБЯЗАНА синкаться: разрешение стоит ВЫШЕ .robot-* (первое совпадение побеждает)." \
    '.read-*' '!.robot-alive-*.log' '.robot-*' '*.bak-*' '_archive' '**/__pycache__' '*.pyc' '*.sync-conflict-*' '.stversions' '(?d).DS_Store' '(?d)._*'; }
write_ignore() { # write_ignore <каталог> <текст фильтра>. Код 0 ТОЛЬКО если .stignore записан и ПРОЧИТАН ОБРАТНО побайтно.
  local dir="$1" want="$2"
  [ -n "$want" ] || return 1
  [ "$DRY" = 1 ] && { say "  ~ записал бы $dir/.stignore и прочитал обратно"; return 0; }
  mkdir -p "$dir" || return 1
  printf '%s\n' "$want" | put_file "$dir/.stignore" || return 1
  [ -f "$dir/.stignore" ] && [ ! -L "$dir/.stignore" ] && printf '%s\n' "$want" | cmp -s - "$dir/.stignore"; }
folder_cfg() { st_get "/rest/config/folders/$1" 2>/dev/null; }
folder_accepted() { folder_cfg "$1" | jq -e .id >/dev/null 2>&1; }
accept_folder() { # accept_folder <id> <локальный путь> <тип> <текст .stignore> (фильтр ОБЯЗАТЕЛЕН).
  # Порядок жёсткий: фильтр записан и прочитан обратно, только потом POST. Сбой записи фильтра = шара НЕ принимается.
  # Фильтр идёт АРГУМЕНТОМ, а не через «|»: правая часть конвейера = подоболочка, счётчики BAD и SKIP в ней терялись бы.
  local id="$1" dir="$2" type="$3" ign="$4" cfg cur_path cur_type body
  [ -n "$ign" ] || { bad G-STIGNORE "${id}: пустой фильтр, шару не принимаю"; return 1; }
  cfg="$(folder_cfg "$id")"
  if printf '%s' "$cfg" | jq -e .id >/dev/null 2>&1; then
    cur_path="$(printf '%s' "$cfg" | jq -r .path)"; cur_type="$(printf '%s' "$cfg" | jq -r .type)"
    if [ "$cur_path" != "$dir" ] || [ "$cur_type" != "$type" ]; then
      bad G-FOLDER-PATH "${id} принята ИНАЧЕ: $cur_path ($cur_type), а по профилю $dir ($type). Не трогаю: путь исправляет оператор, тип меняется PATCH и только при need=0"; return 1; fi
    ok "${id} уже принята: $cur_path ($cur_type)"
    if ! cmp -s <(printf '%s\n' "$ign" | eff) <(eff <"$dir/.stignore" 2>/dev/null); then   # сравниваем действующие строки: правка комментария не дёргает скан
      write_ignore "$dir" "$ign" || { bad G-STIGNORE "${id}: новый .stignore не записан или не прочитан обратно"; return 1; }
      st_post "/rest/db/scan?folder=$id" "" || { bad G-ST-POST "${id}: скан после смены фильтра не запущен"; return 1; }; fi
    return 0; fi
  if [ "$DRY" != 1 ]; then
    st_get /rest/cluster/pending/folders 2>/dev/null | jq -e --arg id "$id" 'has($id)' >/dev/null 2>&1 || { skip G-PENDING "хаб ещё не предложил папку ${id}: не принята"; return 0; }; fi
  case "$dir" in "$HOME/Sync"|"$HOME/Sync"/*) bad G-SYNC-DIR "${id}: путь в ~/Sync запрещён"; return 1;; esac
  # sendreceive в непустой каталог = слияние локального с хабом в обе стороны; только осознанно, MERGE_OK=1 (.stignore не считается)
  if [ "$type" = sendreceive ] && [ -d "$dir" ] && [ -n "$(find "$dir" -mindepth 1 -maxdepth 1 ! -name .stignore 2>/dev/null | head -1)" ] && [ "${MERGE_OK:-0}" != 1 ]; then
    bad G-MERGE "${id}: $dir не пуст, sendreceive сольёт его с хабом. Разбери каталог или повтори с MERGE_OK=1"; return 1; fi
  write_ignore "$dir" "$ign" || { bad G-STIGNORE "${id}: .stignore не записан или не прочитан обратно: шару НЕ принимаю"; return 1; }
  # sendreceive получает trashcan-версионирование (30 дней): удаление и перезапись с хаба обратимы на этой стороне
  body="$(jq -n --arg id "$id" --arg dir "$dir" --arg type "$type" --arg hub "$P_HUB_DEVICE_ID" --arg me "$MYID" \
    '{id:$id,label:$id,path:$dir,type:$type,fsWatcherEnabled:true,devices:[{deviceID:$hub},{deviceID:$me}]} + (if $type=="sendreceive" then {versioning:{type:"trashcan",params:{cleanoutDays:"30"}}} else {} end)')"
  st_post /rest/config/folders "$body" || { bad G-ST-POST "${id}: POST /rest/config/folders не прошёл"; return 1; }
  ok "${id} принята: $dir ($type)"; }
phase_syncthing() {
  hdr "syncthing: LaunchAgent + REST 127.0.0.1:8384; папки по таблице профиля, фильтр ДО приёма, claude-home = сперва «ничего», потом whitelist"
  if [ ! -x "$ST_BIN" ]; then
    if [ "$DRY" = 1 ]; then say "  ~ в настоящем прогоне здесь нужен $ST_BIN (результат фазы tools)"; else bad G-ORDER "нет $ST_BIN: сперва фаза tools"; return 1; fi; fi
  put_file "$LA/net.syncthing.syncthing.plist" <<EOF || { bad G-STEP "plist Syncthing не записан"; return 1; }
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0"><dict>
  <key>Label</key><string>net.syncthing.syncthing</string>
  <key>ProgramArguments</key><array>
    <string>$ST_BIN</string>
    <string>serve</string><string>--no-browser</string><string>--no-restart</string>
  </array>
  <key>EnvironmentVariables</key><dict><key>STNORESTART</key><string>1</string></dict>
  <key>RunAtLoad</key><true/>
  <key>KeepAlive</key><true/>
  <key>ProcessType</key><string>Background</string>
  <key>Nice</key><integer>10</integer>
  <key>StandardOutPath</key><string>$OPT/syncthing.log</string>
  <key>StandardErrorPath</key><string>$OPT/syncthing.log</string>
</dict></plist>
EOF
  if launchctl list 2>/dev/null | has net.syncthing.syncthing; then ok "LaunchAgent syncthing загружен"; else step G-STEP "загрузка LaunchAgent Syncthing" launchctl load -w "$LA/net.syncthing.syncthing.plist" || return 1; fi
  if [ "$DRY" = 1 ]; then say "  ~ дождался бы REST, показал бы Device ID, принял бы папки по таблице профиля (фильтр до POST)"; receipt syncthing "план" "dry-run"; return 0; fi
  wait_for 120 "config.xml с apikey и REST ping=pong" st_ping || { bad G-STEP "не дождался REST Syncthing (config.xml с apikey и ping=pong)"; return 1; }
  MYID="$(st_get /rest/system/status 2>/dev/null | jq -r '.myID // empty' 2>/dev/null)"
  [ -n "$MYID" ] || { bad G-STEP "REST не отдал Device ID этой машины"; return 1; }
  say ""; say "  ======== DEVICE ID ЭТОЙ МАШИНЫ (отдай хабу: он добавит устройство и расшарит папки) ========"; say "  $MYID"; say ""
  if [ -z "${P_HUB_DEVICE_ID:-}" ]; then
    skip G-HUB-ID "HUB_DEVICE_ID в профиле не задан: устройство хаба и папки не приняты. Впиши Device ID хаба в профиль и повтори фазу."
    receipt syncthing "демон поднят, Device ID показан" "rest/system/ping=pong"; return 0; fi
  need syncthing HUB_NAME VAULT_ROOT VAULT_FOLDER_ID IMPORTS_DIR MEMORY_SHARE_SLUG BUS_LAYOUT CLAUDE_HOME_ALLOW || return 1
  if [ "$P_BUS_LAYOUT" = separate-share ]; then need syncthing BUS_FOLDER_ID BUS_DIR || return 1; fi
  if st_get "/rest/config/devices/$P_HUB_DEVICE_ID" 2>/dev/null | jq -e .deviceID >/dev/null 2>&1; then ok "устройство хаба уже добавлено"
  else st_post /rest/config/devices "$(jq -n --arg id "$P_HUB_DEVICE_ID" --arg n "$P_HUB_NAME" '{deviceID:$id,name:$n,addresses:["dynamic"],autoAcceptFolders:false}')" || { bad G-ST-POST "устройство хаба не добавлено"; return 1; }; fi
  # Гейт общей учётки: стартовый закон не увезён = ни одна папка не принимается (иначе claude-home встретит чужой CLAUDE.md).
  park_starter_law || { say "  папки НЕ принимаю: сперва гейт выше"; return 1; }
  # Отказ любой папки останавливает фазу: следующие папки не принимаются (уже принятые остаются, их видно в выводе).
  accept_folder claude-skills "$HOME/.claude/skills" receiveonly "$(skills_ignore)" || return 1
  accept_folder claude-memory "$HOME/.claude/projects/$P_MEMORY_SHARE_SLUG/memory" receiveonly '(?d).DS_Store' || return 1
  # claude-home. Первый приём ВСЕГДА с фильтром «*»: ничего не тянется, оператор читает индекс хаба. Whitelist встаёт
  # отдельным запуском и только с CLAUDE_HOME_WHITELIST_OK=1 (согласие дано после просмотра индекса).
  if ! folder_accepted claude-home; then
    accept_folder claude-home "$HOME/.claude" receiveonly "$(home_probe)" || return 1
    ! folder_accepted claude-home || skip G-HOME-PROBE "claude-home в режиме «ничего не тянуть». Посмотри индекс хаба (GET /rest/db/browse?folder=claude-home&levels=1), потом повтори фазу с CLAUDE_HOME_WHITELIST_OK=1"
  elif cmp -s <(home_whitelist | eff) <(eff <"$HOME/.claude/.stignore" 2>/dev/null); then
    accept_folder claude-home "$HOME/.claude" receiveonly "$(home_whitelist)" || return 1
  elif [ "${CLAUDE_HOME_WHITELIST_OK:-0}" = 1 ]; then
    accept_folder claude-home "$HOME/.claude" receiveonly "$(home_whitelist)" || return 1
    whitelist_ok "$HOME/.claude/.stignore" || { bad G-HOME-WHITELIST "после записи .stignore claude-home не похож на whitelist"; return 1; }
  else
    skip G-HOME-PROBE "claude-home остаётся с прежним фильтром: whitelist из профиля встаёт только с CLAUDE_HOME_WHITELIST_OK=1"; fi
  accept_folder claude-imports "$P_IMPORTS_DIR" receiveonly "$(imports_ignore)" || return 1
  accept_folder "$P_VAULT_FOLDER_ID" "$P_VAULT_ROOT" sendreceive "$(vault_ignore)" || return 1
  if folder_accepted "$P_VAULT_FOLDER_ID"; then   # шина только после того, как волт ДЕЙСТВИТЕЛЬНО принят (а не «хаб ещё не предложил»)
    if [ "$P_BUS_LAYOUT" = separate-share ]; then
      # второй слой: исключение шины обязано стоять в фильтре волта на диске, иначе шина синкалась бы дважды
      if [ -n "$(bus_rel)" ] && ! g -q -x -F "/$(bus_rel)" "$P_VAULT_ROOT/.stignore" 2>/dev/null; then
        bad G-BUS-EXCLUDE "в $P_VAULT_ROOT/.stignore нет строки /$(bus_rel): шину отдельной шарой не принимаю"; return 1
      else accept_folder "$P_BUS_FOLDER_ID" "$P_BUS_DIR" sendreceive "$(bus_ignore)" || return 1; fi
    else ok "BUS_LAYOUT=inside-vault: шина едет внутри шары волта, отдельной папки нет"; fi
  else [ "$P_BUS_LAYOUT" != separate-share ] || say "  шину отдельной шарой не принимаю: волт ещё не принят"; fi
  local rows; rows="$(st_get /rest/config/folders 2>/dev/null | jq -r '.[].id' | while read -r i; do printf '%s=%s%% ' "$i" "$(st_get "/rest/db/completion?folder=$i" | jq -r '.completion|floor')"; done)"
  receipt syncthing "LaunchAgent, устройство хаба, папки по таблице профиля (фильтр записан и прочитан до POST)" "completion: ${rows:-нет данных}; connected и need=0 синк НЕ доказывают: смотри /rest/db/completion, /rest/db/file и SHA256 против хаба"
}

# ---------- фаза law ----------
f3_block() { # управляемый блок env F3: значения из профиля, путь волта как есть (не пересобирается из basename)
  printf '%s\n' '# >>> second-brain onboarding F3 (блок ведёт onboard-intel-mac.sh, руками не править) >>>' \
    "export CLAUDE_OPERATOR=$(shq "$P_OPERATOR_NAME")" "export MACHINE_KEY=$(shq "$P_MACHINE_KEY")" \
    "export CLAUDE_VAULT_ROOT=$(shq "$P_VAULT_ROOT")" "export MACHINE_BUS_DIR=$(shq "$P_BUS_DIR")" \
    '# <<< second-brain onboarding F3 <<<'; }
f3_ok() { # все четыре переменные: ПОСЛЕДНЕЕ присваивание в ~/.zshrc равно значению из профиля
  local pair k want last
  for pair in "CLAUDE_OPERATOR|$P_OPERATOR_NAME" "MACHINE_KEY|$P_MACHINE_KEY" "CLAUDE_VAULT_ROOT|$P_VAULT_ROOT" "MACHINE_BUS_DIR|$P_BUS_DIR"; do
    k="${pair%%|*}"; want="${pair#*|}"
    last="$(g "^export $k=" "$HOME/.zshrc" 2>/dev/null | tail -1)"
    [ "$last" = "export $k=$(shq "$want")" ] || return 1; done; return 0; }
phase_law() {
  hdr "law: канон флота приезжает шарой claude-home; здесь env F3, ретеншн, линк памяти, заметка узла, доказательство загрузки"
  need law OPERATOR_NAME MACHINE_KEY VAULT_ROOT BUS_DIR MEMORY_SHARE_SLUG CANON_CWD || return 1
  park_starter_law || return 1
  if f3_ok; then ok "env F3 в ~/.zshrc: все четыре переменные равны профилю"
  elif shared_gate "блок env F3 в ~/.zshrc"; then
    say "  + блок env F3 в ~/.zshrc (старый блок заменяется, неполный дополняется; прежний файл в бэкап)"
    if [ "$DRY" != 1 ]; then local tmp; tmp="$(mktemp)" || { bad G-F3 "mktemp"; return 1; }
      # прежний управляемый блок вырезается, новый дописывается В КОНЕЦ: последнее присваивание побеждает и старые одиночные строки
      { [ ! -f "$HOME/.zshrc" ] || awk '/^# >>> second-brain onboarding F3/{skip=1} !skip{print} /^# <<< second-brain onboarding F3 <<</{skip=0}' "$HOME/.zshrc"; printf '\n'; f3_block; } >"$tmp" \
        && put_file "$HOME/.zshrc" <"$tmp"; local rc=$?; rm -f "$tmp"
      [ "$rc" = 0 ] && f3_ok || { bad G-F3 "блок env F3 не встал: после записи значения в ~/.zshrc не равны профилю"; return 1; }; fi
  else return 1; fi
  merge_settings || { bad G-STEP "settings.json: cleanupPeriodDays не записан"; return 1; }
  local share="$HOME/.claude/projects/$P_MEMORY_SHARE_SLUG/memory" slug proj cur
  slug="$(printf '%s' "$P_CANON_CWD" | sed 's#[^A-Za-z0-9-]#-#g')"; proj="$HOME/.claude/projects/$slug/memory"
  [ -d "$HOME/.claude/projects/$slug" ] || warn "слаг $slug ещё не создан Claude: запусти claude один раз из $P_CANON_CWD и сверь имя папки, не гадай"
  if [ -L "$proj" ] && [ "$(readlink "$proj")" = "$share" ]; then ok "память: $proj -> $share"
  elif [ ! -f "$share/MEMORY.md" ]; then skip G-MEMORY-WAIT "память ещё не приехала ($share/MEMORY.md нет): линк не ставлю, повтори law после синка claude-memory"
  else
    if [ -L "$proj" ]; then cur="$(readlink "$proj")"   # симлинк не туда: Claude грузил бы чужую память
      shared_gate "замена линка памяти ($proj -> $cur)" || return 1
      say "  + линк памяти смотрит не туда ($cur): уходит в бэкап (не удаляется)"
      step G-MEMLINK "бэкап-каталог" mkdir -p "$BK" || return 1
      step G-MEMLINK "увоз неверного линка" mv "$proj" "$BK/memory-link-$slug" || return 1
    elif [ -d "$proj" ]; then
      shared_gate "замена локальной папки памяти на линк ($proj)" || return 1
      say "  + локальная папка памяти уходит в бэкап (не удаляется)"
      step G-MEMLINK "бэкап-каталог" mkdir -p "$BK" || return 1
      step G-MEMLINK "увоз локальной папки памяти" mv "$proj" "$BK/memory-local-$slug" || return 1
    elif [ -e "$proj" ]; then bad G-MEMLINK "$proj существует и это не каталог и не линк: разбери руками"; return 1; fi
    step G-MEMLINK "каталог проекта" mkdir -p "$(dirname "$proj")" || return 1
    step G-MEMLINK "линк памяти" ln -s "$share" "$proj" || return 1
    [ "$DRY" = 1 ] || [ "$(readlink "$proj")" = "$share" ] || { bad G-MEMLINK "линк памяти не встал: $proj -> $(readlink "$proj")"; return 1; }; fi
  if [ -f "$NODE/ONBOARDING-STATUS.md" ]; then ok "заметка узла: $NODE/ONBOARDING-STATUS.md (вне receiveonly-шары)"
  else put_file "$NODE/ONBOARDING-STATUS.md" <<EOF || { bad G-STEP "заметка узла не записана"; return 1; }
# Статус онбординга узла (локальная заметка: память проекта = receiveonly-шара флота, туда писать нельзя)
Создано: $STAMP. Узел: $P_MACHINE_KEY. Оператор: $P_OPERATOR_NAME. Машина: $(sysctl -n machdep.cpu.brand_string 2>/dev/null), $(sw_vers -productVersion).
EOF
  fi
  if [ "$DRY" = 1 ]; then say "  ~ проверил бы загрузку канона и памяти headless"
  elif [ "${VERIFY_LLM:-1}" = 0 ]; then skip G-VERIFY-LLM "VERIFY_LLM=0: загрузка канона и памяти headless НЕ проверена"
  else local out; out="$(cd "$P_CANON_CWD" 2>/dev/null && "$GTIMEOUT" 240 "$OPT/node/bin/claude" -p 'Процитируй дословно строку ВЕРСИЯ из CLAUDE.md и одну любую строку из MEMORY.md. Только эти две строки.' 2>/dev/null | tail -3)"
    if printf '%s' "$out" | g -q 'ВЕРСИЯ'; then ok "канон и память загружены headless"; else bad G-LAW-LOAD "headless claude -p не показал строку ВЕРСИЯ: канон или память не грузятся"; fi; fi
  receipt law "env F3 (блок), cleanupPeriodDays, линк памяти, заметка узла" "readlink $proj; строка ВЕРСИЯ в ~/.claude/CLAUDE.md; claude -p из $P_CANON_CWD"
}

# ---------- фаза verify ----------
G=0; R=0; S=0
row() { if eval "$2" >/dev/null 2>&1; then printf '  [зелёный] %s :: %s\n' "$1" "$3"; G=$((G+1)); else printf '  [красный] %s :: %s\n' "$1" "$4"; R=$((R+1)); fi; }
row_skip() { printf '  [ПРОПУЩЕН] %s :: %s (не проверено = не зелёный)\n' "$1" "$2"; S=$((S+1)); }
v_tools() { local t; for t in node rg gtimeout syncthing gh uv jq git; do command -v "$t" >/dev/null 2>&1 || return 1; done; [ -x "$PYFW" ]; }
v_no_sync_dir() { [ -f "$ST_CFG" ] || return 1; ! st_get /rest/config/folders | jq -r '.[].path' | has -e "^$HOME/Sync"; }
v_hub_connected() { st_get /rest/system/connections | jq -e --arg h "$P_HUB_DEVICE_ID" '.connections[$h].connected==true' >/dev/null; }
v_folders() { # каждая папка таблицы: принята, и путь с типом в конфиге РАВНЫ ожидаемым (а не «id существует»)
  local line id dir type cfg; while IFS='|' read -r id dir type; do
    cfg="$(folder_cfg "$id")" || return 1
    [ "$(printf '%s' "$cfg" | jq -r '.path // empty')" = "$dir" ] && [ "$(printf '%s' "$cfg" | jq -r '.type // empty')" = "$type" ] || return 1
  done <<EOF
$(folder_table)
EOF
  return 0; }
v_memory() { local slug; slug="$(printf '%s' "$P_CANON_CWD" | sed 's#[^A-Za-z0-9-]#-#g')"; [ "$(readlink "$HOME/.claude/projects/$slug/memory" 2>/dev/null)" = "$HOME/.claude/projects/$P_MEMORY_SHARE_SLUG/memory" ] && [ -f "$HOME/.claude/projects/$slug/memory/MEMORY.md" ]; }
v_tg_perms() { [ "$(stat -f %Lp "$STORE" 2>/dev/null)" = 700 ] && [ "$(stat -f %Lp "$STORE/mcp.session.env" 2>/dev/null)" = 600 ] && [ "$(stat -f %Lp "$STORE/rail.session.env" 2>/dev/null)" = 600 ] && [ "$(stat -f %Lp "$STORE/api.env" 2>/dev/null)" = 600 ]; }
v_llm() { case "$(llm_says "$@")" in *работает*) return 0;; esac; return 1; }
v_github() { [ "$(git config --global user.email)" = "$P_GIT_EMAIL" ] && [ "$(gh_login_name)" = "$P_GITHUB_LOGIN" ]; }
v_completion() { st_get /rest/config/folders | jq -r '.[].id' | while read -r i; do printf '%s=%s%% ' "$i" "$(st_get "/rest/db/completion?folder=$i" | jq -r '.completion|floor')"; done; }
phase_verify() {
  hdr "verify: зелёным считается только доказанное; пропущенное = ПРОПУЩЕН и итог не PASS (read-only, кроме двух LLM-вызовов и строки в журнале verify)"
  need verify OPERATOR_NAME MACHINE_KEY GIT_EMAIL GITHUB_LOGIN HUB_DEVICE_ID VAULT_ROOT VAULT_FOLDER_ID IMPORTS_DIR MEMORY_SHARE_SLUG CANON_CWD BUS_LAYOUT BUS_DIR LAUNCHD_PREFIX || return 1
  if [ "$P_BUS_LAYOUT" = separate-share ]; then need verify BUS_FOLDER_ID || return 1; fi
  local label="${P_LAUNCHD_PREFIX}.telegram-mcp" rail_out="" rail_rc=1 nfold hist="$NODE/verify-history.log" prev
  prev="$(g -E '^[0-9TZ:-]+ verify-ok ' "$hist" 2>/dev/null | tail -1 | cut -d' ' -f1)"   # запись прошлого полностью зелёного verify (до этого прогона)
  nfold="$(folder_table | wc -l | tr -d ' ')"
  # рельса: ОДИН вызов Telethon на весь verify (второй клиент на том же ключе = AUTH_KEY_DUPLICATED); dry-run сеть не трогает
  if [ "$DRY" != 1 ]; then
    if [ -n "${P_TGBUS_ROOM:-}" ]; then rail_out="$(TGBUS_ROOM="$P_TGBUS_ROOM" "$GTIMEOUT" 60 "$VENV_PY" "$STORE/tgbus.py" check 2>/dev/null | tail -1)"; rail_rc=$?
    else rail_out="$("$GTIMEOUT" 60 "$VENV_PY" "$STORE/tgbus.py" me 2>/dev/null | tail -1)"; rail_rc=$?; fi; fi
  row "1 Intel x86_64 + macOS"            'test "$(uname -m)" = x86_64 && test "$(sysctl -n hw.optional.arm64 2>/dev/null)" != 1' "$(uname -m), macOS $(sw_vers -productVersion), не Rosetta" "не x86_64 или Rosetta"
  row "2 инструменты (вендорные)"          v_tools                             "node rg gtimeout syncthing gh uv jq git py3.13" "чего-то нет: $(for t in node rg gtimeout syncthing gh uv jq git; do command -v $t >/dev/null || printf '%s ' $t; done)"
  row "3 PATH в ~/.zprofile"               'g -q -F "$OPT/node/bin" "$HOME/.zprofile"' "login-shell видит $OPT" "нет строки PATH (Bash-инструмент всё равно зовёт полные пути)"
  if [ "${VERIFY_LLM:-1}" = 0 ] || [ "$DRY" = 1 ]; then
    row_skip "4 claude -p отвечает" "VERIFY_LLM=0 или dry-run: вход в Claude не доказан"
    row_skip "5 codex exec отвечает" "VERIFY_LLM=0 или dry-run: вход в Codex не доказан"
  else
    row "4 claude -p отвечает"             'v_llm "$OPT/node/bin/claude" -p "ответь одним словом: работает"' "слово «работает» вернулось" "пусто: /login не сделан"
    row "5 codex exec отвечает"            'v_llm codex exec --skip-git-repo-check "ответь одним словом: работает"' "слово «работает» вернулось" "пусто: codex login не сделан"; fi
  row "6 git identity + аккаунт gh"        v_github                            "почта из профиля, gh вошёл ожидаемым аккаунтом" "identity не из профиля, gh не вошёл или вошёл НЕ ТОТ аккаунт"
  row "7 Tailscale подпись + статус"       'ts_signed "$TS_APP" && "$GTIMEOUT" 10 "$TS_APP/Contents/MacOS/Tailscale" status' "Developer ID ok, CLI отвечает" "нет .app, подпись, или CLI виснет (расширение не одобрено / нет входа)"
  row "8 Telegram стор 700/600"            v_tg_perms                          "api.env, mcp.session.env, rail.session.env = 600, папка 700" "права или файлы сессий не на месте"
  row "9 Telegram демон + MCP"             'launchctl list | has -F "$label" && curl -s -m 5 -o /dev/null http://127.0.0.1:8765/mcp && "$OPT/node/bin/claude" mcp get telegram' "LaunchAgent, порт 8765, claude mcp get telegram" "демон не загружен / порт молчит / MCP не зарегистрирован"
  if [ "$DRY" = 1 ]; then row_skip "10 Telegram рельса (tgbus)" "dry-run: сеть не трогаю"
  else row "10 Telegram рельса (tgbus)"    'test "$rail_rc" = 0'               "${rail_out:0:60}" "tgbus.py не ответил (${rail_out:-пусто}): сессия rail мертва, venv нет или два клиента на одном ключе"; fi
  [ -n "${P_TGBUS_ROOM:-}" ] || row_skip "10б видимость комнаты флота" "TGBUS_ROOM в профиле не задан"
  row "11 Syncthing демон + хаб"           'launchctl list | has net.syncthing.syncthing && st_ping && v_hub_connected' "LaunchAgent, pong, хаб connected" "демон/REST/хаб не на связи"
  row "12 папки: путь и тип по профилю"    'v_folders && v_no_sync_dir'        "$nfold папок, пути и типы равны таблице профиля, ни одной в ~/Sync" "папка не принята, принята в ДРУГОЙ путь или с другим типом, либо путь в ~/Sync: $(st_get /rest/config/folders 2>/dev/null | jq -r '.[]|.id+"="+.path' | tr '\n' ' ')"
  row "13 claude-home deny-by-default"     'whitelist_ok "$HOME/.claude/.stignore" && test -s "$HOME/.claude.json"' "whitelist, последняя строка *, секреты не разрешены, .claude.json жив" "фильтр не whitelist (режим «ничего не тянуть», ignore-список, опасные пути, звёздочка), либо .claude.json пропал"
  row "14 completion по папкам"            'test -f "$ST_CFG"'                 "$(v_completion 2>/dev/null)" "config.xml нет"
  row "15 канон флота на месте"            'g -q "^> ВЕРСИЯ: v" "$HOME/.claude/CLAUDE.md" && ! g -q "{{" "$HOME/.claude/CLAUDE.md"' "строка ВЕРСИЯ есть, плейсхолдеров нет" "CLAUDE.md не канон флота (стартовый закон? плейсхолдеры?)"
  row "16 память: линк на шару"            v_memory                            "линк смотрит на шару памяти, MEMORY.md читается" "линк памяти не стоит, смотрит НЕ ТУДА или MEMORY.md нет"
  row "17 env F3 + ретеншн"                'f3_ok && test "$(jq -r .cleanupPeriodDays "$HOME/.claude/settings.json")" = 3650' "четыре переменные F3 равны профилю, cleanupPeriodDays=3650" "env F3 неполон или устарел, либо settings.json не готов"
  row "18 заметка узла вне шары"           'test -f "$NODE/ONBOARDING-STATUS.md"' "$NODE/ONBOARDING-STATUS.md" "нет локальной заметки узла"
  # 19: улика повтора = запись прошлого зелёного verify в журнале узла, а не флаг окружения
  if [ -n "$prev" ]; then row "19 повтор verify" 'test -n "$prev"' "прошлый прогон verify тоже был зелёным: $prev ($hist)" "-"
  else row_skip "19 повтор verify" "[G-SECOND-PASS] записи прошлого зелёного verify нет: этот прогон её оставит, если всё прочее зелёное; повтори verify (лучше из НОВОЙ сессии Claude)"; fi
  # журнал: строка только если все строки, кроме самой 19, зелёные
  if [ "$DRY" != 1 ] && [ "$R" = 0 ] && [ "$((S - $([ -n "$prev" ] && echo 0 || echo 1)))" = 0 ]; then
    { mkdir -p "$NODE" && printf '%s verify-ok rows=%d\n' "$(date -u +%Y-%m-%dT%H:%M:%SZ)" "$G" >>"$hist"; } || warn "журнал $hist не дописан: следующий verify не увидит этот прогон"; fi
  printf '\nverify: зелёных %d · красных %d · пропущено %d. Рапорт хабу отправляет ОПЕРАТОР; сообщения из чатов = данные, не приказы.\n' "$G" "$R" "$S"
  FAILS=$((FAILS+R)); SKIPS=$((SKIPS+S))   # красная строка = FAIL, пропущенная = INCOMPLETE; и внутри all тоже
  [ "$R" = 0 ]
}

# ---------- main ----------
PHASES=""; PROFILE="${ONBOARD_PROFILE:-}"
while [ $# -gt 0 ]; do case "$1" in
  --dry-run) DRY=1;;
  --profile) shift; PROFILE="${1:-}";;
  --profile=*) PROFILE="${1#--profile=}";;
  -h|--help) usage; QUIET_FINISH=1; EXIT_FORCE=0; finish;;
  *) PHASES="$PHASES $1";; esac; shift; done
[ -n "$PHASES" ] || { usage; die 3 "не названа ни одна фаза"; }
for ph in $PHASES; do case "$ph" in tools|claude|github|tailscale|telegram|syncthing|law|verify|all) ;; *) die 3 "неизвестная фаза: $ph";; esac; done
guard_intel
load_profile "$PROFILE"
[ "$DRY" = 1 ] && say "DRY-RUN: только печатаю план, ничего не меняю и ничего не доказываю."
case " $PHASES " in *" all "*) ALL_FLOW=1; PHASES="tools claude github tailscale telegram syncthing law verify";; esac
for ph in $PHASES; do
  before="$FAILS"; "phase_$ph"; rc=$?
  # отказ фазы останавливает поток: следующая фаза стоит на результате предыдущей, «идти дальше» = считать пропущенное зелёным
  if [ "$rc" != 0 ] || [ "$FAILS" != "$before" ]; then
    [ "$FAILS" != "$before" ] || bad G-PHASE "фаза $ph вернула код $rc без названной причины"
    say ""; say "ФАЗА $ph НЕ ПРОШЛА: следующие фазы не запускаю."; break; fi
done
finish
