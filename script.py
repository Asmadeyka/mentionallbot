import json
import os
from telegram import Update
from telegram.constants import ParseMode
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, ContextTypes, filters

DATA_FILE = "members.json"
group_members = {}

def load_members():
    global group_members
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            raw = json.load(f)
            group_members = {
                int(chat_id): {
                    int(uid): user for uid, user in users.items()
                } for chat_id, users in raw.items()
            }

def save_members():
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(group_members, f, ensure_ascii=False, indent=2)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Хули ты тыкаешь тут")

async def track_users(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user is None or update.effective_chat is None:
        return

    chat_id = update.effective_chat.id
    user = update.effective_user

    if chat_id not in group_members:
        group_members[chat_id] = {}

    group_members[chat_id][user.id] = {
        "id": user.id,
        "first_name": user.first_name,
        "username": user.username,
    }

    save_members()

from telegram.constants import ParseMode

async def mention_all(update: Update, context: ContextTypes.DEFAULT_TYPE):
    message = update.message
    chat_id = message.chat.id

    try:
        await message.delete()
    except Exception as e:
        print(f"Не удалось удалить сообщение: {e}")


    if chat_id not in group_members or not group_members[chat_id]:
        await message.reply_text("Я ещё никого не знаю в этой группе.")
        return

    mentions = []
    for user in group_members[chat_id].values():
        if user["username"]:
            mentions.append(f"@{user['username']}")
        else:
            first_name = user['first_name'].replace('<', '&lt;').replace('>', '&gt;')
            mentions.append(f'<a href="tg://user?id={user["id"]}">{first_name}</a>')

    text = " ".join(mentions)
    await context.bot.send_message(chat_id=chat_id, text=text, parse_mode=ParseMode.HTML)

async def main():
    load_members()

    tke = os.getenv("BOT_TOKEN")
    app = ApplicationBuilder().token(tke).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & filters.ChatType.GROUPS, track_users))
    app.add_handler(MessageHandler(filters.TEXT & filters.ChatType.GROUPS, mention_all))

    await app.run_polling()

if __name__ == '__main__':
    import asyncio
    from telegram.ext import ApplicationBuilder

    tke = os.getenv("BOT_TOKEN")
    app = ApplicationBuilder().token(tke).build()

    load_members()
    app.add_handler(CommandHandler("all",mention_all))
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & filters.ChatType.GROUPS, track_users))
    app.add_handler(MessageHandler(filters.TEXT & filters.ChatType.GROUPS, mention_all))


    app.run_polling()  # <--- без await и без asyncio.run()
