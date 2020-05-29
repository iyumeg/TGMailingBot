from telegram import Update
from telegram.ext import CallbackContext

from settings import ADMIN_USERNAME


def start_command_handler(update: Update, callback: CallbackContext):
    if update.effective_user.username != ADMIN_USERNAME:
        return
    callback.bot_data['admin_chat_id'] = update.effective_chat.id
    callback.bot.send_message(chat_id=update.effective_chat.id, text='Привет! Я, projt2501')
