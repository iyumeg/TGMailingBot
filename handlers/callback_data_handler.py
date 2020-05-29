from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.error import BadRequest
from telegram.ext import CallbackContext

from handlers.add_mailing import stage_conversation, add_mailing_handler
from utils.enums import ConversationDirection


def callback_handler(update: Update, callback: CallbackContext):
    message = update.effective_message
    callback_data = update.callback_query.data
    chats = callback.bot_data.get('chats', {})

    if callback_data == 'chats.refresh':
        buttons = [[InlineKeyboardButton(text=chat_title, callback_data=f'chats.{chat_id}')
                    for chat_id, chat_title in chats.items()],
                   [InlineKeyboardButton(text='Обновить', callback_data='chats.refresh')]]
        try:
            message.edit_reply_markup(reply_markup=InlineKeyboardMarkup(buttons))
        except BadRequest:
            pass
    else:
        _, chat_id = callback_data.split('.')
        stage = callback.user_data.get('add_mail_stage')
        model = callback.user_data.get('add_mail_model')

        model.chat_id = int(chat_id)
        model.chat_title = chats[model.chat_id]

        callback.user_data['add_mail_direction'] = ConversationDirection.ASK
        callback.user_data['add_mail_stage'] = stage_conversation[stage]
        add_mailing_handler(update, callback)
