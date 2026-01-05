import time
import re
from collections import defaultdict
from pyrogram import filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from Dev import app

# ───────── CONFIG ─────────
MAX_MSGS = 7
TIME_WINDOW = 5
SPAM_SCORE_LIMIT = 7

user_msgs = defaultdict(list)
user_score = defaultdict(int)

SPAM_PATTERNS = [
    r"http[s]?://",
    r"t\.me/",
    r"@[\w\d_]{4,}",
    r"(free|earn|crypto|forex|profit)",
    r"(join|click|dm me)",
    r"(subscribe|promo|offer)",
    r"(chut|lund|bsdk|gand|madarchod|bhenchod)"
]

# ───────── GET ADMINS ─────────
async def get_admin_ids(client, chat_id):
    admins = []
    async for member in client.get_chat_members(chat_id, filter="administrators"):
        if member.user and not member.user.is_bot:
            admins.append(member.user.id)
    return admins

# ───────── AI SPAM GUARD ─────────
@app.on_message(filters.group & ~filters.service & ~filters.me, group=1)
async def ai_spam_guard(client, message):
    user = message.from_user
    chat = message.chat

    if not user:
        return

    if message.text and message.text.startswith("/"):
        return

    # Skip admins / owner
    try:
        member = await client.get_chat_member(chat.id, user.id)
        if member.status in ("administrator", "owner"):
            return
    except:
        return

    now = time.time()

    # Flood check
    user_msgs[user.id] = [t for t in user_msgs[user.id] if now - t < TIME_WINDOW]
    user_msgs[user.id].append(now)

    if len(user_msgs[user.id]) > MAX_MSGS:
        user_score[user.id] += 2

    text = (message.text or "").lower()

    for pattern in SPAM_PATTERNS:
        if re.search(pattern, text):
            user_score[user.id] += 2

    if message.text and message.text.isupper() and len(message.text) > 6:
        user_score[user.id] += 1

    # ───────── ACTION ─────────
    if user_score[user.id] >= SPAM_SCORE_LIMIT:
        spam_text = message.text or "non-text message"

        try:
            await message.delete()
        except:
            pass

        # ── GROUP MESSAGE ──
        try:
            await client.send_message(
                chat.id,
                "🚨 𝘚𝘱𝘢𝘮 𝘋𝘦𝘵𝘦𝘤𝘵𝘦𝘥\n\n"
                f"👤 {user.mention}\n\n"
                "🧠 𝘈𝘐 𝘴𝘺𝘴𝘵𝘦𝘮 𝘥𝘦𝘭𝘦𝘵𝘦𝘥 𝘺𝘰𝘶𝘳 𝘮𝘦𝘴𝘴𝘢𝘨𝘦.\n\n"
                "⚠️ 𝘙𝘦𝘱𝘦𝘢𝘵𝘦𝘥 𝘴𝘱𝘢𝘮 𝘮𝘢𝘺 𝘳𝘦𝘴𝘶𝘭𝘵 𝘪𝘯 𝘮𝘶𝘵𝘦 𝘰𝘳 𝘣𝘢𝘯.",
                reply_markup=InlineKeyboardMarkup(
                    [[
                        InlineKeyboardButton(
                            "𝘝𝘦𝘳𝘪𝘧𝘺 𝘠𝘰𝘶𝘳𝘴𝘦𝘭𝘧 🌷",
                            url="https://t.me/masumX_musicbot?start=true"
                        )
                    ]]
                )
            )
        except:
            pass

        # ── DM TO USER ──
        try:
            await client.send_message(
                user.id,
                "⚠️ 𝘞𝘢𝘳𝘯𝘪𝘯𝘨\n\n"
                f"𝘠𝘰𝘶𝘳 𝘮𝘦𝘴𝘴𝘢𝘨𝘦 𝘸𝘢𝘴 𝘮𝘢𝘳𝘬𝘦𝘥 𝘢𝘴 𝘴𝘱𝘢𝘮 𝘪𝘯 {chat.title}.\n\n"
                "𝘋𝘰 𝘯𝘰𝘵 𝘳𝘦𝘱𝘦𝘢𝘵 𝘵𝘩𝘪𝘴."
            )
        except:
            pass

        # ── DM TO ADMINS ──
        try:
            admin_ids = await get_admin_ids(client, chat.id)

            admin_text = (
                "🚨 𝘚𝘱𝘢𝘮 𝘈𝘭𝘦𝘳𝘵\n\n"
                f"👤 𝘜𝘴𝘦𝘳: {user.mention}\n"
                f"🆔 𝘐𝘋: `{user.id}`\n"
                f"🏠 𝘎𝘳𝘰𝘶𝘱: {chat.title}\n\n"
                f"📩 𝘔𝘦𝘴𝘴𝘢𝘨𝘦: \n`{spam_text[:3500]}`"
            )

            for admin_id in admin_ids:
                try:
                    await client.send_message(admin_id, admin_text)
                except:
                    pass
        except:
            pass

        user_score[user.id] = 0
