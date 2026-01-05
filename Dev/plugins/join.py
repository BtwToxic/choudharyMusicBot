from pyrogram import filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from Dev import app, db


# ─────────────────────────────
# VERIFY VIA START PARAM ONLY
# /start verify OR ?start=verify
# ─────────────────────────────
@app.on_message(filters.private & filters.command("start"))
async def verify_user(client, message):
    # Ignore normal /start
    if len(message.command) < 2:
        return

    # Only handle verification
    if message.command[1].lower() != "verify":
        return

    await db.add_verified(message.from_user.id)

    await message.reply_text(
        "✅ **Verification Successful**\n\n"
        "You are now verified as a human.\n"
        "You can send messages in the group freely."
    )


# ─────────────────────────────
# GROUP VERIFICATION GUARD
# ─────────────────────────────
@app.on_message(filters.group & ~filters.service & ~filters.me)
async def verify_guard(client, message):
    user = message.from_user
    chat = message.chat

    if not user:
        return

    # Skip admins / owner
    try:
        member = await client.get_chat_member(chat.id, user.id)
        if member.status in ("administrator", "owner"):
            return
    except:
        return

    # Already verified → allow
    if await db.is_verified(user.id):
        return

    # ❌ Not verified → delete user's message
    try:
        await message.delete()
    except:
        pass

    # ⚠️ Public warning with Start button
    try:
        bot = await client.get_me()
        await client.send_message(
            chat.id,
            f"⚠️ **Human Verification Required**\n\n"
            f"👤 {user.mention}\n\n"
            "❌ You must verify before sending messages in this group.\n\n"
            "👇 Click the button below to start the bot and verify:",
            reply_markup=InlineKeyboardMarkup(
                [[
                    InlineKeyboardButton(
                        "🤖 Start Verification",
                        url=f"https://t.me/{bot.username}?start=verify"
                    )
                ]]
            )
        )
    except:
        pass
