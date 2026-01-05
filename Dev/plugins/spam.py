import time
import re
from collections import defaultdict
from pyrogram import filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from Dev import app

MAX_MSGS = 2
TIME_WINDOW = 2
SPAM_SCORE_LIMIT = 3

user_msgs = defaultdict(list)
user_score = defaultdict(int)

SPAM_PATTERNS = [
    r"http[s]?://",
    r"t\.me/",
    r"@[\w\d_]{4,}",
    r"(free|earn|crypto|forex|profit)",
    r"(join|click|dm me)",
    r"(subscribe|promo|offer)"
]


@app.on_message(filters.group & ~filters.service & ~filters.me, group=1)
async def ai_spam_guard(client, message):
    user = message.from_user
    chat = message.chat

    if not user:
        return

    # ✅ ALLOW COMMANDS (THIS WAS MISSING)
    if message.text and message.text.startswith("/"):
        return

    # Admin skip
    try:
        member = await client.get_chat_member(chat.id, user.id)
        if member.status in ("administrator", "owner"):
            return
    except:
        return

    now = time.time()
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

    if user_score[user.id] >= SPAM_SCORE_LIMIT:
        try:
            await message.delete()
        except:
            pass

        try:
            await client.send_message(
                chat.id,
                f"🚨 **Spam Detected**\n\n"
                f"👤 {user.mention}\n"
                "🧠 AI system deleted your message.\n\n"
                "⚠️ Repeated spam may result in mute or ban.",
                reply_markup=InlineKeyboardMarkup(
                    [[
                        InlineKeyboardButton(
                            "🤖 Verify Yourself",
                            url=f"https://t.me/{(await client.get_me()).username}?start=verify"
                        )
                    ]]
                )
            )
        except:
            pass

        user_score[user.id] = 0
