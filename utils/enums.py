from enum import Enum


class ConversationDirection(Enum):
    ASK = 'aks'
    ANSWER = 'answer'


class AddMailStage(Enum):
    MESSAGE = 'message'
    CHAT = 'chat'
    SEND_TIME = 'send_time'
    END_DATE = 'end_date'
    FINISH = 'finish'
