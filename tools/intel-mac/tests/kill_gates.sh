#!/bin/bash
# kill_gates.sh: приёмочная проба «убей каждый гейт» для onboard-intel-mac.sh.
#
#   tools/intel-mac/tests/kill_gates.sh [--script <путь к скрипту>] [--only <имя сценария>] [--list] [--no-baseline]
#
# Что делает: на каждый гейт из ../gates.tsv строит одноразовый HOME, подкладывает отказ (чужой аккаунт, сбой записи
# фильтра, неверный путь папки, пропущенная проверка...) и смотрит НАБЛЮДАЕМОЕ: код выхода, журнал POST-запросов к
# Syncthing, файлы на диске. Гейт сработал = скрипт остановился и ничего лишнего не сделал.
# Боевую машину не трогает: HOME одноразовый, сеть, launchctl, osascript, Syncthing REST, gh, claude, codex, uv и
# интерпретатор venv заменены подставными командами в <HOME>/lab/opt/*; скрипт под проверкой при этом байт-в-байт боевой.
# Фазы claude и tailscale здесь НЕ гоняются: в них есть абсолютные пути (/usr/local/bin/brew, /Applications), которые
# подставной командой не закрыть.
#
# Коды: 0 = все проверки зелёные · 1 = есть RED · 2 = ошибка прибора (нет подставной команды, базовый прогон не зелёный)
# KG_TMP=<каталог> задаёт место одноразовых HOME (по умолчанию свой mktemp, который убирается на выходе; KG_KEEP=1
# оставляет его для разбора). KG_PROFILE=<файл> заменяет профиль-фикстуру. KG_LEGACY_ENV=1 дополнительно передаёт ключи
# профиля старыми переменными окружения: так этот же набор проб прогоняется на версии скрипта до профиля (красный лог).
set -o pipefail
HERE="$(cd "$(dirname "$0")" && pwd)"
SCRIPT="$HERE/../onboard-intel-mac.sh"; ONLY=""; LIST=0; BASELINE=1
while [ $# -gt 0 ]; do case "$1" in
  --script) SCRIPT="$2"; shift 2;; --only) ONLY="$2"; shift 2;; --list) LIST=1; shift;; --no-baseline) BASELINE=0; shift;;
  *) echo "неизвестный аргумент: $1" >&2; exit 2;; esac; done
[ -f "$SCRIPT" ] || { echo "нет скрипта: $SCRIPT" >&2; exit 2; }
KIT_DIR_SRC="$(cd "$(dirname "$SCRIPT")" && pwd)"
FIXPROFILE="${KG_PROFILE:-$HERE/fixtures/profile.smoke.env}"
g() { LC_ALL=C /usr/bin/grep -a "$@"; }
PASS=0; RED=0; ERR=0; CUR=""
good() { printf '  ok   %-24s %s\n' "$CUR" "$1"; PASS=$((PASS+1)); }
red()  { printf '  RED  %-24s %s\n' "$CUR" "$1"; RED=$((RED+1)); }
err()  { printf '  ERR  %-24s %s\n' "$CUR" "$1"; ERR=$((ERR+1)); }

# ---------- одноразовый HOME с подставными командами ----------
stub() { local f="$1"; mkdir -p "$(dirname "$f")"; cat >"$f"; chmod +x "$f"; }
mk_home() { # mk_home <имя>: задаёт H (HOME), N (папка узла), S (каталог состояния подставных команд), P (профиль)
  local name="$1"; D="$TMPROOT/$name"; chmod -R u+rwX "$D" 2>/dev/null; rm -rf "$D"
  H="$D/home"; N="$H/lab"; S="$D/state"; P="$D/profile.env"; OUT="$D/out.txt"; RC=""
  mkdir -p "$D/tmp" "$H/.claude" "$H/Library/Application Support/Syncthing" "$H/Library/LaunchAgents" "$S/folders" "$S/devices" "$N/opt/dl" "$N/mcp" "$H/work" || exit 2
  cp "$FIXPROFILE" "$P"
  printf '<configuration><gui><apikey>stub-key-not-a-secret</apikey></gui></configuration>\n' >"$H/Library/Application Support/Syncthing/config.xml"
  local b="$N/opt/coreutils/bin"
  stub "$b/gtimeout" <<'EOF'
#!/bin/bash
# подставной gtimeout: тот же смысл (потолок времени), без GNU coreutils
exec /usr/bin/perl -e 'alarm shift; exec @ARGV or exit 127' "$@"
EOF
  stub "$b/curl" <<'EOF'
#!/bin/bash
# подставной curl: REST Syncthing из каталога состояния; любой другой адрес = «сеть» и отказ
S="$STUB_DIR"; method=GET; data=""; url=""
case "$*" in *X-API-Key*) echo "KEY-IN-ARGV" >>"$S/keyarg.log";; esac   # ключ REST обязан идти через stdin (-K -), не аргументом
while [ $# -gt 0 ]; do case "$1" in
  -X) method="$2"; shift 2;; --data) data="$2"; shift 2;; -o|-H|-m|--retry) shift 2;; -*) shift;; *) url="$1"; shift;; esac; done
case "$url" in
  http://127.0.0.1:8384/*) p="${url#http://127.0.0.1:8384}";;
  http://127.0.0.1:8765/*) [ -f "$S/mcp_down" ] && exit 7; exit 0;;
  *) echo "NETWORK $url" >>"$S/network.log"; exit 6;;
esac
if [ "$method" = POST ]; then
  echo "POST $p" >>"$S/post.log"
  [ -f "$S/post_fail" ] && exit 22
  case "$p" in
    /rest/config/folders) id="$(printf '%s' "$data" | /usr/bin/jq -r .id)"; echo "ACCEPT $id" >>"$S/accept.log"; printf '%s' "$data" >"$S/folders/$id.json";;
    /rest/config/devices) printf '%s' "$data" >"$S/devices/$(printf '%s' "$data" | /usr/bin/jq -r .deviceID).json";;
  esac; exit 0; fi
