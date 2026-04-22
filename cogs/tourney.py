import time
import random
import json
import random
import asyncio
import discord
from discord.ext import commands

class deletion_view(discord.ui.View):
    @discord.ui.button(label='Confirm ✅')
    async def confirm_deletion(self,button,interaction):
        await interaction.channel.delete(reason='Finished match')


    @discord.ui.button(label='Cancel ❌')
    async def cancel_deletion(self,button,interaction):
        embed = discord.Embed(description='Cancelled deletion')
        self.disable_all_items()
        await interaction.response.edit_message(view=self)



class tourney(commands.Cog, name='Tourney Commands',guild_ids=[1484925834849681489]):
    def __init__(self,bot):
        self.bot = bot


    @commands.slash_command(
        name='roll',
        description='Roll a random number from 1 - 100'
    )
    async def roll(self,ctx):
        embed = discord.Embed(description=f'<@{ctx.author.id}> rolled {random.randint(1,100)} 🎲')
        await ctx.respond(embed=embed)


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
        with open('./data.json','r',encoding='utf-8') as f:
            data = json.load(f)
        with open('./data.json','w',encoding='utf-8') as f:
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
        embed = discord.Embed(description=f'Channel created <#{new_channel.id}>')
        await ctx.respond(embed=embed)


    @commands.slash_command(
        name='end_room',
        description='End the match and delete channel'
    )
    @commands.has_permissions(
        manage_channels=True
    )
    async def end(self,ctx):
        with open('./data.json','r',encoding='utf-8') as f:
            data = json.load(f)
        with open('./data.json','w',encoding='utf-8') as f:
            data[:] = [d for d in data if d.get('channel_id') != ctx.channel_id]
            json.dump(data,f)
        # Add confirmation here
        confirm_embed = discord.Embed(description='Please confirm that the match has ended')
        await ctx.respond(f'<@{ctx.author.id}>',embed=confirm_embed,view=deletion_view(timeout=10))


    @commands.slash_command(
        name='random_maps',
        description='Randomly choose maps to create a pool'
    )
    async def randomize(self,ctx,num:int,min_diff:float,max_diff:float):
        #check channel
        with open('./data.json',encoding='utf-8') as fi:
            channel_data = json.load(fi)
        for channel in channel_data:
            if ctx.channel_id == channel['channel_id'] and ctx.author.id in channel['created']:
                #maps choosing
                with open('./maps.json',encoding='utf-8') as f:
                    data = json.load(f)
                qualified = []
                for x in data:
                    if x['constant'] >= min_diff and x['constant'] <= max_diff:
                        qualified.append(x)
                chosen_maps = random.sample(qualified,k=num)
                maps = []
                for index,chosen_map in enumerate(chosen_maps):
                    maps.append(discord.Embed(title=f'Map number {index+1}',description=f'{chosen_map['song_name']} [{chosen_map['diff']} {chosen_map['constant']}]'))
                await ctx.respond(embeds=maps)

                #data handling
                for x in channel_data:
                    if x['channel_id'] == ctx.channel_id:
                        x['maps'] = chosen_maps
                with open('./data.json','w',encoding='utf-8') as fi:
                    json.dump(channel_data,fi)


    @commands.slash_command(
        name='ban',
        description='Ban a map'
    )
    async def ban(self,ctx,map:int):
        map -= 1
        with open('./data.json',encoding='utf-8') as f:
            data = json.load(f)
            for channel in data:
                if channel['channel_id'] == ctx.channel_id and ctx.author.id in channel['created']:
                    if map in channel['banned']:
                        await ctx.respond(embed=discord.Embed(description='Cannot ban a banned map'))
                    elif map in channel['picked']:
                        await ctx.respond(embed=discord.Embed(description='Cannot ban a picked map'))
                    else:
                        channel['banned'].append(map)
                        chosen_map = channel['maps'][map]
                        await ctx.respond(embed=discord.Embed(description=f'`{map+1}.` {chosen_map['song_name']} [{chosen_map['diff']}] has been banned.'))
        
        with open('./data.json','w',encoding='utf-8') as f:
            json.dump(data,f)


    @commands.slash_command(
        name='pick',
        description='Pick a map'
    )
    async def pick(self,ctx,map:int):
        map -= 1
        with open('./data.json',encoding='utf-8') as f:
            data = json.load(f)
            for channel in data:
                if channel['channel_id'] == ctx.channel_id and ctx.author.id in channel['created']:
                    if map in channel['banned']:
                        await ctx.respond(embed=discord.Embed(description='Cannot pick a banned map'))
                    elif map in channel['picked']:
                        await ctx.respond(embed=discord.Embed(description='Cannot pick a picked map'))
                    else:
                        channel['picked'].append(map)
                        chosen_map = channel['maps'][map]
                        await ctx.respond(embed=discord.Embed(description=f'`{map+1}.` {chosen_map['song_name']} [{chosen_map['diff']}] has been picked'))
        
        with open('./data.json','w',encoding='utf-8') as f:
            json.dump(data,f)


    @commands.slash_command(
        name='pool',
        description='Show a pool'
    )
    async def pool(self,ctx):
        with open('./data.json',encoding='utf-8') as f:
            data = json.load(f)
            for channel in data:
                if channel['channel_id'] == ctx.channel_id:
                    maps = []
                    for index,chosen_map in enumerate(channel['maps']):
                        if index not in channel['banned'] and index not in channel['picked']:
                            maps.append(discord.Embed(title=f'Map number {index+1}',description=f'{chosen_map['song_name']} [{chosen_map['diff']} {chosen_map['constant']}]'))
                        elif index in channel['picked']:
                            maps.append(discord.Embed(color=discord.Color.red(),title=f'Map number {index+1} PICKED',description=f'~~{chosen_map['song_name']} [{chosen_map['diff']} {chosen_map['constant']}]~~'))
                        elif index in channel['banned']:
                            maps.append(discord.Embed(color=discord.Color.red(),title=f'Map number {index+1} BANNED',description=f'~~{chosen_map['song_name']} [{chosen_map['diff']} {chosen_map['constant']}]~~'))
                    await ctx.respond(embeds=maps)


    @commands.slash_command(
        name='add_ref',
        description='Add a referee to the match'
    )
    async def add_ref(self,ctx,ref:discord.Member):
        with open('./data.json',encoding='utf-8') as f:
            data = json.load(f)
            for channel in data:
                if channel['channel_id'] == ctx.channel_id and ctx.author.id in channel['created']:
                    channel['created'].append(ref.id)
        with open('./data.json','w',encoding='utf-8') as f:
            json.dump(data,f)
        await ctx.respond(f'Added {ref.mention}')


    @commands.slash_command(
        name='remove_ref',
        description='Remove a referee from the match'
    )
    async def remove_ref(self,ctx,ref:discord.Member):
        with open('./data.json',encoding='utf-8') as f:
            data = json.load(f)
            for channel in data:
                if channel['channel_id'] == ctx.channel_id and ctx.author.id in channel['created']:
                    channel['created'].remove(ref.id)
        with open('./data.json','w',encoding='utf-8') as f:
            json.dump(data,f)
        await ctx.respond(f'Removed {ref.mention}')

def setup(bot):
    bot.add_cog(tourney(bot))