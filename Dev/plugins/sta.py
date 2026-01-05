from pyrogram import filters
from Dev import app

# SAME VERIFIED_USERS set use karega
# (jo verification plugin me hai)
try:
    from Dev.plugins.verify_guard import VERIFIED_USERS
except:
    VERIFIED_USERS = set()

@app.on_message(filters.command("verifystats") & filters.group)
async def verify_stats(client, message):
    try:
        member = await client.get_chat_member(message.chat.id, message.from_user.id)
        if member.status not in ("administrator", "owner"):
            return
    except:
        return

    total_verified = len(VERIFIED_USERS)

    await message.reply_text(
        "📊 **Verification Stats**\n\n"
        f"✅ Verified Users: **{total_verified}**\n"
        "🤖 Method: Bot Start Verification\n"
        "🧠 Protection: AI Spam Guard Enabled"
    )
