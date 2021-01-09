import logging
import asyncio
import os
import discord
from wowapi import WowApi
from chatterbot import ChatBot
from credentials import db, token, bnet_cid, bnet_secret

intents = discord.Intents.default()
intents.members = True
client = discord.Client(intents=intents)
warnList = []
realmStatus = ["Online"]

permitedChannels = [781422176472924160]
officerChannel = 382859094123610113
announcementChannel = 339505925058723840
warnChannel = 722604230434619462
guildMasterRoleID = 339507321506103296
raiderRoleID = 382855295552061440
socialRoleID = 709005091927097354
WCLogsWebHookID = 786136417457274931
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

async def checkServer():
    api = WowApi(bnet_cid, bnet_secret)
    realm = api.get_connected_realm(region='us', namespace='dynamic-us', locale='pt_BR', id=realmID)
    if 'UP' not in str(realm) and "Online" in realmStatus:
        await client.get_channel(announcementChannel).send("Parace que o servidor caiu, pessoal, vou avisar aqui quando voltar, mas qualquer coisa podem pedir pra eu avisar por DM.")
        realmStatus.pop()
        realmStatus.append("Offline")
    elif 'UP' in str(realm) and "Offline" in realmStatus:
        await client.get_channel(announcementChannel).send("O servidor voltou, pessoal!")
        for player in warnList:
            await player.send("O servidor voltou, bro, bora lá.")
        warnList.clear()
        realmStatus.pop()
        realmStatus.append("Online")
    if 'UP' not in str(realm):
        return False
    else:
        return True

@client.event
async def on_ready():
    timer = 600
    while True:
        if await checkServer():
            timer = 600
        else:
            timer = 60
        await asyncio.sleep(timer)

@client.event
async def on_member_join(member):
    await member.edit(nick = member.display_name.lower().title())
    await member.add_roles(member.guild.get_role(socialRoleID))
    await member.send("Seja bem-vindo à Dagon! Caso tenha sido convidado por um dos oficiais entre em qualquer sala que eles já vão te puxar.")

@client.event
async def on_member_remove(member):
    await  client.get_channel(officerChannel).send("O " + member.display_name + " viadinho acabou de sair do servidor, deve ter ido dar.")

@client.event
async def on_member_update(before, after):
    if ("778819742928601109" not in str(before.roles)) and ("778819742928601109" in str(after.roles)):
        await after.send("Parabéns por ter sido aprovado na entrevista! Agora você é um dos trainees da Dagon! Não se esqueça de dar uma boa lida no #bem-vindo e muito boa sorte nas próximas etapas do processo!")
    elif ("382855295552061440" not in str(before.roles)) and ("382855295552061440" in str(after.roles)):
        await after.send("Opa! Aí sim! Agora você é um titular da Dagon, meus parabéns! Quando tiver um tempo vamos conversar um pouco, é só me chamar pelo nome ou ir até o meu canal, quem sabe assim um dia eu fico menos estúpido.")

@client.event
async def on_message(message):

    if message.content.startswith("!") and message.channel.id in permitedChannels:
        await message.channel.send("Canal errado, bro, pra falar com outros bots chama eles pelo #geral.")

    elif message.content.startswith("!prune"):
        if message.guild.get_role(guildMasterRoleID) in message.author.roles:
            try:
                amount = int(message.content.split()[1])
                await message.channel.purge(limit = amount + 1)
            except:
                await message.channel.send("Uso incorreto do comando prune, por favor verifique a sintaxe.")
        else:
            await message.channel.send("Você não tem permissão para usar o comando prune.")

    elif message.author.id == WCLogsWebHookID:
        await message.channel.send(f"Logs de hoje, {message.guild.get_role(raiderRoleID).mention}:\n"+message.embeds[0].url)
        await message.delete()

    elif message.channel.id == warnChannel:
        for member in message.guild.members:
            if message.guild.get_role(raiderRoleID) in member.roles:
                if len(message.embeds) == 0 and len(message.attachments) == 0:
                    await member.send("**Nova mensagem no #avisos!**\n\n"+message.content)
                else:
                    await member.send("**Nova mensagem no #avisos!**\nCheca lá porque ela tem algum anexo que não consigo enviar por aqui.")

    elif message.author != client.user and ("!remind" in message.content or "!remindme" in message.content):

            if "Online" in realmStatus:
                await message.channel.send("Não sei do que está falando, aqui pra mim o servidor está aberto.")
            else:
                warnList.append(message.author)
                await message.channel.send("Pode deixar, quando o servidor voltar eu te aviso.")

    elif message.author != client.user and ("!server" in message.content or "!realm" in message.content):
        if await checkServer():
            await message.channel.send("Até onde sei está tudo em ordem com o servidor")
        else:
            await message.channel.send("Parece que o servidor está com problemas mesmo, se quiser que eu te avise quando ele voltar ao normal é só pedir usando !remindme.")

    elif message.channel.id == officerChannel:

        if "A new" in message.content:
            aux = message.content.split()
            link = aux[len(aux) - 1]
            role = aux[2]
            if role == "Death" or role == "Demon":
                role += " "+aux[3]
            await message.delete()
            await client.get_channel(officerChannel).send("Olha aí o "+role+" arrombado querendo raidar com a gente: "+link)

        elif "application has been" in message.content:
            await message.channel.purge(limit = 2)

        elif "application" in message.content:
            await message.delete()

    elif message.author != client.user:

        if message.channel.id in permitedChannels:
            await message.channel.send(chatbot.get_response(message.content))

        elif ("mekgorod" in message.content or "Mekgorod" in message.content) and message.channel not in permitedChannels:
            await message.channel.send("Quem ousa?")
            permitedChannels.append(message.channel)
            await asyncio.sleep(60)
            permitedChannels.pop()
            await message.channel.send("Não me pertube mais.")

client.run(token)