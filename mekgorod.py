import logging
import asyncio
import os
import discord
from selenium import webdriver
from selenium.webdriver.firefox.firefox_binary import FirefoxBinary
from bs4 import BeautifulSoup
from chatterbot import ChatBot
from chatterbot.trainers import ChatterBotCorpusTrainer
from credentials import db, token

client = discord.Client()
channels = [781422176472924160]
realmstatusurl = "https://worldofwarcraft.com/en-us/game/status/us"

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

        elif message.content == "mekgorod" or message.content == "Mekgorod":
            await message.channel.send("Quem ousa?")
            channels.append(0)
            await asyncio.sleep(60)
            channels.pop()
            await message.channel.send("Não me pertube mais.")

@client.event
async def on_message(message):

    if message.author != client.user:

        if message.content == "mekgorod, me avisa quando o servidor abrir":
            status = 'Online'
            binary = FirefoxBinary('/usr/lib/firefox/firefox')
            fireFoxOptions = webdriver.FirefoxOptions()
            fireFoxOptions.set_headless()
            driver = webdriver.Firefox(firefox_binary=binary, firefox_options=fireFoxOptions)
            driver.get(realmstatusurl)
            soup = BeautifulSoup(driver.page_source, 'html.parser')
            realms = soup.find_all("div", {'class': 'SortTable-row'})
            for realm in realms:
                if 'Azralon' in str(realm):
                    if 'Offline' in str(realm):
                        status = 'Offline'
                        print('Offline, aguardando')
                    else:
                        await message.channel.send("Como assim, mano? O server tá aberto.")
            
            while(status == 'Offline'):
                print('Checando novamente! 5 minutos')
                await asyncio.sleep(5)
                print('Checando novamente!')
                binary = FirefoxBinary('/usr/lib/firefox/firefox')
                fireFoxOptions = webdriver.FirefoxOptions()
                fireFoxOptions.set_headless()
                driver = webdriver.Firefox(firefox_binary=binary, firefox_options=fireFoxOptions)
                driver.get(realmstatusurl)
                soup = BeautifulSoup(driver.page_source, 'html.parser')
                realms = soup.find_all("div", {'class': 'SortTable-row'})
                for realm in realms:
                    if 'Azralon' in str(realm):
                        if 'Online' in str(realm):
                            status = 'Online'
                            await message.author.send("Abriu, mano.")

client.run(token)