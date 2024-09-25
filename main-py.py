import os
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters
from config import BOT_TOKEN, GOOGLE_CLIENT_ID, GOOGLE_CLIENT_SECRET, GOOGLE_REDIRECT_URI
from google_auth_oauthlib.flow import Flow
from googleapiclient.discovery import build
import base64

# OAuth 2.0 scopes
SCOPES = ['https://www.googleapis.com/auth/gmail.readonly']

# Dictionary to store user credentials
user_credentials = {}

def start(update, context):
    context.bot.send_message(chat_id=update.effective_chat.id, 
                             text="Welcome! This bot will help you scan your emails for receipts. Use /login to get started.")

def help(update, context):
    context.bot.send_message(chat_id=update.effective_chat.id, 
                             text="Use /login to authenticate with Gmail. Then use /scan to search for receipts.")

def login(update, context):
    flow = Flow.from_client_secrets_file(
        'credentials/client_secret.json',
        scopes=SCOPES,
        redirect_uri=GOOGLE_REDIRECT_URI
    )
    
    authorization_url, _ = flow.authorization_url(prompt='consent')
    
    context.bot.send_message(chat_id=update.effective_chat.id, 
                             text=f"Please visit this URL to authorize the application: {authorization_url}")
    
    # Store the flow object for later use
    context.user_data['flow'] = flow

def handle_oauth_callback(update, context):
    # This function would be called when the user provides the OAuth code
    # You'd need to set up a way for the user to input this code
    flow = context.user_data.get('flow')
    if not flow:
        context.bot.send_message(chat_id=update.effective_chat.id, 
                                 text="Please use /login first.")
        return

    # For simplicity, let's assume the user sends the code directly
    code = update.message.text

    try:
        flow.fetch_token(code=code)
        credentials = flow.credentials
        user_credentials[update.effective_user.id] = credentials
        context.bot.send_message(chat_id=update.effective_chat.id, 
                                 text="Successfully logged in! You can now use /scan to search for receipts.")
    except Exception as e:
        context.bot.send_message(chat_id=update.effective_chat.id, 
                                 text=f"An error occurred: {str(e)}")

def scan(update, context):
    credentials = user_credentials.get(update.effective_user.id)
    if not credentials:
        context.bot.send_message(chat_id=update.effective_chat.id, 
                                 text="Please login first using /login")
        return

    try:
        service = build('gmail', 'v1', credentials=credentials)
        results = service.users().messages().list(userId='me', q='subject:receipt').execute()
        messages = results.get('messages', [])

        if not messages:
            context.bot.send_message(chat_id=update.effective_chat.id, 
                                     text="No receipts found.")
        else:
            for message in messages[:5]:  # Limit to first 5 receipts
                msg = service.users().messages().get(userId='me', id=message['id']).execute()
                subject = next(header['value'] for header in msg['payload']['headers'] if header['name'] == 'Subject')
                context.bot.send_message(chat_id=update.effective_chat.id, 
                                         text=f"Found receipt: {subject}")
    except Exception as e:
        context.bot.send_message(chat_id=update.effective_chat.id, 
                                 text=f"An error occurred while scanning: {str(e)}")

def main():
    updater = Updater(BOT_TOKEN, use_context=True)
    dp = updater.dispatcher

    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(CommandHandler("help", help))
    dp.add_handler(CommandHandler("login", login))
    dp.add_handler(CommandHandler("scan", scan))
    dp.add_handler(MessageHandler(Filters.text & ~Filters.command, handle_oauth_callback))

    updater.start_polling()
    updater.idle()

if __name__ == '__main__':
    main()
