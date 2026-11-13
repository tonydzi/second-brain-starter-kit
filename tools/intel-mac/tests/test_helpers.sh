#!/bin/bash
# test_helpers.sh: дверь ввода (tools/secret_prompt.sh) и помощники Telegram (tgbus/*.py) без человека и без сети.
#
#   tools/intel-mac/tests/test_helpers.sh [--kit <каталог tools/intel-mac>]
#
# Окно macOS заменено подменой (SECRET_PROMPT_TEST=1), Telethon заменён подставным пакетом, HOME одноразовый.
# Настоящее окно здесь НЕ показывается и не нажимается: это остаётся непроверенным (см. README).
# Коды: 0 = всё зелёное · 1 = есть RED · 2 = ошибка прибора (нет python3).
set -o pipefail
HERE="$(cd "$(dirname "$0")" && pwd)"; KIT="$(cd "$HERE/.." && pwd)"
while [ $# -gt 0 ]; do case "$1" in --kit) KIT="$(cd "$2" && pwd)"; shift 2;; *) echo "неизвестный аргумент: $1" >&2; exit 2;; esac; done
PROMPT="$KIT/../secret_prompt.sh"
g() { LC_ALL=C /usr/bin/grep -a "$@"; }
PY="$(command -v python3 2>/dev/null)"; [ -n "$PY" ] || { echo "test_helpers: нет python3" >&2; exit 2; }
if [ -n "${KG_TMP:-}" ]; then T="$KG_TMP"; mkdir -p "$T" || exit 2
else T="$(mktemp -d "${TMPDIR:-/tmp}/test_helpers.XXXXXX")" || exit 2; [ "${KG_KEEP:-0}" = 1 ] || trap 'chmod -R u+rwX "$T" 2>/dev/null; rm -rf "$T"' EXIT; fi   # свой каталог убирается на выходе
PASS=0; RED=0
good() { printf '  ok   %-18s %s\n' "$1" "$2"; PASS=$((PASS+1)); }
red()  { printf '  RED  %-18s %s\n' "$1" "$2"; RED=$((RED+1)); }
is()   { [ "$3" = "$4" ] && good "$1" "$2: $3" || red "$1" "$2: получено «$3», ждали «$4»"; }   # is <тест> <что> <получено> <ждали>
echo "test_helpers: набор $KIT · $(date -u +%Y-%m-%dT%H:%M:%SZ)"
SECRETV="$(( (RANDOM * 32768 + RANDOM) % 9000000000 + 1000000000 ))"   # подставное «набранное» значение (10 цифр, новое на каждый прогон): ищем его следы там, где его быть не должно

# ---------- secret_prompt.sh ----------
sp() { # sp <подмена окна> <GUI> -- <аргументы secret_prompt>; вывод в $T/sp.out, код в RC
  local dlg="$1" gui="$2"; shift 3
  env -i PATH=/usr/bin:/bin:/usr/sbin:/sbin LANG=en_US.UTF-8 SECRET_PROMPT_TEST=1 SECRET_PROMPT_TEST_GUI="$gui" SECRET_PROMPT_TEST_DIALOG="$dlg" MARK="$T" PSPAT="[${SECRETV:0:1}]${SECRETV:1}" /bin/bash "$PROMPT" "$@" >"$T/sp.out" 2>&1; RC=$?; }
if [ ! -f "$PROMPT" ]; then red secret_prompt "нет $PROMPT: шаги с руками оператора идут без двери ввода"
else
  rm -f "$T"/m-*; sp "printf $SECRETV" Aqua -- --visible api_id '[0-9]{5,10}' -- /bin/sh -c 'cat >"$MARK/m-got"'
  is sp-valid "код" "$RC" 0; is sp-valid "команда получила значение на stdin" "$(cat "$T/m-got" 2>/dev/null)" "$SECRETV"
  g -q -F "ok, длина 10" "$T/sp.out" && good sp-valid "в выводе «ok, длина 10»" || red sp-valid "в выводе нет «ok, длина 10»"
  g -q -F "$SECRETV" "$T/sp.out" && red sp-valid "значение попало в вывод скрипта" || good sp-valid "значения в выводе нет"
  rm -f "$T"/m-*; sp "printf abcdefghijklm" Aqua -- --visible api_id '[0-9]{5,10}' -- /bin/sh -c 'touch "$MARK/m-called"; cat >/dev/null'
  is sp-format "13 нецифровых знаков для api_id: код" "$RC" 4; [ ! -e "$T/m-called" ] && good sp-format "команда входа НЕ запущена" || red sp-format "команда входа запущена с негодным значением"
  rm -f "$T"/m-*; sp "touch \"\$MARK/m-dialog\"; printf $SECRETV" Background -- api_id '[0-9]{5,10}' -- /bin/sh -c 'touch "$MARK/m-called"; cat >/dev/null'
  is sp-nogui "нет графической сессии: код" "$RC" 3; [ ! -e "$T/m-called" ] && [ ! -e "$T/m-dialog" ] && good sp-nogui "ни окна, ни команды, ни чтения из терминала" || red sp-nogui "без GUI что-то запустилось"
  rm -f "$T"/m-*; sp "printf __CANCEL__" Aqua -- api_id '[0-9]{5,10}' -- /bin/sh -c 'touch "$MARK/m-called"; cat >/dev/null'
  is sp-cancel "отмена: код" "$RC" 2; [ ! -e "$T/m-called" ] && good sp-cancel "команда не запущена" || red sp-cancel "команда запущена после отмены"
  rm -f "$T"/m-*; sp "touch \"\$MARK/m-dialog\"; printf $SECRETV" Aqua -- api_id '[0-9]{5,10}'
  is sp-nosink "некуда отдать значение: код" "$RC" 5; [ ! -e "$T/m-dialog" ] && good sp-nosink "окно не показано" || red sp-nosink "окно показано, хотя значение некуда отдать"
  sp "printf $SECRETV" Aqua -- --fd 1 api_id '[0-9]{5,10}'; is sp-fd "--fd 1 (stdout) запрещён: код" "$RC" 5
  # значение из двух строк: regex «.+» в bash совпадает и через перевод строки, а получатель читает одну строку
  rm -f "$T"/m-*; sp "printf '123\n456'" Aqua -- --visible code '.+' -- /bin/sh -c 'touch "$MARK/m-called"; cat >/dev/null'
  is sp-newline "значение с переводом строки: код" "$RC" 4; [ ! -e "$T/m-called" ] && good sp-newline "команда не запущена" || red sp-newline "команда получила значение из двух строк"
  env -i PATH=/usr/bin:/bin LANG=en_US.UTF-8 SECRET_PROMPT_TEST=1 SECRET_PROMPT_TEST_GUI=Aqua SECRET_PROMPT_TEST_DIALOG="printf $SECRETV" /bin/bash -x "$PROMPT" --fd 7 api_id '[0-9]{5,10}' >"$T/sp.out" 2>&1 7>"$T/m-fd"; RC=$?
  is sp-fd "--fd 7 под bash -x: код" "$RC" 0; is sp-fd "значение в канале" "$(cat "$T/m-fd" 2>/dev/null)" "$SECRETV"
  g -q -F "$SECRETV" "$T/sp.out" && red sp-fd "значение утекло в трассировку bash -x" || good sp-fd "в трассировке bash -x значения нет"
  # значение не должно появляться в аргументах процессов: команда-получатель смотрит ps, пока жива
  rm -f "$T"/m-*; sp "printf $SECRETV" Aqua -- api_id '[0-9]{5,10}' -- /bin/sh -c 'cat >/dev/null; ps -axww -o args= | LC_ALL=C /usr/bin/grep -a -c -e "$PSPAT" >"$MARK/m-ps"'
  is sp-argv "процессов со значением в аргументах" "$(cat "$T/m-ps" 2>/dev/null)" 0
  # подмены окна: читаются только под «"$TEST" = 1», а TEST=1 ставится в ОДНОМ месте и только по SECRET_PROMPT_TEST=1.
  # (Живьём «подмена без флага» не проверяется: правильное поведение там = настоящее окно на экране.)
  n="$(g -c -E 'SECRET_PROMPT_TEST_(DIALOG|GUI)' "$PROMPT")"; m="$(g -E 'SECRET_PROMPT_TEST_(DIALOG|GUI)' "$PROMPT" | g -v -E '^#' | g -c -v -F '"$TEST" = 1')"
  t1="$(g -v -E '^#' "$PROMPT" | g -o -F 'TEST=1' | wc -l | tr -d ' ')"; t2="$(g -c -F 'TEST=0; [ "${SECRET_PROMPT_TEST:-0}" = 1 ] && { TEST=1;' "$PROMPT")"
  [ "$n" -gt 0 ] && [ "$m" = 0 ] && [ "$t1" = 1 ] && [ "$t2" = 1 ] && good sp-seam "подмены действуют только при SECRET_PROMPT_TEST=1" || red sp-seam "подмена окна доступна без SECRET_PROMPT_TEST=1 (строк без проверки: $m, присваиваний TEST=1: $t1)"
fi

# ---------- помощники Telegram: подставной Telethon и одноразовый HOME ----------
ST="$T/home/Library/Application Support/claude-tgbus"; rm -rf "$T/home" "$T/stub"; mkdir -p "$ST" "$T/stub/telethon" "$T/bin"
cp "$KIT"/tgbus/*.py "$ST/" 2>/dev/null; [ -f "$PROMPT" ] && cp "$PROMPT" "$ST/"
cat >"$T/stub/telethon/__init__.py" <<'EOF'
import os
def _mark(s): open(os.environ["TL_MARK"], "a").write(s + "\n")
_mark("IMPORTED")
class _Ent: title = "SECRET-ROOM-TITLE"
class TelegramClient:
    def __init__(self, *a, **k): _mark("CLIENT")
    async def __aenter__(self): return self
    async def __aexit__(self, *a): return False
    async def get_me(self): return object()
    async def get_entity(self, x): return _Ent()
class errors:
    class SessionPasswordNeededError(Exception): pass
    class PasswordHashInvalidError(Exception): pass
    class AuthTokenExpiredError(Exception): pass
class functions: pass
EOF
cat >"$T/stub/telethon/sync.py" <<'EOF'
from . import _mark
class _S:
    def save(self): return "stub-session-not-a-secret"
class TelegramClient:
    def __init__(self, *a, **k): _mark("CLIENT"); self.session = _S()
    def __enter__(self): return self
    def __exit__(self, *a): return False
    def start(self, phone=None, password=None, code_callback=None): _mark("START " + str(phone)); code_callback()
    def get_me(self): return object()
EOF
printf 'class StringSession:\n    def __init__(self, s=None): self.s = s\n' >"$T/stub/telethon/sessions.py"
# подставной osascript в PATH: для версии помощников до двери ввода (она звала osascript из PATH сама)
printf '#!/bin/bash\ncase "$*" in *activate*) exit 0;; esac\nprintf "%%s\\n" "${STUB_ANSWER:-abcdefghijklm}"\n' >"$T/bin/osascript"; chmod +x "$T/bin/osascript"
helper() { # helper <секунд> <подмена окна> <скрипт> [аргументы]: вывод в $T/h.out, код в RC (142 = таймаут)
  local secs="$1" dlg="$2" script="$3"; shift 3; : >"$T/tl.mark"
  env -i HOME="$T/home" PATH="$T/bin:/usr/bin:/bin:/usr/sbin:/sbin" LANG=en_US.UTF-8 PYTHONPATH="$T/stub" PYTHONDONTWRITEBYTECODE=1 TL_MARK="$T/tl.mark" \
    SECRET_PROMPT_TEST=1 SECRET_PROMPT_TEST_GUI=Aqua SECRET_PROMPT_TEST_DIALOG="$dlg" ${HELPER_ENV:-} \
    /usr/bin/perl -e 'alarm shift; exec @ARGV or exit 127' "$secs" "$PY" "$ST/$script" "$@" >"$T/h.out" 2>&1; RC=$?; }
# 13 нецифровых знаков вместо api_id: отказ ДО Telethon (на подставных значениях, настоящих секретов здесь нет)
rm -f "$ST"/*.env; helper 15 'printf abcdefghijklm' tg_login_first.py --label mcp
[ "$RC" != 0 ] && [ "$RC" != 142 ] && good login-format "13 нецифровых знаков для api_id: отказ, код $RC" || red login-format "13 нецифровых знаков для api_id: код $RC (0 = принято, 142 = бесконечный переспрос до таймаута)"
g -q -e IMPORTED -e CLIENT "$T/tl.mark" && red login-format "Telethon затронут при негодном api_id: $(tr '\n' ' ' <"$T/tl.mark")" || good login-format "Telethon не импортирован и не вызван"
[ ! -e "$ST/api.env" ] && good login-format "api.env не записан" || red login-format "api.env записан с негодным значением"
# второй слой: даже если дверь ввода отдала негодное значение с кодом 0 (сломана или подменена), помощник обязан отказать
if [ -f "$ST/secret_dialog.py" ]; then cp "$ST/secret_prompt.sh" "$T/prompt.keep"
  # подменная дверь: api_id отдаёт годный, всё остальное (api_hash) негодное, и всегда код 0
  printf '#!/bin/bash\nwhile [ $# -gt 2 ]; do [ "$1" = --fd ] && fd="$2"; shift; done\ncase "$1" in api_id) printf "1234567\\n" >&"$fd";; *) printf "not-a-hash\\n" >&"$fd";; esac\n' >"$ST/secret_prompt.sh"
  rm -f "$ST"/*.env; helper 15 'printf x' tg_login_first.py --label mcp
  [ "$RC" != 0 ] && [ "$RC" != 142 ] && ! g -q -e IMPORTED -e CLIENT "$T/tl.mark" && [ ! -e "$ST/api.env" ] && good dialog-recheck "негодное значение от двери ввода отвергнуто помощником (код $RC), Telethon не тронут" || red dialog-recheck "помощник принял негодное значение от двери ввода: код $RC, метки: $(tr '\n' ' ' <"$T/tl.mark")"
  # дверь отдаёт ГОДНУЮ первую строку и хвост второй строкой: значение из двух строк помощник обязан отвергнуть
  printf '#!/bin/bash\nwhile [ $# -gt 2 ]; do [ "$1" = --fd ] && fd="$2"; shift; done\ncase "$1" in api_id) v=1234567;; api_hash) v=0123456789abcdef0123456789abcdef;; telegram_phone) v=+10000000000;; telegram_code) v=12345;; *) v=x;; esac\nprintf "%%s\\nTAIL\\n" "$v" >&"$fd"\n' >"$ST/secret_prompt.sh"
  rm -f "$ST"/*.env; helper 15 'printf x' tg_login_first.py --label mcp
  [ "$RC" != 0 ] && [ "$RC" != 142 ] && ! g -q -e IMPORTED -e CLIENT "$T/tl.mark" && [ ! -e "$ST/api.env" ] && good dialog-oneline "значение из двух строк отвергнуто помощником (код $RC), Telethon не тронут" || red dialog-oneline "помощник принял значение из двух строк: код $RC, метки: $(tr '\n' ' ' <"$T/tl.mark")"
  cp "$T/prompt.keep" "$ST/secret_prompt.sh"
else red dialog-recheck "нет secret_dialog.py: у помощников нет общей двери ввода"; fi
# счастливый путь: формат верный, сессия записана с правами 600, значения в выводе нет
rm -f "$ST"/*.env; helper 30 'case "$SECRET_PROMPT_NAME" in api_id) printf 1234567;; api_hash) printf 0123456789abcdef0123456789abcdef;; telegram_phone) printf +10000000000;; telegram_code) printf 12345;; *) printf x;; esac' tg_login_first.py --label mcp
is login-ok "верный формат: код" "$RC" 0; is login-ok "права mcp.session.env" "$(stat -f %Lp "$ST/mcp.session.env" 2>/dev/null)" 600
g -q -F 0123456789abcdef0123456789abcdef "$T/h.out" && red login-ok "api_hash попал в вывод" || good login-ok "api_hash в выводе нет"
# рельса без названного plist демона: отказ до Telethon
rm -f "$ST/rail.session.env"; helper 15 'printf x' tg_login_rail.py
[ "$RC" != 0 ] && [ "$RC" != 142 ] && ! g -q CLIENT "$T/tl.mark" && good rail-plist "без TGBUS_DAEMON_PLIST: отказ (код $RC), Telethon не вызван" || red rail-plist "без TGBUS_DAEMON_PLIST: код $RC, метки: $(tr '\n' ' ' <"$T/tl.mark")"
# название комнаты не печатается
printf 'TELEGRAM_API_ID=1\nTELEGRAM_API_HASH=stub\n' >"$ST/api.env"; printf 'TELEGRAM_SESSION_STRING=stub\n' >"$ST/rail.session.env"
HELPER_ENV="TGBUS_ROOM=-1001" helper 15 'printf x' tgbus.py check
is tgbus-title "tgbus.py check: код" "$RC" 0
g -q -F "SECRET-ROOM-TITLE" "$T/h.out" && red tgbus-title "название комнаты напечатано: $(head -1 "$T/h.out")" || good tgbus-title "названия комнаты в выводе нет"
g -q -F "rail OK" "$T/h.out" && good tgbus-title "в выводе «rail OK»" || red tgbus-title "в выводе нет «rail OK»: $(head -1 "$T/h.out")"
# линт: чтение из терминала в логин-скриптах запрещено
logins="$(ls "$KIT"/tgbus/tg_login_*.py 2>/dev/null)"
if [ -z "$logins" ]; then red lint-getpass "логин-скрипты не найдены"; else
  miss=0; for f in $logins; do g -q -F 'secret_dialog' "$f" || miss=$((miss+1)); done
  is lint-getpass "логин-скриптов без secret_dialog" "$miss" 0
  n="$(g -h -E '(^|[^A-Za-z_])(getpass|input[[:space:]]*\()' $logins | g -v -E '^[[:space:]]*#' | g -c -v -E 'запрещен|нельзя')"
  is lint-getpass "строк с getpass или input( в логин-скриптах" "$n" 0; fi
# гигиена проб: kill_gates без KG_TMP не оставляет временных каталогов. На macOS «mktemp -d» без шаблона игнорирует
# TMPDIR, поэтому смотрим не в TMPDIR, а (1) на вызовы mktemp через подменную команду в PATH и (2) на путь, который kill_gates сам напечатал.
if [ -f "$KIT/tests/kill_gates.sh" ]; then mkdir -p "$T/mk/bin" "$T/mk/tmp"; : >"$T/mk/calls"
  printf '#!/bin/bash\necho "mktemp $*" >>"%s"\n[ "$*" = -d ] && exec /usr/bin/mktemp -d "$TMPDIR/bare.XXXXXX"\nexec /usr/bin/mktemp "$@"\n' "$T/mk/calls" >"$T/mk/bin/mktemp"; chmod +x "$T/mk/bin/mktemp"   # «mktemp -d» без шаблона уводится в наш каталог: проба сама мусор не оставляет
  env -u KG_TMP TMPDIR="$T/mk/tmp" PATH="$T/mk/bin:$PATH" /bin/bash "$KIT/tests/kill_gates.sh" --list >/dev/null 2>&1
  is harness-tmp "kill_gates --list: вызовов mktemp" "$(g -c . "$T/mk/calls")" 0
  env -u KG_TMP TMPDIR="$T/mk/tmp" PATH="$T/mk/bin:$PATH" /bin/bash "$KIT/tests/kill_gates.sh" --only s_single_exit >"$T/mk/run.out" 2>&1
  root="$(sed -n 's/.*одноразовые HOME в \(.*\) · [0-9-]*T.*/\1/p' "$T/mk/run.out" | head -1)"
  if [ -z "$root" ]; then red harness-tmp "kill_gates --only не напечатал свой временный каталог: проверять нечего"
  elif [ -e "$root" ]; then red harness-tmp "kill_gates --only оставил временный каталог (${root##*/})"; rmdir "$root" 2>/dev/null
  else good harness-tmp "kill_gates --only убрал свой временный каталог"; fi
else red harness-tmp "нет $KIT/tests/kill_gates.sh"; fi
chmod -R u+rwX "$T" 2>/dev/null
printf '\ntest_helpers: проверок зелёных %d · RED %d\n' "$PASS" "$RED"
[ "$RED" = 0 ] || exit 1
exit 0
