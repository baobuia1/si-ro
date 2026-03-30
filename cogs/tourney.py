import random
import json
import random
import discord
from discord.ext import commands

class tourney(commands.Cog, name='Tourney Commands',guild_ids=[1484925834849681489]):
    def __init__(self,bot):
        self.bot = bot
    
    @commands.slash_command(
        name='roll',
        description='Roll a random number from 1 - 100'
    )
    async def roll(self,ctx):
        await ctx.respond(f'<@{ctx.author.id}> rolled {random.randint(1,100)}')
    
    @commands.slash_command(
        name='create_room',
        description='Create a channel for a match'
    )
    @commands.has_permissions(
        manage_channels=True
    )
    async def create(self,ctx,name:str):
        category = ctx.channel.category
        new_channel = await category.create_text_channel(name)
        with open('./data.json','r') as f:
            data = json.load(f)
        with open('./data.json','w') as f:
            data.append(
                {
                    'channel_id':new_channel.id,
                    'created':[ctx.author.id],
                    'maps':[],
                    'banned':[],
                    'picked':[]
                }
            )
            json.dump(data,f)
        await ctx.respond(f'Channel created <#{new_channel.id}>')

    @commands.slash_command(
        name='random_maps',
        description='Randomly choose maps for ban pick ()'
    )
    async def randomize(self,ctx,num:int,min_diff:float,max_diff:float):
        #check channel
        with open('./data.json') as fi:
            channel_data = json.load(fi)
        for channel in channel_data:
            if ctx.channel_id == channel['channel_id'] and ctx.author.id in channel['created']:
                #maps choosing
                with open('./maps.json') as f:
                    data = json.load(f)
                qualified = []
                for x in data:
                    if x['constant'] >= min_diff and x['constant'] <= max_diff:
                        qualified.append(x)
                print(qualified)
                chosen_maps = random.sample(qualified,k=num)
                msg = '```'
                for index,chosen_map in enumerate(chosen_maps):
                    msg += f'{index+1}. {chosen_map['song_name']}[{chosen_map['diff']}] - {chosen_map['constant']}\n'
                msg+='```'
                await ctx.respond(msg)

                #data handling
                for x in channel_data:
                    if x['channel_id'] == ctx.channel_id:
                        x['maps'] = chosen_maps
                with open('./data.json','w') as fi:
                    json.dump(channel_data,fi)

    @commands.slash_command(
        name='ban',
        description='Ban a map'
    )
    async def ban(self,ctx,map:int):
        map -= 1
        with open('./data.json') as f:
            data = json.load(f)
            for channel in data:
                if channel['channel_id'] == ctx.channel_id and ctx.author.id in channel['created']:
                    if map in channel['banned']:
                        await ctx.respond('Cannot ban a banned map')
                    else:
                        channel['banned'].append(map)
                        await ctx.respond(f'Picked {channel['maps'][map]}')
        
        with open('./data.json','w') as f:
            json.dump(data,f)
    
    @commands.slash_command(
        name='pick',
        description='Pick a map'
    )
    async def pick(self,ctx,map:int):
        map -= 1
        with open('./data.json') as f:
            data = json.load(f)
            for channel in data:
                if channel['channel_id'] == ctx.channel_id and ctx.author.id in channel['created']:
                    if map in channel['banned']:
                        await ctx.respond('Cannot pick a banned map')
                    elif map in channel['picked']:
                        await ctx.respond('Cannot pick a picked map')
                    else:
                        channel['picked'].append(map)
                        await ctx.respond(f'Picked {channel['maps'][map]}')
        
        with open('./data.json','w') as f:
            json.dump(data,f)
    
    @commands.slash_command(
        name='pool',
        description='Show a pool'
    )
    async def pool(self,ctx):
        with open('./data.json') as f:
            data = json.load(f)
            for channel in data:
                if channel['channel_id'] == ctx.channel_id:
                    msg = '```'
                    for index,chosen_map in enumerate(channel['maps']):
                        msg += f'{index+1}. {chosen_map['song_name']}[{chosen_map['diff']}] - {chosen_map['constant']}\n'
                    msg+='```'
                    await ctx.respond(msg)
    
    @commands.slash_command(
        name='add_ref',
        description='Add a referee to the match'
    )
    async def add_ref(self,ctx,ref:discord.Member):
        with open('./data.json') as f:
            data = json.load(f)
            for channel in data:
                if channel['channel_id'] == ctx.channel_id and ctx.author.id in channel['created']:
                    channel['created'].append(ref.id)
        with open('./data.json','w') as f:
            json.dump(data,f)

def setup(bot):
    bot.add_cog(tourney(bot))