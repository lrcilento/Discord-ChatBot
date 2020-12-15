import logging
import asyncio
import os
import discord
from wowapi import WowApi
from bs4 import BeautifulSoup
from chatterbot import ChatBot
from chatterbot.trainers import ChatterBotCorpusTrainer
from credentials import db, token, bnet_cid, bnet_secret

intents = discord.Intents.default()
intents.members = True
client = discord.Client(intents=intents)
channels = [781422176472924160]
realmID = 3209
warnList = []
realmStatus = ["Online"]

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
    api = WowApi(bnet_cid, bnet_secret)
    timer = 600
    while True:
        realm = api.get_connected_realm(region='us', namespace='dynamic-us', locale='pt_BR', id=realmID)
        if 'UP' not in str(realm) and "Online" in realmStatus:
            await client.get_channel(339505925058723840).send("Parace que o servidor caiu, pessoal, vou avisar aqui quando voltar, mas qualquer coisa podem pedir pra eu avisar por DM.")
            realmStatus.pop()
            realmStatus.append("Offline")
            timer = 60
        elif 'UP' in str(realm) and "Offline" in realmStatus:
            await client.get_channel(339505925058723840).send("O servidor voltou, pessoal!")
            for player in warnList:
                player.send("O servidor voltou, bro, bora lá.")
            warnList.clear()
            realmStatus.pop()
            realmStatus.append("Online")
            timer = 600
        await asyncio.sleep(timer)

@client.event
async def on_member_join(member):
    await member.send("Seja bem-vindo à Dagon! Caso tenha sido convidado por um dos oficiais entre em qualquer sala que eles já vão te puxar.")

@client.event
async def on_member_remove(member):
    await  client.get_channel(382859094123610113).send("O " + member.display_name + " viadinho acabou de sair do servidor.")

@client.event
async def on_member_update(before, after):
    if ("778819742928601109" not in str(before.roles)) and ("778819742928601109" in str(after.roles)):
        await after.send("Parabéns por ter sido aprovado na entrevista! Agora você é um dos trainees da Dagon! Não se esqueça de dar uma boa lida no #bem-vindo e muito boa sorte nas próximas etapas do processo!")
    elif ("382855295552061440" not in str(before.roles)) and ("382855295552061440" in str(after.roles)):
        await after.send("Opa! Aí sim! Agora você é um titular da Dagon, meus parabéns! Quando tiver um tempo vamos conversar um pouco, quem sabe assim um dia eu fico menos estúpido.")

@client.event
async def on_message(message):

    if message.author != client.user and "servidor abrir" not in message.content and "servidor voltar" not in message.content:

        if message.channel.id in channels or 0 in channels:
            await message.channel.send(chatbot.get_response(message.content))

        elif "mekgorod" in message.content or "Mekgorod" in message.content:
            await message.channel.send("Quem ousa?")
            channels.append(0)
            await asyncio.sleep(60)
            channels.pop()
            await message.channel.send("Não me pertube mais.")

    if message.author != client.user and ("servidor abrir" in message.content or "servidor voltar" in message.content):

            if "Online" in realmStatus:
                await message.channel.send("Como assim, mano? O server tá aberto.")
            else:
                warnList.append(message.author)
                await message.channel.send("Pode deixar, mano.")

client.run(token)