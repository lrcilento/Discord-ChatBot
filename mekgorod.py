import asyncio
import os
import discord
import time
from blizzardapi import BlizzardApi
from credentials import bnet_cid, bnet_secret, token
from config import *

intents = discord.Intents.default()
intents.members = True
client = discord.Client(intents=intents)
warnList = []
mutedPeople = []
realmStatus = ["Online"]

helpString = "!prune [int]: Apaga um número (int) de mensagens do canal\n!mute [userID]: Impede um usuário (userID) de mandar mensagens\n!unmute [userID]: Desmuta um jogador previamente mutado\n!realm ou !server: Checa se o servidor está online\n!remind ou !remindme: Avisa quando o servidor voltar, caso esteja offline"

async def checkServer(offChecking):
    api = BlizzardApi(bnet_cid, bnet_secret)
    realm = api.wow.game_data.get_connected_realm(region='us', locale='pt_BR', connected_realm_id=realmID)
    if 'UP' not in str(realm) and "Online" in realmStatus:
        await client.get_channel(announcementChannel).send("Parace que o servidor caiu, pessoal, vou avisar aqui quando voltar, mas qualquer coisa podem pedir pra eu avisar por DM.")
        realmStatus.pop()
        realmStatus.append("Offline")
        if offChecking:
            return False
    elif 'UP' in str(realm) and "Offline" in realmStatus:
        await client.get_channel(announcementChannel).send("O servidor voltou, pessoal!")
        for player in warnList:
            await player.send("O servidor voltou, bro, bora lá.")
        warnList.clear()
        realmStatus.pop()
        realmStatus.append("Online")
        if offChecking:
            return False
    elif offChecking:
        return True
    if 'UP' not in str(realm):
        return False
    else:
        return True

@client.event
async def on_ready():
    print("Who dares to summons me?!")
    timer = 600
    while True:
        if await checkServer(False):
            timer = 600
        else:
            timer = 60
        await asyncio.sleep(timer)

"""
@client.event
async def on_voice_state_update(member, before, after):

    # Seguir seu mestre nos canais de voz

    if member.guild.get_role(guildMasterRoleID) in member.roles:

        if before.channel != after.channel:

            if after.channel is not None:
                try:
                    time.sleep(1)
                    await after.channel.connect()
                except:
                    time.sleep(1)
                    await member.guild.voice_client.disconnect()
                    try:
                        time.sleep(1)
                        await after.channel.connect()
                    except:
                       pass

            else:
                time.sleep(1)
                await member.guild.voice_client.disconnect()
"""

@client.event
async def on_member_join(member):

    # Correção de nome e boas-vindas:

    await member.edit(nick = member.display_name.lower().title())
    await member.add_roles(member.guild.get_role(socialRoleID))
    await member.send("Seja bem-vindo à Dagon! Caso tenha sido convidado por um dos oficiais entre em qualquer sala que eles já vão te puxar.")

@client.event
async def on_member_remove(member):

    # Aviso de saída do servidor:

    await  client.get_channel(officerChannel).send("O " + member.display_name + " viadinho acabou de sair do servidor, deve ter ido dar.")

@client.event
async def on_member_update(before, after):

    # Congratulações de avanço de cargo:

    if ("778819742928601109" not in str(before.roles)) and ("778819742928601109" in str(after.roles)):
        await after.send("Parabéns por ter sido aprovado na entrevista! Agora você é um dos trainees da Dagon! Não se esqueça de dar uma boa lida no #bem-vindo e muito boa sorte nas próximas etapas do processo!")
    elif ("382855295552061440" not in str(before.roles)) and ("382855295552061440" in str(after.roles)):
        await after.send("Opa! Aí sim! Agora você é um titular da Dagon, meus parabéns!")

