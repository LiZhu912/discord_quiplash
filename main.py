import discord
from discord.ext import commands
import json
import praw

token = 'NTU2OTI5NDc2Mzc0NjkxODQw.XNBqJw.qwoQXsv2dkhYpqvNFQjXzpzSH4Q'

bot = commands.Bot(command_prefix='$')

initial_extensions = ['cogs.quiplash']

if __name__ == '__main__':
    for extension in initial_extensions:
        bot.load_extension(extension)

@bot.event
async def on_ready():
    print('Booted')


bot.run(token)
