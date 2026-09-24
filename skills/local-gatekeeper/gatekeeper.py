#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Привратник «Builders» — тонкий детерминированный движок (AK-47), v2.

Механика: protocol-gatekeeper-join-request-funnel (🔴 must, origin: anton 21.06).
Группа: «Palo Alto AI Research Lab — Builders 🧠» id=[id].
DM заявителю шлёт АДМИН-аккаунт Антона (НЕ бот) — заявка даёт дружелюбный action-bar.

ДВА КАСАНИЯ (порядок железный, из старой CRM `gatekeeper_job` + ресёрча 21.06):
  1) greet   — «что строишь?» ДО одобрения. Одобрение убивает повод писать, поэтому НИКОГДА
               не одобряем раньше приветствия.
  2) welcome — пост-одобрение: пак «что взять и о чём прошу» (⭐ звезда/форк · 🤝 дружба Клодов ·
               📘 FB Антона · 🎁 бесплатный сид). Просим прямо и по максимуму (CLAUDE.md §1.5).

Команды:
  pending                                — необработанные заявки
  greet   <user> [--text ..] [--force]   — приветствие ДО одобрения (чекает журнал аутрича)
  approve <user> [--welcome]             — одобрить (+ сразу welcome-пак)
  reject  <user>                         — отклонить (спам)
  welcome <user> [--force]               — только welcome-пак (уже в группе)
  stats                                  — сводка по журналу (Антон: «статистика по всему»)
Интерпретатор: ~/mcp/telegram-mcp/.venv/bin/python (там telethon).
"""
import os, sys, json, asyncio, subprocess
from datetime import datetime, timezone

CHAT_ID = [id]
# Дефолт — рабочий аккаунт Антона (протокол: DM шлёт «обычно @TonyDzi», не бот).
# С 29.07 он снова может: слоты почищены, он введён в группу и промоутнут админом.
# [рабочий аккаунт] остаётся владельцем группы и запасным привратником: GATEKEEPER_ACCOUNT=[рабочий аккаунт]
ACCOUNT = os.environ.get('GATEKEEPER_ACCOUNT', 'TONYDZI')
VAULT = os.environ.get('OBSIDIAN_VAULT', os.path.expanduser('~/Obsidian/Anton-Knowledge'))
LOG = os.path.expanduser('~/.claude/gatekeeper_log.jsonl')

# --- Касание 1: приветствие ДО одобрения. Варианты — чтобы не слать пачкой один текст ---
GREETS = [
 "hey — saw your request to join Builders 🧠. before I open the door: what are you building "
 "right now? one line is plenty.",
 "hey! your request to Builders 🧠 landed. quick one before I let you in — what are you working "
 "on, and what's the annoying part of it?",
 "hi — you asked to join Builders 🧠. tell me in a line what you're building (or want to), and "
 "I'll open it up.",
]

# --- Касание 2: welcome-пак. Просим прямо и по максимуму (anton 29.07) ---
WELCOME = """welcome in 🧠 — you're inside Builders, the room where we build a second brain on Claude Code in public.

what's yours to take, free:
• github.com/tonydzi — everything we ship is MIT/Apache. start with `claude-bible` (rules-as-files governance) and `claude-consensus` (agents across machines without state drift)
• a free starter seed of the second brain — I set it up on your machine, you keep it

and I'm asking straight, because asking is cheaper than being polite about it:
1. ⭐ star + fork `claude-bible` — github.com/tonydzi/claude-bible. it costs you 5 seconds and it's the whole reason strangers find us
2. 🤝 let's introduce our Claudes — send me your CLAUDE.md (or the messy version of it) and I'll send mine. two agents comparing rules beats two humans comparing opinions
3. 📘 follow Anton on facebook.com/AntonyDzi — that's where the build gets narrated daily, failures included
4. 🗣 and tell me what to fix: what broke for you this week that a second brain should have caught?

no [человек] on any of it — but #1 takes five seconds, so maybe that one now 🙂"""


def load_env():
    env = {}
    for line in open(os.path.expanduser('~/mcp/telegram-mcp/.env')):
        line = line.strip()
        if '=' in line and not line.startswith('#'):
            k, v = line.split('=', 1); env[k] = v.strip()
    return env


def journal(event, user, extra=None):
    """Свой журнал привратника — «отправил» без записи = не отправлял (Connect-правило)."""
    rec = {'ts': datetime.now(timezone.utc).isoformat(), 'event': event,
           'user': str(user), 'account': ACCOUNT}
    rec.update(extra or {})
    with open(LOG, 'a') as f:
        f.write(json.dumps(rec, ensure_ascii=False) + '\n')


