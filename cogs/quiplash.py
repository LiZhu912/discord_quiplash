import discord
import praw
import json
from discord.ext import commands


with open('config.json', 'r') as f:
    secrets = json.loads(f.read())

# Reddit API
reddit = praw.Reddit(client_id = 'PqzN5d34xPFatA',
                     client_secret = secrets['reddit']['client_secret'],
                     username = secrets['reddit']['username'],
                     password = secrets['reddit']['password'],
                     user_agent = 'ask_discord',)
subreddit = reddit.subreddit('AskOuija')
hot_ouija = subreddit.hot()


def get_prompt():
    for submission in hot_ouija:
        if not submission.stickied:
            return submission.title

class Game(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.round = 1
        #light blue, blue, green, purple, red
        self.round_colors = [0xadd8e6, 0x6495ed, 0xe53fe5, 0xff0000, 0xffb700]

    def next_round(self):
        self.round +=1

    def get_round_color(self):
        return self.round_colors[self.round-1]

    def over(self):
        self.round = 1
        
    @commands.command()
    async def ping(self, ctx):
        await ctx.send('pong')
        
    @commands.command()
    async def prompt(self, ctx):
        prompt = get_prompt()
        embed = discord.Embed(title=f'Round {self.round}',
                              colour= Game.get_round_color(self))
        embed.add_field(name='Prompt:', value=prompt)
        if self.round == 4:
            embed.set_footer(text='points are doubled')
        elif self.round == 5:
            embed.set_footer(text='points are tripled')
        await ctx.send(content='ROUND BEGIN!', embed=embed)
        if self.round < 5:
            Game.next_round(self)
        if self.round == 5:
            Game.over(self)
        
       
def setup(bot):
    bot.add_cog(Game(bot))