all() { local d="$1"; if ls "$d"/*.json >/dev/null 2>&1; then /usr/bin/jq -s . "$d"/*.json; else echo '[]'; fi; }
case "$p" in
  /rest/system/ping) echo '{"ping":"pong"}';;
  /rest/system/status) echo '{"myID":"ZZZZZZZ-ZZZZZZZ-ZZZZZZZ-ZZZZZZZ-ZZZZZZZ-ZZZZZZZ-ZZZZZZZ-ZZZZZZZ"}';;
  /rest/system/connections) printf '{"connections":{"%s":{"connected":true}}}\n' "$(cat "$S/hub_id" 2>/dev/null)";;
  /rest/cluster/pending/folders) cat "$S/pending.json";;
  /rest/config/folders) all "$S/folders";;
  /rest/config/folders/*) f="$S/folders/${p##*/}.json"; [ -f "$f" ] && cat "$f" || exit 22;;
  /rest/config/devices) all "$S/devices";;
  /rest/config/devices/*) f="$S/devices/${p##*/}.json"; [ -f "$f" ] && cat "$f" || exit 22;;
  /rest/db/completion*) echo '{"completion":100}';;
  *) exit 22;;
esac
EOF
  stub "$b/launchctl" <<'EOF'
#!/bin/bash
S="$STUB_DIR"; echo "launchctl $*" >>"$S/launchctl.log"
case "$1" in
  list) cat "$S/launchctl.list" 2>/dev/null;;
  load) for a in "$@"; do case "$a" in *.plist) printf -- '-\t0\t%s\n' "$(basename "$a" .plist)" >>"$S/launchctl.list";; esac; done;;
  managername) echo Aqua;;
esac; exit 0
EOF
  stub "$b/osascript" <<'EOF'
#!/bin/bash
echo "osascript" >>"$STUB_DIR/osascript.log"; exit 0
EOF
  stub "$b/uname" <<'EOF'
#!/bin/bash
[ "$1" = -m ] && [ -f "$STUB_DIR/uname_m" ] && { cat "$STUB_DIR/uname_m"; exit 0; }; exec /usr/bin/uname "$@"
EOF
  stub "$b/codex" <<'EOF'
#!/bin/bash
case "$1" in --version) echo "codex-stub";; exec) [ -f "$STUB_DIR/llm_down" ] && exit 1; echo "работает";; esac
EOF
  stub "$N/opt/node/bin/node" <<'EOF'
#!/bin/bash
echo v0.0.0-stub
EOF
  stub "$N/opt/node/bin/npm" <<'EOF'
#!/bin/bash
echo "npm $*" >>"$STUB_DIR/npm.log"
EOF
  stub "$N/opt/node/bin/claude" <<'EOF'
#!/bin/bash
S="$STUB_DIR"; echo "claude $1 $2" >>"$S/claude.log"
case "$1" in
  --version) echo "0.0.0-stub";;
  mcp) case "$2" in get) [ -f "$S/mcp_registered" ];; add) touch "$S/mcp_registered";; esac;;
  -p) [ -f "$S/llm_down" ] && exit 1; echo "> ВЕРСИЯ: v0.0.0-stub работает";;
esac
EOF
  stub "$N/opt/gh/bin/gh" <<'EOF'
#!/bin/bash
S="$STUB_DIR"; echo "gh $*" >>"$S/gh.log"
case "$1 $2" in
  "auth status") [ -f "$S/gh_auth" ];;
  "auth login") touch "$S/gh_auth";;
  "api user") [ -f "$S/gh_auth" ] && cat "$S/gh_login";;
  "--version "*) echo "gh version 0.0.0-stub";;
esac
EOF
  stub "$N/opt/ripgrep/rg" <<'EOF'
#!/bin/bash
echo "ripgrep 0.0.0-stub"
EOF
  stub "$N/opt/syncthing/syncthing" <<'EOF'
#!/bin/bash
echo "syncthing v0.0.0-stub"
EOF
  stub "$N/opt/uv/uv" <<'EOF'
#!/bin/bash
echo "uv $*" >>"$STUB_DIR/uv.log"; [ "$1" = --version ] && echo "uv 0.0.0-stub"; [ -f "$STUB_DIR/uv_fail" ] && exit 1; exit 0
EOF
  stub "$N/mcp/telegram-mcp/.venv/bin/python" <<'EOF'
#!/bin/bash
S="$STUB_DIR"; T="$HOME/Library/Application Support/claude-tgbus"
[ "$1" = -c ] && exit 0
b="$(basename "$1")"; shift; echo "$b $*" >>"$S/py.log"
case "$b" in
  tg_login_first.py) [ -f "$S/first_fail" ] && { echo "ввод отменён"; exit 2; }; printf 'TELEGRAM_SESSION_STRING=stub-not-a-session\n' >"$T/mcp.session.env";;
  tg_login_rail.py)  [ -f "$S/rail_fail" ] && { echo "пароль не введён"; exit 2; }; printf 'TELEGRAM_SESSION_STRING=stub-not-a-session\n' >"$T/rail.session.env";;
  mcpcall.py) echo "3 tools: a b c";;
  tgbus.py) [ -f "$S/tgbus_fail" ] && { echo "rail DEAD"; exit 1; }; echo "rail OK: комната видна";;