def ident(user, uid=None):
    """Все известные написания человека — @ник и числовой id.

    Без этого антидубль обходится сменой идентичности: greet @name, потом welcome 12345
    (находка Codex 29.07). Поэтому журналируем и сверяем ОБА.
    """
    out = {str(user).lstrip('@').lower()}
    if uid:
        out.add(str(uid))
    return {x for x in out if x}


def seen(event, user, uid=None):
    """Антидубль по СВОЕМУ журналу: слали ли мы уже это касание этому человеку."""
    if not os.path.exists(LOG):
        return False
    keys = ident(user, uid)
    for line in open(LOG):
        try:
            r = json.loads(line)
        except Exception:
            continue
        if r.get('event') != event:
            continue
        known = ident(r.get('user', ''), r.get('uid'))
        if keys & known:
            return True
    return False


def outreach_check(user):
    """Антидубль по ОБЩЕМУ журналу аутрича флота. True = чисто, можно писать."""
    log = os.path.join(VAULT, '_outreach', 'outreach_log.py')
    if not os.path.exists(log):
        print(f'⚠️ журнала нет по пути {log} — антидубль флота пропущен'); return True
    r = subprocess.run(['python3', log, 'check', str(user).lstrip('@')],
                       capture_output=True, text=True, timeout=30)
    out = (r.stdout + r.stderr).strip()
    print(out)
    up = out.upper()
    # 'CLEAN' in 'NOT CLEAN' == True — на этом ловил Codex 29.07. Отказ главнее разрешения.
    if any(bad in up for bad in ('NOT CLEAN', 'DUPLICATE', 'ALREADY', 'ДУБЛ')):
        return False
    return 'CLEAN' in up


def pick_greet(user):
    """Ротация без random: один и тот же человек всегда получает свой вариант."""
    h = sum(ord(ch) for ch in str(user))
    return GREETS[h % len(GREETS)]


def cmd_stats():
    if not os.path.exists(LOG):
        print('📭 журнала ещё нет — привратник не сработал ни разу'); return
    counts, users = {}, set()
    for line in open(LOG):
        try:
            r = json.loads(line)
        except Exception:
            continue
        counts[r.get('event', '?')] = counts.get(r.get('event', '?'), 0) + 1
        users.add(str(r.get('user', '')).lower())
    print(f'ПРИВРАТНИК — журнал {LOG}')
    for k in ('greet', 'approve', 'reject', 'welcome'):
        print(f'  {k:8}: {counts.get(k, 0)}')
    print(f'  людей всего: {len(users)}')
    g, w = counts.get('greet', 0), counts.get('welcome', 0)
    if g:
        print(f'  доведено до welcome: {w}/{g} ({round(100*w/g)}%)')


