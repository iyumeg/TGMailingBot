from telegram import Update
from telegram.ext import CallbackContext

from handlers.add_mailing import add_mailing_handler
from models.mailing_model import MailingModel
from utils.enums import AddMailStage, ConversationDirection
from settings import ADMIN_USERNAME


def add_mailing_command(update: Update, callback: CallbackContext):
    if update.effective_user.username != ADMIN_USERNAME:
        return

    callback.user_data['add_mail_stage'] = AddMailStage.MESSAGE
    callback.user_data['add_mail_direction'] = ConversationDirection.ASK
    callback.user_data['add_mail_model'] = MailingModel()
    add_mailing_handler(update, callback)
