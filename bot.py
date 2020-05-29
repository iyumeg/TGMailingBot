import logging

from telegram.ext import Updater, MessageHandler, Filters, PicklePersistence, CommandHandler, CallbackQueryHandler

from commands.add_mailing import add_mailing_command
from commands.start import start_command_handler
from handlers.add_mailing import add_mailing_handler
from handlers.callback_data_handler import callback_handler
from handlers.left_chat_memeber import left_chat_member_handler
from handlers.new_chat_members import new_chat_members_handler
from jobs.sender import sender_job
from settings import MAILING_JOBS, TOKEN, PROXY_URL

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.DEBUG)

updater = Updater(
    token=TOKEN,
    use_context=True, request_kwargs={'proxy_url': PROXY_URL},
    persistence=PicklePersistence(filename='data.tpp')
)
updater.dispatcher.add_handler(
    MessageHandler(filters=Filters.status_update.new_chat_members, callback=new_chat_members_handler)
)
updater.dispatcher.add_handler(
    MessageHandler(filters=Filters.status_update.left_chat_member, callback=left_chat_member_handler)
)
updater.dispatcher.add_handler(
    CommandHandler(filters=Filters.text, command='add', callback=add_mailing_command)
)
updater.dispatcher.add_handler(
    CommandHandler(filters=Filters.text, command='start', callback=start_command_handler)
)
updater.dispatcher.add_handler(
    MessageHandler(filters=Filters.text, callback=add_mailing_handler)
)
updater.dispatcher.add_handler(
    CallbackQueryHandler(callback=callback_handler)
)
models = updater.persistence.bot_data.setdefault('mailing_models', [])
for model in models:
    MAILING_JOBS[model.chat_id].append(
        updater.job_queue.run_daily(callback=sender_job, time=model.send_time, context=model)
    )

updater.start_polling()
updater.idle()