async def run(cmd, user=None, text=None, force=False, with_welcome=False):
    from telethon import TelegramClient, functions
    from telethon.errors import RPCError, FloodWaitError
    from telethon.sessions import StringSession
    env = load_env()
    s = env.get(f'TELEGRAM_SESSION_STRING_{ACCOUNT}')
    if not s:
        sys.exit(f'❌ нет сессии {ACCOUNT} в ~/mcp/telegram-mcp/.env')
    c = TelegramClient(StringSession(s), int(env['TELEGRAM_API_ID']), env['TELEGRAM_API_HASH'])
    await c.connect()
    try:
        if not await c.is_user_authorized():
            sys.exit(f'❌ {ACCOUNT} не авторизован')
        chat = None
        async for d in c.iter_dialogs(limit=200):
            if getattr(d.entity, 'id', None) == CHAT_ID:
                chat = d.entity; break
        if chat is None:
            sys.exit('❌ группа Builders не найдена в диалогах — не тот аккаунт?')

        async def send(target, body, event):
            ent = await c.get_entity(target if not str(target).isdigit() else int(target))
            uid = getattr(ent, 'id', None)
            uname = getattr(ent, 'username', None)
            # повторная сверка уже по РАЗРЕШЁННОЙ идентичности (ник мог смениться, id — нет)
            if seen(event, uname or target, uid) and not force:
                sys.exit(f'⛔ {event} этому человеку уже уходил (id {uid}). Осознанный повтор = --force')
            try:
                await c.send_message(ent, body)
            except FloodWaitError as e:
                # читаем СКОЛЬКО сказал Telegram, не хардкодим экспоненту
                sys.exit(f'⏸ FloodWait {e.seconds}s — Telegram просит подождать, повтори позже')
            journal(event, uname or target, {'chars': len(body), 'uid': uid})
            me = await c.get_me()
            print(f'✅ {event} → {uname or target} (id {uid}) с @{me.username}')

        if cmd == 'pending':
            r = await c(functions.messages.GetChatInviteImportersRequest(
                peer=chat, requested=True, q='', offset_date=None,
                offset_user=(await c.get_input_entity('me')), limit=100))
            users = {u.id: u for u in r.users}
            if not r.importers:
                print('📭 заявок нет')
            for imp in r.importers:
                u = users.get(imp.user_id)
                uname = f'@{u.username}' if u and u.username else ''
                name = f'{getattr(u, "first_name", "") or ""} {getattr(u, "last_name", "") or ""}'.strip()
                mark = ' ✍️greeted' if seen('greet', u.username or imp.user_id) else ''
                print(f'⏳ {imp.user_id} {uname} {name} requested={imp.date:%Y-%m-%d %H:%M} '
                      f'about={imp.about or ""}{mark}')

        elif cmd == 'greet':
            if seen('greet', user) and not force:
                sys.exit(f'⛔ {user} уже приветствовали (журнал привратника). Повтор = --force')
            if not outreach_check(user) and not force:
                sys.exit('⛔ запись в журнале аутрича флота есть — дубль. Осознанный повтор = --force')
            await send(user, text or pick_greet(user), 'greet')
            # 31.07: подсказка врала — register требует --person (не --who) и с этого дня --kind.
            print(f'   зарегистрируй во флотском журнале: python3 {VAULT}/_outreach/outreach_log.py '
                  f'register --person "{user}" --handle {user} --channel tg '
                  f'--account {ACCOUNT.lower()} --campaign gatekeeper --status sent --kind cold')

        elif cmd == 'welcome':
            if seen('welcome', user) and not force:
                sys.exit(f'⛔ welcome-пак {user} уже уходил. Повтор = --force')
            await send(user, text or WELCOME, 'welcome')

        elif cmd in ('approve', 'reject'):
            ent = await c.get_entity(user if not str(user).isdigit() else int(user))
            approved_now = False
            try:
                await c(functions.messages.HideChatJoinRequestRequest(
                    peer=chat, user_id=ent, approved=(cmd == 'approve')))
                journal(cmd, user, {'uid': getattr(ent, 'id', None)})
                approved_now = True
                print(f'✅ {cmd}: {user}')
            except RPCError as e:
                if 'JOIN_REQUEST_MISSING' in str(e) or 'HIDE_REQUESTER_MISSING' in str(e):
                    print(f'ℹ️ заявки от {user} уже нет (обработана раньше или отозвана) — ничего не делаю')
                elif 'ChannelsTooMuch' in type(e).__name__:
                    sys.exit(f'⚠️ {cmd} не прошёл: {user} сам в лимите каналов Telegram '
                             f'(UserChannelsTooMuch) — вступить не сможет, заявка остаётся. '
                             f'Скажи ему освободить слот (/tg-slot — та же болезнь, что у нас)')
                else:
                    sys.exit(f'⚠️ {cmd} не прошёл, Telegram отказал: {type(e).__name__}: {e}')
            if cmd == 'approve' and with_welcome:
                # welcome шлём ТОЛЬКО если approve реально состоялся сейчас; при
                # JOIN_REQUEST_MISSING человек в группу не вошёл (находка Codex 29.07)
                if not approved_now:
                    print('ℹ️ approve не состоялся — welcome-пак НЕ шлю (человек не вошёл). '
                          'Если он уже внутри: gatekeeper.py welcome ' + str(user))
                else:
                    await send(user, WELCOME, 'welcome')
    finally:
        await c.disconnect()


def parse(argv):
    if not argv or argv[0] not in ('pending', 'greet', 'approve', 'reject', 'welcome', 'stats'):
        print(__doc__); sys.exit(3)
    cmd = argv[0]
    user = argv[1] if len(argv) > 1 and not argv[1].startswith('--') else None
    text, force = None, '--force' in argv
    with_welcome = '--welcome' in argv
    if '--text' in argv:
        i = argv.index('--text')
        if i + 1 >= len(argv) or argv[i + 1].startswith('--'):
            sys.exit('⛔ --text требует значение: --text "сообщение"')
        text = argv[i + 1]
    if cmd not in ('pending', 'stats') and not user:
        sys.exit('нужен <user> (id или @username)')
    return cmd, user, text, force, with_welcome


if __name__ == '__main__':
    cmd, user, text, force, with_welcome = parse(sys.argv[1:])
    if cmd == 'stats':
        cmd_stats()
    else:
        asyncio.run(run(cmd, user, text, force, with_welcome))
