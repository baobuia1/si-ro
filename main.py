import os
import copy
from dotenv import load_dotenv
import discord
from discord.ext import commands

'''Setting up'''

intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(
    command_prefix=commands.when_mentioned_or('sfc!'),
    case_insensitive=True,
    intents=intents
)

@bot.event
async def on_ready():
    print('hi')
    print(bot.user)

'''Dev commands'''

class dev(commands.Cog, name='Developer Commands',guild_ids=[1484925834849681489]):
    def __init__(self, bot):
        self.bot = bot
    
    async def check_perm(self, ctx):
        return ctx.author.id == self.bot.owner_id
    
    @commands.slash_command(
        name='reload',
        aliases=['rl']
    )  
    async def reload(self, ctx, cog=all):
        '''
        Reloads a cog.
        '''
        extensions = dict(self.bot.extensions).copy()
        if cog == 'all':
            for extension in extensions:
                self.bot.unload_extension(extension)
                self.bot.load_extension(extension)
            await ctx.respond('done')
        elif cog in extensions:
            self.bot.unload_extension(cog)
            self.bot.load_extension(cog)
            await ctx.respond('done')
        else:
            await ctx.respond('not real')
    
    @commands.slash_command(
        name='unload',
        aliases=['ul']
    ) 
    async def unload(self, ctx, cog):
        '''
        Unload a cog.
        '''
        extensions = self.bot.extensions
        if cog not in extensions:
            await ctx.respond('not real')
            return
        self.bot.unload_extension(cog)
        await ctx.respond('done')
    
    @commands.slash_command(
        name='load'
    )
    async def load(self, ctx, cog):
        '''
        Loads a cog.
        '''
        try:
            self.bot.load_extension(cog)
            await ctx.respond('done')
        except commands.errors.ExtensionNotFound:
            await ctx.respond('not real')

    @commands.slash_command(
        name='listcogs',
        aliases=['lc']
    )
    async def listcogs(self, ctx):
        '''
        Returns a list of all enabled commands.
        '''
        msg = '```'
        msg += '\n'.join([str(cog) for cog in self.bot.extensions])
        msg += '\n```'
        await ctx.respond(msg)

if __name__ == '__main__':
    bot.add_cog(dev(bot))
    for filename in os.listdir("cogs"):
        if filename.endswith(".py"):
            bot.load_extension(f"cogs.{filename[:-3]}")

load_dotenv()
token = os.environ['TOKEN']
bot.run(token)
