from dataclasses import dataclass
from datetime import time, datetime


@dataclass
class MailingModel:
    message: str = None
    chat_title: str = None
    chat_id: int = None
    send_time: time = None
    end_date: datetime = None
