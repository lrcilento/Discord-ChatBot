import logging
import asyncio
import os
import discord
from wowapi import WowApi
from bs4 import BeautifulSoup
from chatterbot import ChatBot
from chatterbot.trainers import ChatterBotCorpusTrainer
from credentials import db, token, bnet_cid, bnet_secret

client = discord.Client()
channels = [781422176472924160]
realmstatusurl = "https://worldofwarcraft.com/en-us/game/status/us"
realmID = 3209

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

    if message.author != client.user and message.content != "mekgorod, me avisa quando o servidor abrir":

        if message.channel.id in channels or 0 in channels:
            await message.channel.send(chatbot.get_response(message.content))

        elif "mekgorod" or "Mekgorod" in message.content:
            await message.channel.send("Quem ousa?")
            channels.append(0)
            await asyncio.sleep(60)
            channels.pop()
            await message.channel.send("Não me pertube mais.")

    if message.author != client.user and message.content == "mekgorod, me avisa quando o servidor abrir":

            status = 'Online'
            api = WowApi(bnet_cid, bnet_secret)
            realm = api.get_connected_realm(region='us', namespace='dynamic-us', locale='pt_BR', id=realmID)
            if 'UP' in str(realm):
                await message.channel.send("Como assim, mano? O server tá aberto.")
                status = 'Offline'
            else:
                status = 'Offline'
                await message.channel.send("Pode deixar, mano.")
            
            while(status == 'Offline'):
                await asyncio.sleep(60)
                realm = api.get_connected_realm(region='us', namespace='dynamic-us', locale='pt_BR', id=realmID)
                if 'UP' in str(realm):
                    print('OPEN')
                    status = 'Online'
                    await message.author.send("Abriu, mano.")

client.run(token)