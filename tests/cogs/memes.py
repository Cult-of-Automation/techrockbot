import discord
import re
from discord.ext import commands

from tests.decorators import mod_command, staff_command
from tests.variables import GuildConfig, _get

class Memes(commands.Cog, name='Miscellaneous'):

    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_message(self, message):
        if _get(message.guild.id, 'toggle', 'memes') is False:
            return
        if re.search(" do(es)? ?n'?o?t work", message.content.lower()):
            await message.channel.send('Welcome to BE')

    @commands.command(name='alive')
    async def alive(self, ctx):
        """Check if TRB is alive"""
        await ctx.message.add_reaction('\U0001F44D')

    @commands.command(name='toggle_memes')
    @staff_command()
    async def toggle_memes(self, ctx):
        """Toggle 'Welcome to BE' listener"""
        with GuildConfig(ctx.guild.id) as guildconfig:
            memes = not guildconfig['toggle']['memes']
            guildconfig['toggle']['memes'] = memes
        await ctx.send(f'`Welcome to BE` set to {memes}')

    @commands.command(name='say')
    @mod_command()
    async def say(self, ctx, *, content:str):
        """Make TRB say something... unoffensive"""
        await ctx.message.delete()
        await ctx.send(content)
            
def setup(bot):
    bot.add_cog(Memes(bot))