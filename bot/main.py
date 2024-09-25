from telegram.ext import Updater, CommandHandler
import os

BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN")

def start(update, context):
    context.bot.send_message(chat_id=update.effective_chat.id, 
                             text="Welcome! Please visit https://gconnect-kappa.vercel.app to log in with your Gmail account.")

def help(update, context):
    context.bot.send_message(chat_id=update.effective_chat.id, 
                             text="Visit https://gconnect-kappa.vercel.app to log in. Then use /scan to search for receipts.")

def scan(update, context):
    # Implement your scanning logic here
    context.bot.send_message(chat_id=update.effective_chat.id, 
                             text="Scanning functionality not yet implemented.")

def main():
    updater = Updater(BOT_TOKEN, use_context=True)
    dp = updater.dispatcher

    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(CommandHandler("help", help))
    dp.add_handler(CommandHandler("scan", scan))

    updater.start_polling()
    updater.idle()

if __name__ == '__main__':
    main()
