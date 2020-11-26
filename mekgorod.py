import logging
import asyncio
import os
import discord
from chatterbot import ChatBot
from chatterbot.trainers import ChatterBotCorpusTrainer
from credentials import db, token

client = discord.Client()
channels = [781422176472924160]

logging.basicConfig(level=logging.INFO)

chatbot = ChatBot(
    "Mekgorod",
    storage_adapter={
        'import_path': "chatterbot.storage.SQLStorageAdapter",
        'database_uri': db
    },
    filters=["filters.get_recent_repeated_responses"]
)

@client.event
async def on_ready():
    print('Mekgorod Summoned!')    

@client.event
async def on_message(message):
    if message.author != client.user:
        if message.channel.id in channels or 0 in channels:
            output = chatbot.get_response(message.content)
            await message.channel.send(output)
            chatbot.get_response(output)
        elif message.content == "mekgorod" or message.content == "Mekgorod":
            await message.channel.send("Quem ousa?")
            channels.append(0)
            await asyncio.sleep(60)
            channels.pop()
            await message.channel.send("Não me pertube mais.")

        else:
            chatbot.get_response(message.content)

client.run(token)