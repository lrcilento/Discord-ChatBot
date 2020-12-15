import logging
from chatterbot import ChatBot
from chatterbot.trainers import ListTrainer
from credentials import db

logging.basicConfig(level=logging.INFO)

chatbot = ChatBot(
    "Mekgorod",
    storage_adapter={
        'import_path': "chatterbot.storage.SQLStorageAdapter",
        'database_uri': db
    },
    filters=["filters.get_recent_repeated_responses"]
)

trainer = ListTrainer(chatbot)

trainer.train([
    "Quem é a gata mais linda do mundo?",
    "A Laura"
]
)
