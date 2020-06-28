import re
from discord.ext import commands

from bot.decorators import mod_command, staff_command
from bot.constants import Emojis
from bot.variables import _get
from bot.utils.cooldown import TriCooldown

cd_memes = TriCooldown('memes')

class Memes(commands.Cog, name='Miscellaneous'):

    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_message(self, message):
        if _get(message.guild.id, 'toggle', 'memes') and re.search(" do(es)? ?n'?o?t work", message.content.lower()):
            cd = cd_memes(message)
            if cd is None:
                await message.channel.send('You guys are enjoying this too much')
            elif cd is False:
                await message.channel.send('Welcome to BE')

    @commands.command(name='alive')
    async def alive(self, ctx):
        """Check if TRB is alive"""
        await ctx.message.add_reaction(Emojis.thumbs_up)

    @commands.command(name='say')
    @mod_command()
    async def say(self, ctx, *, content:str):
        """Make TRB say something... unoffensive"""
        await ctx.message.delete()
        await ctx.send(content)

def setup(bot):
    bot.add_cog(Memes(bot))