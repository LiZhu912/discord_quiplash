import discord
from discord.ext import commands
import json
import praw

token = secrets['token']

bot = commands.Bot(command_prefix='$')

initial_extensions = ['cogs.quiplash']

if __name__ == '__main__':
    for extension in initial_extensions:
        bot.load_extension(extension)

@bot.event
async def on_ready():
    print('Booted')


bot.run(token)