esac; exit 0
EOF
  # состояние по умолчанию: gh вошёл ожидаемым аккаунтом, хаб предложил все папки таблицы
  touch "$S/gh_auth"; pval GITHUB_LOGIN >"$S/gh_login"; pval HUB_DEVICE_ID >"$S/hub_id"
  printf '{"claude-skills":{},"claude-memory":{},"claude-home":{},"claude-imports":{},"%s":{},"%s":{}}\n' "$(pval VAULT_FOLDER_ID)" "$(pval BUS_FOLDER_ID)" >"$S/pending.json"
  : >"$S/post.log"; : >"$S/accept.log"; : >"$S/launchctl.list"; : >"$S/network.log"
  for c in gtimeout curl launchctl osascript uname codex; do [ -x "$b/$c" ] || { err "нет подставной команды $c"; exit 2; }; done
}
pval() { g "^$1=" "$P" | tail -1 | sed "s/^$1=//; s#^\\\$HOME/#$H/#"; }             # значение ключа профиля (с раскрытым $HOME)
pset() { local k="$1" v="$2" t; t="$(mktemp)"; g -v "^$k=" "$P" >"$t"; [ "$v" = __DROP__ ] || printf '%s=%s\n' "$k" "$v" >>"$t"; cat "$t" >"$P"; rm -f "$t"; }
tg_fixture() { # tg_fixture <patched|unpatched>: клон telegram-mcp и набор патчей как локальные git-репозитории (без сети)
  local m="$N/mcp/telegram-mcp" k="$N/mcp/telegram-mcp-kit" q="git -c user.name=fixture -c user.email=fixture@example.com"
  mkdir -p "$m/telegram_mcp/tools" "$k/patches"
  printf 'def list_chats():\n    return []\n' >"$m/telegram_mcp/tools/chats.py"; printf 'def get_messages():\n    return []\n' >"$m/telegram_mcp/tools/messages.py"
  printf '[project]\nname = "fixture"\n\n[tool.uv]\noverride-dependencies = ["cryptography<47"]\n' >"$m/pyproject.toml"; printf 'print("fixture")\n' >"$m/main.py"
  printf '.venv/\n' >"$m/.gitignore"
  ( cd "$m" && git init -q . && $q add -A && $q commit -q -m base ) || exit 2
  printf 'def search_dialogs():\n    return []\n' >>"$m/telegram_mcp/tools/chats.py"; printf 'def get_new_messages_since():\n    return []\n' >>"$m/telegram_mcp/tools/messages.py"
  ( cd "$m" && git diff >"$k/patches/0002-extra-tools-multiaccount.patch" ) || exit 2
  ( cd "$k" && git init -q . && $q add -A && $q commit -q -m kit ) || exit 2
  [ "$1" = patched ] || ( cd "$m" && git checkout -q -- . )
}
store_fixture() { local t="$H/Library/Application Support/claude-tgbus"; mkdir -p "$t"; chmod 700 "$t"; printf 'TELEGRAM_API_ID=1\nTELEGRAM_API_HASH=stub\n' >"$t/api.env"; chmod 600 "$t/api.env"; }
legacy_env() { # ключи профиля старыми переменными окружения (для версии скрипта до профиля)
  [ "${KG_LEGACY_ENV:-0}" = 1 ] || return 0
  local k v; for k in "MACHINE_KEY MACHINE_KEY" "HUB_DEVICE_ID HUB_DEVICE_ID" "HUB_NAME HUB_NAME" "MEMORY_SHARE_SLUG MEMORY_SHARE_SLUG" "CANON_CWD CANON_CWD" "TGBUS_ROOM TGBUS_ROOM" "OPERATOR_NAME CLAUDE_OPERATOR" "VAULT_ROOT CLAUDE_VAULT_ROOT"; do
    v="$(pval "${k%% *}")"; [ -n "$v" ] && printf '%s=%s\n' "${k##* }" "$v"; done; }
kit() { # kit [ПЕРЕМЕННАЯ=значение ...] -- <аргументы скрипта>: запуск в одноразовом HOME; вывод в $OUT, код в $RC
  local envs=() line
  while [ $# -gt 0 ] && [ "$1" != "--" ]; do envs+=("$1"); shift; done; shift
  while IFS= read -r line; do [ -n "$line" ] && envs+=("$line"); done <<EOF
$(legacy_env)
EOF
  [ "${NOPROFILE:-0}" = 1 ] || envs+=("ONBOARD_PROFILE=$P")
  ( cd "${KIT_CWD:-$D}" && env -i HOME="$H" TMPDIR="$D/tmp/" PATH="$N/opt/coreutils/bin:/usr/bin:/bin:/usr/sbin:/sbin" LANG=en_US.UTF-8 STUB_DIR="$S" "${envs[@]}" /bin/bash "$SCRIPT" "$@" ) >"$OUT" 2>&1; RC=$?
  if [ -s "$S/network.log" ]; then err "скрипт пошёл в сеть: $(head -1 "$S/network.log")"; fi
}
# ---------- проверки наблюдаемого ----------
rc_is()   { case " $1 " in *" $RC "*) good "код выхода $RC (ждали: $1)";; *) red "код выхода $RC, ждали: $1";; esac; }
rc_not0() { [ "$RC" != 0 ] && good "код выхода $RC (не ноль)" || red "код выхода 0: гейт не остановил скрипт"; }
out_has() { g -q -F -e "$1" "$OUT" && good "в выводе есть «$1»" || red "в выводе нет «$1»"; }
out_no()  { g -q -F -e "$1" "$OUT" && red "в выводе есть «$1»" || good "в выводе нет «$1»"; }
posted()   { g -q -x -F -e "ACCEPT $1" "$S/accept.log" 2>/dev/null; }   # подставной curl пишет строку ACCEPT <id> на каждый POST /rest/config/folders
post_yes() { posted "$1" && good "папка $1 принята (POST есть)" || red "папка $1 не принята (POST нет)"; }
post_no()  { posted "$1" && red "папка $1 ПРИНЯТА (POST есть), хотя гейт должен был остановить" || good "папка $1 не принята (POST нет)"; }
no_folder_posts() { [ -s "$S/accept.log" ] && red "приняты папки (POST /rest/config/folders): $(tr '\n' ' ' <"$S/accept.log")" || good "ни одного POST /rest/config/folders"; }
eff_ignore() { g -v -e '^//' -e '^$' "$1" 2>/dev/null; }
vault_id() { pval VAULT_FOLDER_ID; }

