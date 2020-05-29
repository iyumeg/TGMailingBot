from datetime import time, datetime

from dateutil.tz import tzlocal
from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import CallbackContext

from jobs.sender import sender_job
from utils.enums import AddMailStage, ConversationDirection
from settings import MAILING_JOBS


def _time_validator(value):
    try:
        hour, minute = value.split(':')
        _time = time(hour=int(hour), minute=int(minute), tzinfo=tzlocal())
        return _time
    except Exception:
        raise ValueError


def _date_validator(value):
    try:
        _datetime = datetime.strptime(value, '%d.%m.%Y')
        return _datetime
    except Exception:
        raise ValueError


def _chat_validator(value):
    raise ValueError


stage_conversation = {
    AddMailStage.MESSAGE: AddMailStage.CHAT,
    AddMailStage.CHAT: AddMailStage.SEND_TIME,
    AddMailStage.SEND_TIME: AddMailStage.END_DATE,
    AddMailStage.END_DATE: AddMailStage.FINISH
}

questions = {
    AddMailStage.MESSAGE: {
        'text': 'Введите сообщение для рассылки', 'validator': lambda x: x.strip(), 'field': 'message'
    },
    AddMailStage.SEND_TIME: {
        'text': 'Введите время отправки (HH:mm)', 'validator': _time_validator, 'field': 'send_time'
    },
    AddMailStage.CHAT: {
        'text': 'Выберите чат', 'validator': _chat_validator, 'field': 'chat_id'
    },
    AddMailStage.END_DATE: {
        'text': 'Введите дату окончания рассылки (dd.mm.YYYY)', 'validator': _date_validator, 'field': 'end_date'
    }
}


def add_mailing_handler(update: Update, callback: CallbackContext):
    stage = callback.user_data.get('add_mail_stage')
    direction = callback.user_data.get('add_mail_direction')
    model = callback.user_data.get('add_mail_model')
    if not stage or not direction:
        return False

    if stage is AddMailStage.FINISH:
        callback.user_data.pop('add_mail_stage', None)
        callback.user_data.pop('add_mail_direction', None)
        model = callback.user_data.pop('add_mail_model')
        models = callback.bot_data.setdefault('mailing_models', [])
        models.append(model)
        job = callback.job_queue.run_daily(callback=sender_job, time=model.send_time, context=model)
        MAILING_JOBS[model.chat_id].append(job)
        text = f'Рассылка для chat_id <b>{model.chat_title}</b> добавлена до <b>' \
               f'{model.end_date.strftime("%d.%m.%Y")}</b>'
        callback.bot.send_message(chat_id=update.message.chat_id, text=text, parse_mode='HTML')
        return

    reply_markup = None
    question = questions.get(stage)

    if direction is ConversationDirection.ASK:
        if stage is AddMailStage.CHAT:
            chats = callback.bot_data.get('chats', {})
            buttons = [[InlineKeyboardButton(text=chat_title, callback_data=f'chats.{chat_id}')
                        for chat_id, chat_title in chats.items()],
                       [InlineKeyboardButton(text='Обновить', callback_data='chats.refresh')]]
            reply_markup = InlineKeyboardMarkup(buttons)
        callback.bot.send_message(
            chat_id=update.effective_message.chat.id, text=question['text'], reply_markup=reply_markup
        )
        callback.user_data['add_mail_direction'] = ConversationDirection.ANSWER
    elif direction is ConversationDirection.ANSWER:
        answer = update.effective_message.text
        try:
            validator = question['validator']
            if validator is not None:
                answer = validator(answer)
            setattr(model, question['field'], answer)
            callback.user_data['add_mail_direction'] = ConversationDirection.ASK
            callback.user_data['add_mail_stage'] = stage_conversation[stage]
            add_mailing_handler(update, callback)
        except ValueError:
            callback.bot.send_message(chat_id=update.effective_message.chat.id, text='Попробуйте еще раз')
