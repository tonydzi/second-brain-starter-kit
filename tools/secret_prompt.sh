#!/bin/bash
# secret_prompt.sh: ОДНА дверь для всего, что вводит человек (секрет или нет). Окно macOS, не терминал:
# оператор может не видеть вкладок терминала, а всё набранное в терминале сессии агента попадает в её журнал.
#
#   secret_prompt.sh [--visible] [--text "пояснение"] [--tries N] <имя> <regex> -- <команда> [аргументы...]
#       значение уходит команде на stdin одной строкой и забывается; код выхода = код команды
#   secret_prompt.sh [--visible] [--text "пояснение"] [--tries N] --fd N <имя> <regex>
#       значение пишется в унаследованный дескриптор N (N >= 3: канал, который открыл родительский процесс)
#
# Контракт:
#   * формат проверяется ДО того, как значение куда-либо уйдёт: <regex> = ERE, совпадение целиком; значение одной
#     строкой (перевод строки или возврат каретки = формат не подошёл: получатель читает одну строку);
#     не подошло = окно повторяется (всего --tries раз, по умолчанию 3), потом отказ с кодом 4. Команда НЕ запускается.
#   * значение не попадает в аргументы процессов, в окружение, на stdout и stderr, в файлы. В вывод идёт только
#     строка «ok, длина N». Трассировка оболочки (set -x) выключается принудительно.
#   * по умолчанию ввод скрыт (hidden answer); --visible для несекретного (номер, код из приложения).
#   * нет графической сессии (ssh, launchd-агент без Aqua) = код 3. Отката на чтение из терминала (read, getpass) НЕТ.
#   * отмена или таймаут окна (10 минут) = код 2.
#
# Коды: 0 = принято и доставлено · 2 = отмена или таймаут · 3 = нет GUI · 4 = формат не подошёл · 5 = неверный вызов
#       (в режиме «-- команда»: код команды, если значение принято).
#
# Проверка без человека: SECRET_PROMPT_TEST=1 включает подмены SECRET_PROMPT_TEST_DIALOG (команда вместо окна,
# её stdout = «набранное») и SECRET_PROMPT_TEST_GUI (ответ вместо launchctl managername). Без SECRET_PROMPT_TEST=1
# подмены игнорируются. Подмене окна передаётся имя запрошенного значения в SECRET_PROMPT_NAME.
# Тесты: tools/intel-mac/tests/test_helpers.sh
set +x
set -o pipefail

HIDDEN=1; TEXT=""; TRIES=3; FD=""; NAME=""; RE=""
fail() { printf 'secret_prompt: %s\n' "$2" >&2; exit "$1"; }
while [ $# -gt 0 ]; do case "$1" in
  --visible) HIDDEN=0; shift;;
  --text) TEXT="${2:-}"; shift 2 || fail 5 "после --text нужно пояснение";;
  --tries) TRIES="${2:-}"; shift 2 || fail 5 "после --tries нужно число";;
  --fd) FD="${2:-}"; shift 2 || fail 5 "после --fd нужен номер дескриптора";;
  --) break;;
  -*) fail 5 "неизвестный флаг: $1";;
  *) if [ -z "$NAME" ]; then NAME="$1"; elif [ -z "$RE" ]; then RE="$1"; else fail 5 "лишний аргумент до «--»: $1"; fi; shift;;
esac; done
[ -n "$NAME" ] && [ -n "$RE" ] || fail 5 "нужно: secret_prompt.sh [--visible] [--text T] [--tries N] <имя> <regex> -- <команда...>  либо  --fd N <имя> <regex>"
case "$TRIES" in ''|*[!0-9]*|0) fail 5 "--tries: нужно целое число от 1";; esac
if [ "${1:-}" = "--" ]; then shift; [ $# -gt 0 ] || fail 5 "после «--» нужна команда, которая прочитает значение со stdin"; [ -z "$FD" ] || fail 5 "нужно одно из двух: --fd N или «-- команда»"
else
  [ -n "$FD" ] || fail 5 "некуда отдать значение: нужна «-- команда» (stdin) или --fd N. На stdout значение не печатается никогда"
  case "$FD" in ''|*[!0-9]*) fail 5 "--fd: нужен номер дескриптора";; esac
  [ "$FD" -ge 3 ] || fail 5 "--fd: дескрипторы 0, 1 и 2 запрещены (значение попало бы на экран или в журнал)"
  { : >&"$FD"; } 2>/dev/null || fail 5 "--fd $FD: дескриптор не открыт родительским процессом"
  [ ! -t "$FD" ] || fail 5 "--fd $FD: это терминал, значение попало бы на экран"