# ---------- сценарии: по одному на гейт ----------
s_profile_missing() { mk_home "$CUR"; NOPROFILE=1 kit -- --dry-run github; rc_is 3; out_has "профиль не задан"; out_no "user.name"; }
s_profile_placeholder() { mk_home "$CUR"; cp "$KIT_DIR_SRC/profile.example.env" "$P" 2>/dev/null || printf 'NODE_DIR=CHANGE_ME\n' >"$P"; kit SHARED_ACCOUNT_OK=1 -- github; rc_is 3; out_has "CHANGE_ME"; [ ! -e "$H/.gitconfig" ] && good "~/.gitconfig не создан" || red "~/.gitconfig создан при профиле-образце"; }
s_profile_tracked() { mk_home "$CUR"; mkdir -p "$D/repo"; cp "$P" "$D/repo/profile.env"; P="$D/repo/profile.env"
  ( cd "$D/repo" && git init -q . && git -c user.name=f -c user.email=f@example.com add profile.env && git -c user.name=f -c user.email=f@example.com commit -q -m p ) || { err "git-фикстура"; return; }
  kit SHARED_ACCOUNT_OK=1 -- github; rc_is 3; out_has "отслеживается git"; [ ! -e "$H/.gitconfig" ] && good "~/.gitconfig не создан" || red "~/.gitconfig создан при профиле из git"; }
s_profile_keys() { mk_home "$CUR"; pset GIT_EMAIL __DROP__; kit SHARED_ACCOUNT_OK=1 -- github; rc_is 1; out_has "[G-PROFILE-KEYS]"; [ ! -e "$H/.gitconfig" ] && good "~/.gitconfig не создан" || red "~/.gitconfig создан без GIT_EMAIL в профиле"; }
s_intel() { mk_home "$CUR"; echo arm64 >"$S/uname_m"; kit SHARED_ACCOUNT_OK=1 -- github; rc_is 2; [ ! -e "$H/.gitconfig" ] && good "~/.gitconfig не создан" || red "фаза пошла на не-Intel"; }
node_fixture() { # node_fixture <good|bad>: архив node в каталоге загрузок и файл сумм вендора (верный или неверный)
  local ver a t; ver="$(sed -n 's/^NODE_VER=\([0-9.]*\);.*/\1/p' "$SCRIPT")"; a="node-v$ver-darwin-x64"; t="$D/mk"
  mkdir -p "$t/$a/bin"; printf '#!/bin/bash\necho v-fixture\n' >"$t/$a/bin/node"; chmod +x "$t/$a/bin/node"
  ( cd "$t" && tar -czf "$N/opt/dl/$a.tar.gz" "$a" ) || exit 2
  rm -rf "$N/opt/node"; NODE_ARCH="$a"
  if [ "$1" = good ]; then printf '%s  %s\n' "$(shasum -a 256 "$N/opt/dl/$a.tar.gz" | awk '{print $1}')" "$a.tar.gz" >"$N/opt/dl/node-SHASUMS256-$ver.txt"
  else printf '%s  %s\n' 0000000000000000000000000000000000000000000000000000000000000000 "$a.tar.gz" >"$N/opt/dl/node-SHASUMS256-$ver.txt"; fi; }
s_hash_vendor() { mk_home "$CUR"; node_fixture bad; kit -- tools; rc_is 1; out_has "[G-HASH-VENDOR]"
  [ ! -e "$N/opt/$NODE_ARCH" ] && good "архив не распакован" || red "архив РАСПАКОВАН при несовпавшем хэше вендора"
  ls "$N/opt/dl/$NODE_ARCH.tar.gz.bad-"* >/dev/null 2>&1 && good "плохой файл отложен как .bad-<штамп>" || red "плохой файл не отложен"; }
s_hash_pin() { mk_home "$CUR"; node_fixture good; kit -- tools; rc_is 1; out_has "[G-HASH-PIN]"
  [ ! -e "$N/opt/$NODE_ARCH" ] && good "архив не распакован" || red "архив РАСПАКОВАН при хэше, не равном закреплённому"; }
s_shared() { mk_home "$CUR"; kit -- github; rc_is 1; [ ! -e "$H/.gitconfig" ] && good "~/.gitconfig не создан" || red "~/.gitconfig создан без SHARED_ACCOUNT_OK"; }
s_gh_account() { mk_home "$CUR"; echo someone-else >"$S/gh_login"; kit SHARED_ACCOUNT_OK=1 -- github; rc_is 1; out_has "[G-GH-ACCOUNT]"; }
s_tg_first() { mk_home "$CUR"; tg_fixture patched; store_fixture; touch "$S/first_fail"; kit -- telegram; rc_is 1
  ls "$H/Library/LaunchAgents/"*telegram-mcp.plist >/dev/null 2>&1 && red "plist демона записан без первой сессии" || good "plist демона не записан"; }
s_tg_rail() { mk_home "$CUR"; tg_fixture patched; store_fixture; touch "$S/rail_fail"; kit -- telegram; rc_is 1; out_has "[G-TG-RAIL]"; }
s_tg_pin() { mk_home "$CUR"; tg_fixture unpatched; store_fixture; kit -- telegram; rc_is 1; out_has "[G-TG-PIN]"
  [ -z "$(git -C "$N/mcp/telegram-mcp" status --porcelain)" ] && good "клон на чужом коммите не тронут" || red "патч наложен на НЕзакреплённый коммит: $(git -C "$N/mcp/telegram-mcp" status --porcelain | tr '\n' ' ')"; }
