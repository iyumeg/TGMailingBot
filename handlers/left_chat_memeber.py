from telegram import Update, Chat
from telegram.ext import CallbackContext

from settings import MAILING_JOBS


def left_chat_member_handler(update: Update, callback: CallbackContext):
    if update.message.left_chat_member.id != callback.bot.id:
        return
    chat: Chat = update.message.chat
    chats: dict = callback.bot_data.get('chats', {})
    chats.pop(chat.id, None)
    admin_chat_id = callback.bot_data.get('admin_chat_id')
    for job in MAILING_JOBS[chat.id]:
        job.schedule_removal()
    if admin_chat_id is not None:
        text = f'Бот удален из чата <b>{chat.title}</b> все рассылки в этот чат удалены'
        callback.bot.send_message(chat_id=admin_chat_id, text=text, parse_mode='HTML')