fi
FULL="^(${RE})\$"
[[ "" =~ $FULL ]]; [ $? = 2 ] && fail 5 "regex не разобран: $RE"

TEST=0; [ "${SECRET_PROMPT_TEST:-0}" = 1 ] && { TEST=1; printf 'secret_prompt: ТЕСТОВЫЙ РЕЖИМ, окно заменено подменой\n' >&2; }
gui="$(/bin/launchctl managername 2>/dev/null)"; [ "$TEST" = 1 ] && [ -n "${SECRET_PROMPT_TEST_GUI:-}" ] && gui="$SECRET_PROMPT_TEST_GUI"
[ "$gui" = Aqua ] || fail 3 "нет графической сессии (launchctl managername = «${gui:-пусто}»): окно показать негде. Из терминала значение не читаю: запусти шаг из сессии на экране машины."

esc() { local s="$1"; s="${s//\\/\\\\}"; s="${s//\"/\\\"}"; printf '%s' "$s"; }
dialog() { # dialog <примечание>: печатает набранное (перехватывается $( ) в этом же процессе). Код 2 = отмена или таймаут.
  local out hid=""
  if [ "$TEST" = 1 ] && [ -n "${SECRET_PROMPT_TEST_DIALOG:-}" ]; then out="$(SECRET_PROMPT_NAME="$NAME" /bin/bash -c "$SECRET_PROMPT_TEST_DIALOG")" || return 2
  else
    [ "$HIDDEN" = 1 ] && hid="with hidden answer"
    /usr/bin/osascript -e 'tell application "System Events" to activate' >/dev/null 2>&1
    out="$(/usr/bin/osascript \
      -e "set r to display dialog \"$(esc "$1${TEXT:-Введи: $NAME}")\" default answer \"\" $hid with title \"$(esc "Ввод: $NAME")\" buttons {\"Отмена\", \"OK\"} default button \"OK\" giving up after 600" \
      -e 'if gave up of r then return "__GAVEUP__"' -e 'if button returned of r is "Отмена" then return "__CANCEL__"' -e 'return text returned of r' 2>/dev/null)" || return 2
  fi
  case "$out" in __GAVEUP__|__CANCEL__) return 2;; esac
  printf '%s' "$out"; }

v=""; note=""; n=0; good=0
while [ "$n" -lt "$TRIES" ]; do
  n=$((n+1))
  v="$(dialog "$note")" || { v=""; fail 2 "${NAME}: ввод отменён или окно закрылось по таймауту"; }
  case "$v" in *$'\n'*|*$'\r'*) ;; *) if [[ "$v" =~ $FULL ]]; then good=1; break; fi;; esac   # «.» в bash ERE совпадает и с переводом строки
  note="Формат не подошёл (получено знаков: ${#v}). Попытка $((n+1)) из ${TRIES}. "
  v=""
done
[ "$good" = 1 ] || { v=""; fail 4 "${NAME}: формат не подошёл за $TRIES попыток. Значение никуда не отправлено."; }
printf 'secret_prompt: %s ok, длина %d\n' "$NAME" "${#v}"
if [ -n "$FD" ]; then printf '%s\n' "$v" >&"$FD"; rc=$?; v=""; exit "$rc"; fi
printf '%s\n' "$v" | "$@"; rc=${PIPESTATUS[1]}; v=""
[ "$rc" = 0 ] || printf 'secret_prompt: команда вернула %s\n' "$rc" >&2
exit "$rc"