s_tg_conflict() { mk_home "$CUR"; tg_fixture patched; store_fixture; printf '<<<<<<< ours\nx = 1\n=======\nx = 2\n>>>>>>> theirs\n' >>"$N/mcp/telegram-mcp/telegram_mcp/tools/messages.py"
  kit -- telegram; rc_is 1; out_has "[G-TG-PATCH]"
  ls "$H/Library/LaunchAgents/"*telegram-mcp.plist >/dev/null 2>&1 && red "демон заведён на файле с маркерами конфликта" || good "демон на файле с маркерами конфликта не заведён"; }
s_park() { mk_home "$CUR"; printf '# стартовый закон набора\n' >"$H/.claude/CLAUDE.md"; kit -- syncthing; rc_is 1; no_folder_posts
  [ -f "$H/.claude/CLAUDE.md" ] && good "стартовый CLAUDE.md на месте (без согласия не увезён)" || red "стартовый CLAUDE.md увезён без SHARED_ACCOUNT_OK"; }
s_stignore_write() { mk_home "$CUR"; mkdir -p "$H/.claude/skills"; chmod 555 "$H/.claude/skills"; kit -- syncthing; chmod 755 "$H/.claude/skills"; rc_is 1; out_has "[G-STIGNORE]"; post_no claude-skills; }
s_stignore_readback() { mk_home "$CUR"; mkdir -p "$(pval IMPORTS_DIR)/.stignore"; kit -- syncthing; rc_is 1; out_has "[G-STIGNORE]"; post_no claude-imports; }
s_home_probe() { mk_home "$CUR"; kit -- syncthing; rc_is 4; post_yes claude-home; out_has "[G-HOME-PROBE]"
  [ "$(eff_ignore "$H/.claude/.stignore")" = '*' ] && good "первый приём claude-home: фильтр «*» (ничего не тянется)" || red "первый приём claude-home НЕ в режиме «ничего»: $(eff_ignore "$H/.claude/.stignore" | tr '\n' ' ')"; }
s_home_flag() { mk_home "$CUR"; kit -- syncthing; kit -- syncthing; rc_is 4
  [ "$(eff_ignore "$H/.claude/.stignore")" = '*' ] && good "без CLAUDE_HOME_WHITELIST_OK фильтр остался «*»" || red "whitelist встал без согласия: $(eff_ignore "$H/.claude/.stignore" | tr '\n' ' ')"
  kit CLAUDE_HOME_WHITELIST_OK=1 -- syncthing; rc_is 0
  local e; e="$(eff_ignore "$H/.claude/.stignore")"
  [ "$(printf '%s\n' "$e" | tail -1)" = '*' ] && printf '%s\n' "$e" | g -q -x -F '!/CLAUDE.md' && good "с согласием встал whitelist: поимённые строки и завершающая *" || red "whitelist не встал: $(printf '%s' "$e" | tr '\n' ' ')"; }
s_home_whitelist() { mk_home "$CUR"; pset CLAUDE_HOME_ALLOW "CLAUDE.md projects"; kit -- syncthing; rc_is 3; out_has "G-HOME-WHITELIST"; no_folder_posts
  pset CLAUDE_HOME_ALLOW "CLAUDE.md *.json"; kit -- syncthing; rc_is 3; out_has "G-HOME-WHITELIST"; no_folder_posts
  # звёздочка, которая в текущем каталоге раскрылась бы в настоящие имена файлов, обязана остаться звёздочкой и быть отвергнута
  mkdir -p "$D/cwd-with-md"; : >"$D/cwd-with-md/README.md"; : >"$D/cwd-with-md/NOTES.md"
  pset CLAUDE_HOME_ALLOW "CLAUDE.md *.md"; KIT_CWD="$D/cwd-with-md" kit -- syncthing; rc_is 3; out_has "G-HOME-WHITELIST"; no_folder_posts; }
s_folder_path_accept() { mk_home "$CUR"; mkdir -p "$H/elsewhere"
  printf '{"id":"claude-imports","path":"%s","type":"receiveonly"}' "$H/elsewhere" >"$S/folders/claude-imports.json"; kit -- syncthing; rc_is 1; out_has "[G-FOLDER-PATH]"
  [ ! -e "$H/elsewhere/.stignore" ] && good "в чужой путь ничего не записано" || red "в чужой путь записан .stignore"; }
s_folder_path_verify() { mk_home "$CUR"; kit -- syncthing; kit CLAUDE_HOME_WHITELIST_OK=1 -- syncthing
  printf '{"id":"claude-imports","path":"%s","type":"receiveonly"}' "$H/elsewhere" >"$S/folders/claude-imports.json"; kit VERIFY_LLM=0 -- verify; rc_not0
  g -F -e " папки" "$OUT" | g -q -F -e "[красный]" && good "строка «папки» в verify красная при чужом пути" || red "строка «папки» в verify НЕ красная при чужом пути: $(g -F -e ' папки' "$OUT" | head -1)"; }
s_merge() { mk_home "$CUR"; mkdir -p "$(pval VAULT_ROOT)"; echo local >"$(pval VAULT_ROOT)/note.md"; kit -- syncthing; rc_is 1; post_no "$(vault_id)"; }
s_sync_dir() { mk_home "$CUR"; pset VAULT_ROOT "\$HOME/Sync/vault"; pset BUS_DIR "\$HOME/Sync/vault/_machine-bus"; kit -- syncthing; rc_is 1; post_no "$(vault_id)"; }
s_hub_id() { mk_home "$CUR"; pset HUB_DEVICE_ID "not-a-device-id"; kit -- syncthing; rc_not0; no_folder_posts
  g -q -F -e "POST /rest/config/devices" "$S/post.log" && red "устройство с негодным id добавлено" || good "устройство с негодным id не добавлено"; }
