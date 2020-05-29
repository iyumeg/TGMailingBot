from telegram import Update, Chat
from telegram.ext import CallbackContext


def new_chat_members_handler(update: Update, callback: CallbackContext):
    if callback.bot.id in [member.id for member in update.message.new_chat_members]:
        chat: Chat = update.message.chat
        chats: dict = callback.bot_data.setdefault('chats', {})
        chats[chat.id] = chat.title
