from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes
import os

# 🔐 Bot Configurations
BOT_TOKEN = "8071517946:AAFJNR00L3Il4cruOdaGeCtAvdNlwx47nn4"
CHANNEL_ID = "-1002122745662"  # তোমার চ্যানেল ID
OWNER_USERNAME = "@Eva_Chowdhury_pori"
DOWNLOAD_LINK = "https://example.com/download-link"  # এখানে তোমার ডাউনলোড লিংক বসাও

# ✅ /start command
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    user_id = user.id

    # Check if user joined the channel
    chat_member = await context.bot.get_chat_member(chat_id=CHANNEL_ID, user_id=user_id)

    if chat_member.status in ["member", "administrator", "creator"]:
        keyboard = [
            [InlineKeyboardButton("✅ Verify", callback_data="verify")],
            [InlineKeyboardButton("🔗 Link to Download", url=DOWNLOAD_LINK)],
            [InlineKeyboardButton("📞 Contact", url=f"https://t.me/{OWNER_USERNAME.lstrip('@')}")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await update.message.reply_text("✅ আপনি সফলভাবে আমাদের চ্যানেলে যুক্ত হয়েছেন!", reply_markup=reply_markup)
    else:
        join_keyboard = InlineKeyboardMarkup([
            [InlineKeyboardButton("📢 চ্যানেল Join করুন", url="https://t.me/+mwyluTYFDeFmNDI1")]
        ])
        await update.message.reply_text(
            "❌ আগে আমাদের চ্যানেলে Join করুন তারপর আবার /start দিন।", reply_markup=join_keyboard
        )

# 🔘 Verify Callback
async def verify_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    user_id = query.from_user.id
    chat_member = await context.bot.get_chat_member(chat_id=CHANNEL_ID, user_id=user_id)

    if chat_member.status in ["member", "administrator", "creator"]:
        await query.answer("✅ Verification সফল হয়েছে!")
        await query.edit_message_text(
            text="✅ Access Granted!\n🔗 নিচের লিংক থেকে ডাউনলোড করুন:",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("🔗 Download Now", url=DOWNLOAD_LINK)],
                [InlineKeyboardButton("📞 Contact", url=f"https://t.me/{OWNER_USERNAME.lstrip('@')}")]
            ])
        )
    else:
        await query.answer("❌ আগে চ্যানেলে Join করুন!", show_alert=True)

# ▶️ Run Bot
def main():
    app = Application.builder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(verify_callback, pattern="^verify$"))

    print("🤖 Bot চালু হয়েছে...")
    app.run_polling()

if __name__ == "__main__":
    main()
