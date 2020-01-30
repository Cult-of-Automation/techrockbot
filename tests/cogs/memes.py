import discord
import re
from discord.ext import commands
from tests.constants import Roles
from tests.decorators import with_role

class Memes(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        print('Memes are loaded')

    @commands.Cog.listener()
    async def on_message(self, message):
        if re.search(" do(es)? ?n'?o?t work", message.content.lower()):
            await message.channel.send('Welcome to BE')

    @commands.command(name='alive')
    async def alive(ctx):
        await ctx.message.add_reaction('\U0001F44D')

    @commands.command(name='say')
    @with_role(Roles.admin)
    async def say(self, ctx, *, content:str):
        await ctx.message.delete()
        await ctx.send(content)
            
def setup(bot):
    bot.add_cog(Memes(bot))