s_bus_layout() { mk_home "$CUR"; pset BUS_LAYOUT __DROP__; kit -- syncthing; rc_is 1; out_has "BUS_LAYOUT"; no_folder_posts; }
s_bus_separate() { mk_home "$CUR"; kit -- syncthing; rc_is 4; post_yes "$(vault_id)"; post_yes "$(pval BUS_FOLDER_ID)"
  g -q -x -F -e "/_machine-bus" "$(pval VAULT_ROOT)/.stignore" 2>/dev/null && good "шина исключена в фильтре волта" || red "в фильтре волта нет исключения шины"; }
s_bus_inside() { mk_home "$CUR"; pset BUS_LAYOUT inside-vault; kit -- syncthing; rc_is 4; post_yes "$(vault_id)"; post_no "$(pval BUS_FOLDER_ID)"
  g -q -x -F -e "/_machine-bus" "$(pval VAULT_ROOT)/.stignore" 2>/dev/null && red "при inside-vault шина исключена из волта" || good "при inside-vault исключения шины нет"
  kit CLAUDE_HOME_WHITELIST_OK=1 -- syncthing; kit VERIFY_LLM=0 -- verify
  g -F -e " папки" "$OUT" | g -q -F -e "[зелёный]" && good "verify при inside-vault не требует отдельной папки шины" || red "verify при inside-vault: строка «папки» не зелёная: $(g -F -e ' папки' "$OUT" | head -1)"; }
law_fixture() { mkdir -p "$H/.claude/projects/$(pval MEMORY_SHARE_SLUG)/memory"; echo "- память" >"$H/.claude/projects/$(pval MEMORY_SHARE_SLUG)/memory/MEMORY.md"
  SLUG="$(printf '%s' "$(pval CANON_CWD)" | sed 's#[^A-Za-z0-9-]#-#g')"; mkdir -p "$H/.claude/projects/$SLUG"; }
zval() { g "^export $1=" "$H/.zshrc" 2>/dev/null | tail -1 | sed "s/^export $1=//; s/^['\"]//; s/['\"]\$//"; }
s_f3() { mk_home "$CUR"; law_fixture; printf 'export CLAUDE_OPERATOR=Old\n' >"$H/.zshrc"; kit SHARED_ACCOUNT_OK=1 -- law; rc_is 0
  [ "$(zval MACHINE_KEY)" = "$(pval MACHINE_KEY)" ] && [ "$(zval CLAUDE_OPERATOR)" = "$(pval OPERATOR_NAME)" ] && [ -n "$(zval MACHINE_BUS_DIR)" ] && good "неполный блок F3 дополнен: все четыре переменные на месте" || red "блок F3 не дополнен: MACHINE_KEY=«$(zval MACHINE_KEY)» CLAUDE_OPERATOR=«$(zval CLAUDE_OPERATOR)»"; }
s_vault_root() { mk_home "$CUR"; law_fixture; pset VAULT_ROOT "\$HOME/Volumes/Data/MyVault"; pset BUS_DIR "\$HOME/Volumes/Data/MyVault/_machine-bus"; kit SHARED_ACCOUNT_OK=1 -- law; rc_is 0
  local z; z="$(zval CLAUDE_VAULT_ROOT)"; z="${z/\$HOME/$H}"
  [ "$z" = "$H/Volumes/Data/MyVault" ] && good "путь волта сохранён как есть" || red "путь волта искажён: в ~/.zshrc «$(zval CLAUDE_VAULT_ROOT)»"; }
s_memlink() { mk_home "$CUR"; law_fixture; mkdir -p "$H/wrong-memory"; ln -s "$H/wrong-memory" "$H/.claude/projects/$SLUG/memory"; kit SHARED_ACCOUNT_OK=1 -- law; rc_is 0
  [ "$(readlink "$H/.claude/projects/$SLUG/memory")" = "$H/.claude/projects/$(pval MEMORY_SHARE_SLUG)/memory" ] && good "неверный линк памяти заменён" || red "линк памяти смотрит не туда: $(readlink "$H/.claude/projects/$SLUG/memory")"
  [ -z "$(ls -A "$H/wrong-memory")" ] && good "в чужой каталог ничего не положено" || red "в чужой каталог положена ссылка: $(ls -A "$H/wrong-memory" | tr '\n' ' ')"; }
s_law_llm_skip() { mk_home "$CUR"; law_fixture; kit SHARED_ACCOUNT_OK=1 VERIFY_LLM=0 -- law; rc_is 4; out_has "[G-VERIFY-LLM]"; out_no "ИТОГ: PASS"; }
s_verify_skip() { mk_home "$CUR"; kit VERIFY_LLM=0 -- verify; rc_not0; out_no "ИТОГ: PASS"
  g -F -e "claude -p" "$OUT" | g -q -F -e "ПРОПУЩЕН" && good "строка claude -p: ПРОПУЩЕН" || red "строка claude -p при VERIFY_LLM=0: $(g -F -e 'claude -p' "$OUT" | head -1)"
  g -F -e "codex exec" "$OUT" | g -q -F -e "ПРОПУЩЕН" && good "строка codex exec: ПРОПУЩЕН" || red "строка codex exec при VERIFY_LLM=0: $(g -F -e 'codex exec' "$OUT" | head -1)"; }
s_phase_stop() { mk_home "$CUR"; kit -- github syncthing; rc_is 1; no_folder_posts
  g -q -e "launchctl load" "$S/launchctl.log" 2>/dev/null && red "после отказа фазы github запущена фаза syncthing (launchctl load)" || good "после отказа фазы следующая не запущена"; }
s_single_exit() { CUR="$CUR"; local n; n="$(g -v -e '^[[:space:]]*#' "$SCRIPT" | g -c -E -e '(^|[;&|{(]|[[:space:]])exit([[:space:]]|;|$)')"
  [ "$n" = 1 ] && good "в скрипте одна команда exit (в finish)" || red "команд exit в скрипте: $n (точка выхода не одна)"; }