@client.event
async def on_message(message):

    # Proteção contra usuários mutados:

    if str(message.author) in mutedPeople:
        await message.delete()

    # Aviso de canal errado:

    elif message.content.startswith("!") and message.channel.id in permitedChannels:
        await message.channel.send("Canal errado, bro, pra falar com outros bots chama eles pelo #geral.")

    # Listar comandos disponíveis:

    elif message.content.startswith("!help"):
        if message.guild.get_role(guildMasterRoleID) in message.author.roles:
            await message.author.send(helpString)

    # Comando '!prune':

    elif message.content.startswith("!prune"):
        if message.guild.get_role(guildMasterRoleID) in message.author.roles:
            try:
                amount = int(message.content.split()[1])
                await message.channel.purge(limit = amount + 1)
            except:
                await message.channel.send("Uso incorreto do comando prune, por favor verifique a sintaxe.")
        else:
            await message.channel.send("Você não tem permissão para usar o comando prune.")

    # Comando '!mute':

    elif message.content.startswith("!mute"):
        if message.guild.get_role(guildMasterRoleID) in message.author.roles:
            try:
                user = message.content.split()[1]
                mutedPeople.append(user)
                await message.channel.send("Feito.")
                user.send("Você está temporariamente mutado nesse serividor, em caso de dúvidas procure o Sinclaire.")
            except:
                await message.channel.send("Uso incorreto do comando prune, por favor verifique a sintaxe.")
        else:
            await message.channel.send("Você não tem permissão para usar o comando prune.")

    # Comando '!unmute':

    elif message.content.startswith("!unmute"):
        if message.guild.get_role(guildMasterRoleID) in message.author.roles:
            try:
                user = message.content.split()[1]
                if user in mutedPeople:
                    mutedPeople.remove(user)
                    await message.channel.send("Não concordo, mas tudo bem...")
                else:
                    await message.channel.send("O jogador selecionado não está mutado.")
            except:
                await message.channel.send("Uso incorreto do comando prune, por favor verifique a sintaxe.")
        else:
            await message.channel.send("Você não tem permissão para usar o comando prune.")

    # Proteção contra TikTok:

    elif "tiktok" in message.content or "tiktuk" in message.content:
        await message.delete()
        await message.author.send("É proibida qualquer referência ao TikTok nesse servidor, por favor comporte-se.")

    # Aviso de logs:

    elif message.author.id == WCLogsWebHookID:
        await message.channel.send(f"Logs de hoje, {message.guild.get_role(raiderRoleID).mention}:\n"+message.embeds[0].url)
        await message.delete()

    # Aviso de avisos:

    elif message.channel.id == warnChannel:
        for member in message.guild.members:
            if message.guild.get_role(raiderRoleID) in member.roles:
                if len(message.embeds) == 0 and len(message.attachments) == 0:
                    await member.send("**Nova mensagem no #avisos!**\n\n"+message.content)
                else:
                    await member.send("**Nova mensagem no #avisos!**\nCheca lá porque ela tem algum anexo que não consigo enviar por aqui.")

    # Aviso de queda/retorno do servidor:

    elif message.author != client.user and ("!remind" in message.content or "!remindme" in message.content):

            if "Online" in realmStatus:
                await message.channel.send("Não sei do que está falando, aqui pra mim o servidor está aberto.")
            else:
                warnList.append(message.author)
                await message.channel.send("Pode deixar, quando o servidor voltar eu te aviso.")

    elif message.author != client.user and ("!server" in message.content or "!realm" in message.content):
        if await checkServer(True) and "Online" in realmStatus:
            await message.channel.send("Até onde sei está tudo em ordem com o servidor")
        elif await checkServer(True) and "Offline" in realmStatus:
            await message.channel.send("Parece que o servidor está com problemas mesmo, se quiser que eu te avise quando ele voltar ao normal é só pedir usando !remindme.")

    # Aviso de apply:

    elif message.channel.id == officerChannel:

        if "A new" in message.content:
            aux = message.content.split()
            link = aux[len(aux) - 1]
            role = aux[2]
            if role == "Death" or role == "Demon":
                role += " "+aux[3]
            await message.delete()
            await client.get_channel(officerChannel).send("Olha aí o "+role+" querendo raidar com a gente: "+link)

client.run(token)
