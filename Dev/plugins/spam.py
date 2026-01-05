import time
import re
from collections import defaultdict
from pyrogram import filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from Dev import app

# ─────────────────────────────
# CONFIG
# ─────────────────────────────
MAX_MSGS = 2      # msgs
TIME_WINDOW = 2     # seconds
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

# ─────────────────────────────
# AI SPAM GUARD
# ─────────────────────────────
@app.on_message(filters.group & ~filters.service & ~filters.me)
async def ai_spam_guard(client, message):
    user = message.from_user
    chat = message.chat

    if not user:
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

    # Flood detection
    if len(user_msgs[user.id]) > MAX_MSGS:
        user_score[user.id] += 2

    text = (message.text or "").lower()

    # Pattern based AI scoring
    for pattern in SPAM_PATTERNS:
        if re.search(pattern, text):
            user_score[user.id] += 2

    # CAPS abuse
    if message.text and message.text.isupper() and len(message.text) > 6:
        user_score[user.id] += 1

    # Final decision
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
                "🧠 AI system Deleted Your Msg\n\n"
                "⚠️ Warning: Repeated spam = mute / ban.",
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
