from datetime import datetime

from telegram.ext import CallbackContext

from models.mailing_model import MailingModel


def sender_job(callback: CallbackContext):
    model: MailingModel = callback.job.context
    if datetime.now() > model.end_date:
        callback.job.schedule_removal()
        return

    callback.bot.send_message(chat_id=model.chat_id, text=model.message)
