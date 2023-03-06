import discord
import openai
import requests
from discord.ext import commands

client = commands.Bot(command_prefix='!')

allowed_channels = []
while True:
    channel = input("Bitte die ID eines erlaubten Kanals eingeben (oder Enter zum Beenden): ")
    if not channel:
        break
    try:
        allowed_channels.append(int(channel))
    except ValueError:
        print("Ungültige Kanal-ID.")

banned_users = set()

banned_users_file = 'banned_users.txt'

try:
    with open(banned_users_file, 'r') as f:
        banned_users = set(int(line.strip()) for line in f)
except FileNotFoundError:
    pass

openai.api_key = input("Bitte geben Sie Ihren OpenAI-API-Schlüssel ein: ")

model_engine = "text-davinci-002"

@client.event
async def on_ready():
    print(f'{client.user.name} is ready.')

@client.event
async def on_message(message):
    if message.channel.id in allowed_channels and not message.author.bot:
        if message.author.id in banned_users:
            return

        command, *args = message.content.split()

        if command == '!chat':
            prompt = f"Antworte inteligent, gelassen auf Deutsch. Hier meine Nachricht: {message.content.replace('!chat', '')}\nAntwort:"
            response = openai.Completion.create(
                engine=model_engine,
                prompt=prompt,
                max_tokens=2000,
                n=1,
                stop=None,
                temperature=0.5,
            )
            answer = response.choices[0].text.strip()

            await message.channel.send(f'{message.author.mention} {answer}')

        elif command == '!ban' and message.author.id == 514907234644393996:
            if not args:
                await message.channel.send(f'{message.author.mention} Bitte gib eine Nutzer-ID an.')
                return

            try:
                user_id = int(args[0])
            except ValueError:
                await message.channel.send(f'{message.author.mention} Ungültige Nutzer-ID.')
                return

            banned_users.add(user_id)
            with open(banned_users_file, 'a') as f:
                f.write(f'{user_id}\n')

            await message.channel.send(f'{message.author.mention} {args[0]} wurde gesperrt.')

    elif message.content.startswith(f'<@!{client.user.id}>') and not any(role.name == 'Bot-Verwalter' for role in message.author.roles):
        await message.channel.send(f'{message.author.mention} Bitte benutze "!chat" oder "!ban".')
        return

client.run(input("Bitte geben Sie Ihren Discord-Bot-Token ein: "))