s_no_gate_in_pipe() { local n; n="$(g -v -e '^[[:space:]]*#' "$SCRIPT" | g -c -E -e '(^|[^|])\|[[:space:]]*(accept_folder|park_starter_law|need|step|verify_sha|shared_gate|bad|skip|die|phase_[a-z]+)([[:space:]]|$)')"
  [ "$n" = 0 ] && good "ни один гейт не стоит справа от «|» (подоболочка теряла бы счётчики BAD и SKIP)" || red "гейтов справа от «|»: $n (их BAD и SKIP теряются в подоболочке)"; }
s_gates_table() { local tsv="$KIT_DIR_SRC/gates.tsv" x miss=""
  [ -f "$tsv" ] || { red "нет списка гейтов $tsv"; return; }
  for x in $(g -o -E '(\[|bad |skip |step )G-[A-Z0-9]+(-[A-Z0-9]+)*' "$SCRIPT" | g -o -E 'G-[A-Z0-9-]+' | LC_ALL=C sort -u); do g -v '^#' "$tsv" | cut -f1 | g -q -x -F -e "$x" || miss="$miss $x"; done
  [ -z "$miss" ] && good "каждый id гейта из скрипта есть в gates.tsv" || red "гейты скрипта, которых нет в gates.tsv:$miss"
  miss=""; for x in $(g -v '^#' "$tsv" | cut -f5 | g -v '^-' | tr ' ' '\n' | LC_ALL=C sort -u); do case " $SCENARIOS " in *" $x "*) ;; *) miss="$miss $x";; esac; done
  [ -z "$miss" ] && good "каждый сценарий из gates.tsv существует" || red "в gates.tsv названы сценарии, которых нет:$miss"
  miss=""; for x in $SCENARIOS; do g -v '^#' "$tsv" | cut -f5 | tr ' ' '\n' | g -q -x -F -e "$x" || miss="$miss $x"; done
  [ -z "$miss" ] && good "каждый сценарий привязан к гейту в gates.tsv" || red "сценарии без гейта в gates.tsv:$miss"; }
s_key_argv() { mk_home "$CUR"; kit -- syncthing
  [ -s "$S/post.log" ] && good "контроль: REST вызывался ($(wc -l <"$S/post.log" | tr -d ' ') POST)" || red "контроль: REST не вызывался, проверка ничего не доказывает"
  [ -s "$S/keyarg.log" ] && red "ключ REST передан curl аргументом (виден в ps): $(wc -l <"$S/keyarg.log" | tr -d ' ') вызовов" || good "ключ REST ни разу не попал в аргументы curl"; }
s_post_fail() { mk_home "$CUR"; touch "$S/post_fail"; kit -- syncthing; rc_is 1; out_has "[G-ST-POST]"; }
s_pending() { mk_home "$CUR"; printf '{"claude-skills":{},"claude-memory":{},"claude-home":{},"%s":{},"%s":{}}\n' "$(vault_id)" "$(pval BUS_FOLDER_ID)" >"$S/pending.json"; kit -- syncthing; rc_is 4; out_has "[G-PENDING]"; post_no claude-imports; }
s_pending_vault() { mk_home "$CUR"; printf '{"claude-skills":{},"claude-memory":{},"claude-home":{},"claude-imports":{},"%s":{}}\n' "$(pval BUS_FOLDER_ID)" >"$S/pending.json"; kit -- syncthing
  rc_is 4; out_has "[G-PENDING]"; out_no "  BAD  ["; post_no "$(vault_id)"; post_no "$(pval BUS_FOLDER_ID)"; }
s_plist_write() { mk_home "$CUR"; chmod 555 "$H/Library/LaunchAgents"; kit -- syncthing; chmod 755 "$H/Library/LaunchAgents"; rc_is 1
  g -q -e "launchctl load" "$S/launchctl.log" 2>/dev/null && red "launchctl load вызван, хотя plist не записан" || good "launchctl load не вызван"; }
# отказ ШАГА внутри фазы останавливает фазу: дальше ни записи, ни квитанции, ни следующей папки
s_tools_stop() { mk_home "$CUR"; node_fixture good; kit -- tools; rc_is 1; out_has "[G-HASH-PIN]"
  [ ! -e "$H/.zprofile" ] && good "после отказа шага ~/.zprofile не тронут" || red "после отказа шага фаза tools пошла дальше: ~/.zprofile записан"
  out_no "[КВИТАНЦИЯ tools]"; }
s_syncthing_stop() { mk_home "$CUR"; mkdir -p "$H/.claude/skills"; chmod 555 "$H/.claude/skills"; kit -- syncthing; chmod 755 "$H/.claude/skills"; rc_is 1; out_has "[G-STIGNORE]"; no_folder_posts; }
# запись СКВОЗЬ симлинк = запись в чужой файл; бэкап обязан хранить содержимое, а не только ссылку
s_stignore_symlink() { mk_home "$CUR"; local d; d="$(pval IMPORTS_DIR)"; mkdir -p "$d"; printf 'FOREIGN\n' >"$H/foreign.txt"; ln -s "$H/foreign.txt" "$d/.stignore"
  kit -- syncthing; rc_is 1; out_has "[G-STIGNORE]"; post_no claude-imports
  [ "$(cat "$H/foreign.txt")" = FOREIGN ] && good "файл за симлинком .stignore не тронут" || red "фильтр записан СКВОЗЬ симлинк: чужой файл начинается с «$(head -1 "$H/foreign.txt")»"; }
s_zprofile_link() { mk_home "$CUR"; mkdir -p "$H/dotfiles"; printf 'ORIGINAL\n' >"$H/dotfiles/zprofile"; ln -s "$H/dotfiles/zprofile" "$H/.zprofile"
  kit -- tools; rc_is 1; out_has "[G-STEP]"
  [ "$(cat "$H/dotfiles/zprofile")" = ORIGINAL ] && good "файл за симлинком ~/.zprofile не тронут" || red "PATH дописан СКВОЗЬ симлинк в чужой файл"; }
