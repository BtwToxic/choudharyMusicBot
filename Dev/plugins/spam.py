import time
import re
from collections import defaultdict
from pyrogram import filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from Dev import app

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
    r"(subscribe|promo|offer)"
    r"(chut|land|bsdk|gand)"
]


@app.on_message(filters.group & ~filters.service & ~filters.me, group=1)
async def ai_spam_guard(client, message):
    user = message.from_user
    chat = message.chat

    if not user:
        return
        
    if message.text and message.text.startswith("/"):
        return
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
                f"🚨 𝗦𝗽𝗮𝗺 𝗗𝗲𝘁𝗲𝗰𝘁𝗲𝗱\n\n"
                f"👤 {user.mention} \n\n"
                "🧠 𝘈𝘐 𝘴𝘺𝘴𝘵𝘦𝘮 𝘥𝘦𝘭𝘦𝘵𝘦𝘥 𝘺𝘰𝘶𝘳 𝘮𝘦𝘴𝘴𝘢𝘨𝘦.\n\n"
                "⚠️ 𝘙𝘦𝘱𝘦𝘢𝘵𝘦𝘥 𝘴𝘱𝘢𝘮 𝘮𝘢𝘺 𝘳𝘦𝘴𝘶𝘭𝘵 𝘪𝘯 𝘮𝘶𝘵𝘦 𝘰𝘳 𝘣𝘢𝘯.",
                reply_markup=InlineKeyboardMarkup(
                    [[
                        InlineKeyboardButton(
                            "𝘝𝘦𝘳𝘪𝘧𝘺 𝘠𝘰𝘶𝘳𝘴𝘦𝘭𝘧 🌷",
                            url=f"https://t.me/masumX_musicbot?start=true"
                        )
                    ]]
                )
            )
        except:
            pass

        user_score[user.id] = 0
