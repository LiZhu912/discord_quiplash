import discord
from discord.ext import commands
import praw
import json
import random as rand
import asyncio
import emoji

def text_has_emoji(text):
    for character in text:
        if character in emoji.UNICODE_EMOJI:
            return True
    return False

class Game(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.channel = None
        self.round = 1
        #light blue, blue, purple, red, orange
        self.round_colors = [0x6495ed, 0xe53fe5, 0xff0000, 0xffb700]
        self.game_on = False
        self.wr = None

        self.max_players = 8
        self.players = {}
        self.len_ready = 0
        self.first = None

        self.prompt_dict = {}

        self.accept_response = False


    def next_round(self):
        self.round +=1

    def get_len_players(self):
        return len(self.players)

    def get_round_color(self):
        return self.round_colors[self.round-1]

    def get_len_prompts(self):
        return len(self.prompt_dict[self.round])

    def game_over(self):
        self.round = 1

    def update_lobby(self):
        embed = discord.Embed(title='Game Lobby')
        embed.add_field(name='Waiting for Players... ', value='('+str(self.get_len_players())+'/8)')
        return embed

    def update_wr(self):
        wr_embed = discord.Embed(title=f'Round {self.round}', colour= self.get_round_color())
        wr_embed.add_field(name="Waiting for players' responses...",value = '('+str(self.len_ready)+'/'+str(self.get_len_players()*2)+')')
        return wr_embed

    def instanceReddit(self,len_players):
        len_game_prompts = len_players*2*4
        with open('config.json', 'r') as f:
            secrets = json.loads(f.read())

            # Reddit API
            reddit = praw.Reddit(client_id = 'PqzN5d34xPFatA',
                                 client_secret = secrets['reddit']['client_secret'],
                                 username = secrets['reddit']['username'],
                                 password = secrets['reddit']['password'],
                                 user_agent = 'ask_discord',)
            subreddit = reddit.subreddit('AskOuija')
            hot_ouija = subreddit.hot(limit=len_game_prompts)
            
            return hot_ouija

    def get_prompts(self, len_players, subreddit):
        
        with open('cached_prompts.json','r') as f:
            if f.read():
                cp = json.load(f)
            else:
                cp = []


            for rounds in range(1,5):
                self.prompt_dict[rounds] = {}
                for prompt_num in range(1,len_players+1):
                    self.prompt_dict[rounds][prompt_num] = {}
                    continue

            print(4)

            player_selection1= [*self.players]
            player_selection2= [*self.players]
            count = 1
            print(5)
            print(player_selection1)
            print(player_selection2)
            for submission in subreddit:
                if not submission.stickied and '_' in submission.title and not text_has_emoji(submission.title):
                    if submission.title not in cp:
                        #cp.append(submission.title)
                        print(6)
                        
                        # Assign first player to a prompt.
                        selected_player1 = rand.choice(player_selection1)
                        player_selection1.remove(selected_player1)
                        self.players[selected_player1]['prompts'][self.round]['prompt'].append(submission.title)
                        self.players[selected_player1]['prompts'][self.round]['prompt_num'].append(count)
                        print(7)
                        
                        # Assign second player to a prompt.
                        selected_player2 = rand.choice(player_selection2)
                        print(selected_player2.name)
                        while selected_player1 == selected_player2:
                            print('while loop')
                            selected_player2 = rand.choice(player_selection2)
                        player_selection2.remove(selected_player2)
                        self.players[selected_player2]['prompts'][self.round]['prompt'].append(submission.title)
                        self.players[selected_player2]['prompts'][self.round]['prompt_num'].append(count)
                        print(8)
                        
                        self.prompt_dict[self.round][count] = {'prompt':submission.title,'players':{selected_player1:[], selected_player2:[]}}
                        print(9)
                        print(len_players)
                        if count == len_players:
                            break
                        else:
                            count +=1


    async def send_prompt(self):
        print(10)
        for player in self.players:
            

            player_prompts = self.players[player]['prompts'][self.round]['prompt']
        
            embed = discord.Embed(title=f'Round {self.round}',
                              colour= self.get_round_color())
            embed.add_field(name='Prompt A:', value=player_prompts[0])
            embed.add_field(name='Prompt B:', value=player_prompts[1], inline=False)
            
            if self.round == 3:
                embed.set_footer(text='points are doubled')
            elif self.round == 4:
                embed.set_footer(text='points are tripled')
                
            await player.send(content='ROUND BEGIN!', embed=embed)
            print(11)
            if self.round == 4:
                self.game_over()

    # caches a list of prompts
    def cache_prompts(self, prompt_list):
        with open('cached_prompts.json','r') as f:
            cp = json.load(f)
            cp += prompt_list
        with open('cached_prompts.json','w') as f:
            json.dump(cp)
            
    @commands.command()
    async def ping(self, ctx):
        await ctx.send('pong')

    @commands.command()
    async def create(self, ctx):
        if self.game_on:
            await ctx.send('A game is already in progress.')
        else:
            self.server = ctx.guild
            self.channel = ctx.channel
            
            self.players[ctx.author] = {'points':0, 'prompts':{1:{'prompt_num':[],'prompt':[],'responded':[False,False]}
                                                               ,2:{'prompt_num':[],'prompt':[],'responded':[False,False]}
                                                               ,3:{'prompt_num':[],'prompt':[],'responded':[False,False]}
                                                               ,4:{'prompt_num':[],'prompt':[],'responded':[False,False]}}}
            
            embed = discord.Embed(title='Game Lobby')
            embed.add_field(name='Waiting for Players... ', value='('+str(self.get_len_players())+'/8)')
            lobby = await self.channel.send(content='A game has been created.\n**React** to join | **$start** to start game', embed=embed)
            
            await lobby.add_reaction('\U0001F44D')
        
            @self.bot.event
            async def on_reaction_add(reaction, user):
                if not user.bot:
                    if self.get_len_players() < 8:
                        self.players[user] = {'points':0, 'prompts':{1:{'prompt_num':[],'prompt':[],'responded':[False,False]}
                                                               ,2:{'prompt_num':[],'prompt':[],'responded':[False,False]}
                                                               ,3:{'prompt_num':[],'prompt':[],'responded':[False,False]}
                                                               ,4:{'prompt_num':[],'prompt':[],'responded':[False,False]}}}
                        await lobby.edit(embed=self.update_lobby())
                    
    @commands.command()
    async def start(self, ctx):
        if self.game_on:
            await ctx.send('A game is already in progress.')
        else:
            self.game_on = True
            channel = self.channel
            await channel.send('A game has been started')
            len_players = self.get_len_players()
            print(1)
            subreddit = self.instanceReddit(len_players)
            print(2)
            print(self.game_on)
            while self.game_on:

                self.get_prompts(len_players, subreddit)
                print(3)
                
                await self.send_prompt()
                
                self.accept_response = True

                # Waiting for players' responses...
                self.wr = await channel.send(embed=self.update_wr())
                while self.len_ready < len_players*2:
                    await asyncio.sleep(2)
                    
                self.accept_response = False
                    
                await asyncio.sleep(3)
                await channel.send("Okay, let's jump right into the voting round. Pick your favorite response by smacking that like button.")
                await asyncio.sleep(3)
                await self.vote()

                await asyncio.sleep(2)
                await channel.send("\n**Alright! Round "+str(self.round)+" is over. Now we see who is on top in the standings.**")
                await asyncio.sleep(3)
                await self.get_standings()

                await asyncio.sleep(3)
                
                if self.round == 4:
                    await channel.send("Congratualations to "+self.first+"!")
                    self.game_on = False
                else:
                    await channel.send("\n**Nice work everyone. Next round's prompts will now be sent to you.**\n---------------------------------------------")
                    await asyncio.sleep(3)
                    self.next_round()


    @commands.command()
    async def a(self, ctx, *,answer):
        if self.accept_response and not self.players[ctx.author]['prompts'][self.round]['responded'][0]:
            prompt_num = self.players[ctx.author]['prompts'][self.round]['prompt_num'][0]
            self.prompt_dict[self.round][prompt_num]['players'][ctx.author].append(answer)
            self.len_ready +=1
            await self.wr.edit(embed=self.update_wr())
            await ctx.author.send('Response 1 delivered')
            self.players[ctx.author]['prompts'][self.round]['responded'][0] = True
        else:
            await ctx.author.send("I can't deliver response 1 now.")

    @commands.command()
    async def b(self, ctx, *,answer):
        if self.accept_response and not self.players[ctx.author]['prompts'][self.round]['responded'][1]:
            prompt_num = self.players[ctx.author]['prompts'][self.round]['prompt_num'][1]
            self.prompt_dict[self.round][prompt_num]['players'][ctx.author].append(answer)
                    
            self.len_ready +=1
            await self.wr.edit(embed=self.update_wr())
            await ctx.author.send('Response 2 delivered')
            self.players[ctx.author]['prompts'][self.round]['responded'][1] = True
        else:
            await ctx.author.send("I can't deliver response 2 now.")

    async def vote(self):
        channel = self.channel
        
        self.len_ready = 0
        prompt_dict = self.prompt_dict[self.round]
        for prompt in range(1,self.get_len_prompts()+1):
            prompt_str = prompt_dict[prompt]['prompt']
            vote_embed = discord.Embed(title=f'Round {self.round}', color = self.get_round_color())
            vote_embed.add_field(name='Prompt '+str(prompt)+':',value=prompt_str)
            await channel.send(embed=vote_embed)
            await asyncio.sleep(5)

            players = prompt_dict[prompt]['players']
            player1 = list(players.keys())[0]
            player2 = list(players.keys())[1]

            player1_answer = await channel.send(f'**{player1.name}\'s response:**\n{players[player1]}')
            await player1_answer.add_reaction('\U0001F44D')
            await asyncio.sleep(3)
            player2_answer = await channel.send(f'**{player2.name}\'s response:**\n{players[player2]}')
            await player2_answer.add_reaction('\U0001F44D')
            await asyncio.sleep(8)

            cache_answer1 = await channel.fetch_message(player1_answer.id)
            cache_answer2 = await channel.fetch_message(player2_answer.id)

            votedAlready = [player1,player2]
            for reaction in cache_answer1.reactions:
                async for user in reaction.users():
                    if not user in votedAlready and not user.bot:
                        if self.round == 3:
                            self.players[player1]['points'] += 60
                        elif self.round == 4:
                            self.players[player1]['points'] += 90
                        else:
                            self.players[player1]['points'] += 30
                            
                        votedAlready.append(user)
            for reaction in cache_answer2.reactions:
                async for user in reaction.users():
                    if not user in votedAlready and not user.bot:
                        if self.round == 3:
                            self.players[player1]['points'] += 60
                        elif self.round == 4:
                            self.players[player1]['points'] += 90
                        else:
                            self.players[player1]['points'] += 30
                        votedAlready.append(user)

    async def get_standings(self):
        channel = self.channel
        standings = []
        embed = discord.Embed(title='Standings', colour= self.get_round_color())
        for player in self.players:

            #temporary
            if player.name == 'LiZoom':
                self.players[player]['points']+=99
                
            standings.append((self.players[player]['points'],player.name))

        standings = sorted(standings, key=lambda tup: tup[0], reverse=True)
        
        for place in range(1,self.get_len_players()+1):
            if place == 1:
                embed.add_field(name=str(place)+'st',value=str(standings[place-1][1])+' : ' + str(standings[place-1][0]))
                self.first = str(standings[place-1][1])
            elif place == 2:
                embed.add_field(name=str(place)+'nd',value=str(standings[place-1][1])+' : ' + str(standings[place-1][0]))
            elif place == 3:
                embed.add_field(name=str(place)+'rd',value=str(standings[place-1][1])+' : ' + str(standings[place-1][0]))
            else:
                embed.add_field(name=str(place)+'th',value=str(standings[place-1][1])+' : ' + str(standings[place-1][0]))

        await channel.send(embed=embed)

                       
def setup(bot):
    bot.add_cog(Game(bot))