s_gitconfig_link() { mk_home "$CUR"; mkdir -p "$H/dotfiles"; printf '[user]\n\tname = Original\n' >"$H/dotfiles/gitconfig"; ln -s "$H/dotfiles/gitconfig" "$H/.gitconfig"
  kit SHARED_ACCOUNT_OK=1 -- github; rc_is 0
  local b; b="$(find "$N/backup-onboarding" -type f -name '*gitconfig*' 2>/dev/null | head -1)"
  [ -n "$b" ] && g -q -F 'name = Original' "$b" && good "в бэкапе СОДЕРЖИМОЕ прежнего ~/.gitconfig, а не только ссылка" || red "в бэкапе нет содержимого прежнего ~/.gitconfig: $(find "$N/backup-onboarding" -name '*gitconfig*' -exec ls -ld {} \; 2>/dev/null | head -1 | sed "s#$D#<tmp>#g")"; }
# строка «19» verify зелёная только по записи прошлого зелёного verify, а не по флагу
s_second_pass() { mk_home "$CUR"; kit SECOND_PASS=1 VERIFY_LLM=0 -- verify
  g -F -e "] 19 " "$OUT" | g -q -F -e "[зелёный]" && red "строка 19 зелёная без улики (флаг SECOND_PASS=1 вместо проверки)" || good "без записи прошлого зелёного verify строка 19 не зелёная"
  printf '2026-01-01T00:00:00Z verify-ok rows=18\n' >"$N/verify-history.log"; kit VERIFY_LLM=0 -- verify
  g -F -e "] 19 " "$OUT" | g -q -F -e "[зелёный]" && good "с записью прошлого зелёного verify строка 19 зелёная" || red "строка 19 не зелёная при записи прошлого зелёного verify: $(g -F -e '] 19 ' "$OUT" | head -1)"; }
# базовые прогоны: без подложенного отказа фаза обязана пройти (иначе красное выше ничего не значит)
b_github() { mk_home "$CUR"; kit SHARED_ACCOUNT_OK=1 -- github; rc_is 0; [ "$(HOME="$H" git config --global user.email)" = "$(pval GIT_EMAIL)" ] && good "identity из профиля записана" || red "identity не записана"; }
b_tools() { mk_home "$CUR"; kit -- tools; rc_is 0; }
b_telegram() { mk_home "$CUR"; tg_fixture patched; store_fixture; kit -- telegram; rc_is 0; }
b_syncthing() { mk_home "$CUR"; kit -- syncthing; rc_is 4; kit CLAUDE_HOME_WHITELIST_OK=1 -- syncthing; rc_is 0; }
b_law() { mk_home "$CUR"; law_fixture; kit SHARED_ACCOUNT_OK=1 -- law; rc_is 0; }

SCENARIOS="s_profile_missing s_profile_placeholder s_profile_tracked s_profile_keys s_intel s_hash_vendor s_hash_pin s_shared s_gh_account s_tg_first s_tg_rail s_tg_pin s_tg_conflict s_park s_stignore_write s_stignore_readback s_home_probe s_home_flag s_home_whitelist s_folder_path_accept s_folder_path_verify s_merge s_sync_dir s_hub_id s_bus_layout s_bus_separate s_bus_inside s_f3 s_vault_root s_memlink s_law_llm_skip s_verify_skip s_phase_stop s_single_exit s_no_gate_in_pipe s_gates_table s_key_argv s_post_fail s_pending s_pending_vault s_plist_write s_tools_stop s_syncthing_stop s_stignore_symlink s_zprofile_link s_gitconfig_link s_second_pass"
BASELINES="b_github b_tools b_telegram b_syncthing b_law"
[ "$LIST" = 1 ] && { printf '%s\n' $BASELINES $SCENARIOS; exit 0; }   # список: ни одного временного каталога
if [ -n "${KG_TMP:-}" ]; then TMPROOT="$KG_TMP"; mkdir -p "$TMPROOT" || exit 2
else TMPROOT="$(mktemp -d "${TMPDIR:-/tmp}/kill_gates.XXXXXX")" || exit 2   # свой каталог убирается на выходе, иначе каждый прогон оставлял бы мусор в $TMPDIR
  [ "${KG_KEEP:-0}" = 1 ] || trap 'chmod -R u+rwX "$TMPROOT" 2>/dev/null; rm -rf "$TMPROOT"' EXIT; fi
echo "kill_gates: скрипт $SCRIPT"
echo "kill_gates: sha256 $(shasum -a 256 "$SCRIPT" | awk '{print $1}') · одноразовые HOME в $TMPROOT · $(date -u +%Y-%m-%dT%H:%M:%SZ)"
if [ -n "$ONLY" ]; then RUN="$ONLY"; elif [ "$BASELINE" = 1 ]; then RUN="$BASELINES $SCENARIOS"; else RUN="$SCENARIOS"; fi
for CUR in $RUN; do
  case " $BASELINES $SCENARIOS " in *" $CUR "*) ;; *) echo "нет такого сценария: $CUR" >&2; exit 2;; esac
  before_red="$RED"; "$CUR"
  case "$CUR" in b_*) [ "$RED" = "$before_red" ] || { ERR=$((ERR+1)); printf '  ERR  %-24s базовый прогон не зелёный: красное по гейтам ниже ничего не доказывает\n' "$CUR"; };; esac
done
chmod -R u+rwX "$TMPROOT" 2>/dev/null
[ "$BASELINE" = 1 ] || [ -n "$ONLY" ] || echo "ВНИМАНИЕ: базовые прогоны пропущены (--no-baseline): красное выше не отличает сработавший гейт от сломанной обвязки"
printf '\nkill_gates: проверок зелёных %d · RED %d · ошибок прибора %d\n' "$PASS" "$RED" "$ERR"
[ "$ERR" = 0 ] || exit 2
[ "$RED" = 0 ] || exit 1
exit 0
