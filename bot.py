import json
import os
import datetime
from telegram import Update, Chat
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, ContextTypes, filters

BOT_TOKEN = "8071517946:AAFJNR00L3Il4cruOdaGeCtAvdNlwx47nn4"
OWNER_ID = 6660880060  # Eva_Chowdhury_pori
CHANNEL_USERNAME = "@mwyluTYFDeFmNDI1"

DATA_FILE = "users.json"

def load_data():
    if not os.path.exists(DATA_FILE):
        with open(DATA_FILE, "w") as f:
            json.dump({}, f)
    with open(DATA_FILE, "r") as f:
        return json.load(f)

def save_data(data):
    with open(DATA_FILE, "w") as f:
        json.dump(data, f, indent=2)

def can_use(user):
    now = datetime.datetime.utcnow()
    last_used = datetime.datetime.fromisoformat(user.get("last_used", "2000-01-01T00:00:00"))
    mode = user.get("mode", "free")
    usage_left = user.get("extra", 0)

    if mode == "unlimited":
        return True
    elif mode == "daily" and (now.date() != last_used.date()):
        return True
    elif mode == "weekly" and (now - last_used).days >= 7:
        return True
    elif mode == "monthly" and (now - last_used).days >= 30:
        return True
    elif mode == "once" and not user.get("used_once", False):
        return True
    elif mode == "free" and (now.date() != last_used.date() or usage_left > 0):
        return True
    return False

def record_usage(user):
    now = datetime.datetime.utcnow()
    user["last_used"] = now.isoformat()
    if user.get("mode", "free") == "once":
        user["used_once"] = True
    if user.get("mode", "free") == "free" and user.get("extra", 0) > 0:
        user["extra"] -= 1
    return user

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = str(update.effective_user.id)
    ref_id = context.args[0] if context.args else None
    data = load_data()

    if update.effective_chat.type != Chat.PRIVATE:
        await context.bot.leave_chat(update.effective_chat.id)
        return

    if user_id not in data:
        data[user_id] = {
            "mode": "free",
            "extra": 0,
            "last_used": "2000-01-01T00:00:00",
            "used_once": False,
            "ref_by": None
        }

    if ref_id and ref_id != user_id and ref_id in data:
        data[ref_id]["extra"] += 1
        data[user_id]["extra"] += 1
        data[user_id]["ref_by"] = ref_id

    # Check if joined channel
    try:
        chat_member = await context.bot.get_chat_member(CHANNEL_USERNAME, update.effective_user.id)
        if chat_member.status not in ["member", "administrator", "creator"]:
            raise Exception("Not joined")
    except:
        await update.message.reply_text(f"❗ আগে আমাদের চ্যানেল Join করুন:\n{CHANNEL_USERNAME}")
        return

    save_data(data)
    await update.message.reply_text("🎉 স্বাগতম! আপনি প্রতিদিন ১ বার ফ্রি ব্যবহার করতে পারবেন।")

async def allow(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != OWNER_ID:
        return
    if len(context.args) < 2:
        await update.message.reply_text("ব্যবহার: /allow <user_id> <mode>")
        return
    user_id, mode = context.args[0], context.args[1]
    if mode not in ["once", "daily", "weekly", "monthly", "unlimited"]:
        await update.message.reply_text("mode হতে হবে: once/daily/weekly/monthly/unlimited")
        return

    data = load_data()
    if user_id not in data:
        data[user_id] = {
            "mode": mode,
            "extra": 0,
            "last_used": "2000-01-01T00:00:00",
            "used_once": False
        }
    else:
        data[user_id]["mode"] = mode
    save_data(data)
    await update.message.reply_text(f"✅ {user_id} কে {mode} পারমিশন দেওয়া হয়েছে।")

async def status(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = str(update.effective_user.id)
    data = load_data()
    user = data.get(user_id)
    if not user:
        await update.message.reply_text("😐 আপনি এখনো রেজিস্টার করেননি। /start দিয়ে শুরু করুন।")
        return
    msg = f"""📊 আপনার স্ট্যাটাস:

🔹 Mode: {user.get("mode")}
🔹 Extra Uses (Refer Bonus): {user.get("extra", 0)}
🔹 সর্বশেষ ব্যবহার: {user.get("last_used", "N/A")}
🔹 রেফার করেছে: {user.get("ref_by", "N/A")}
"""
    await update.message.reply_text(msg)

async def message_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = str(update.effective_user.id)
    data = load_data()
    user = data.get(user_id)
    if not user:
        await update.message.reply_text("😐 আপনি এখনো রেজিস্টার করেননি। /start দিয়ে শুরু করুন।")
        return

    if can_use(user):
        user = record_usage(user)
        save_data(data)
        await update.message.reply_text("✅ আপনার মেসেজ গ্রহণ করা হয়েছে (ডেমো রিপ্লাই)।")
    else:
        await update.message.reply_text("🚫 আজকের জন্য আপনার ইউজ লিমিট শেষ।\n\n🔓 আনলিমিটেড ইউজ করতে Owner কে মেসেজ করুন:\n👉 @Eva_Chowdhury_pori")

def main():
    app = ApplicationBuilder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("allow", allow))
    app.add_handler(CommandHandler("status", status))
    app.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), message_handler))
    app.run_polling()

if __name__ == "__main__":
    main()
