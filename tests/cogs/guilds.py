import discord
import yaml

from discord.ext import commands

class Guilds(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_guild_join(self, message):
        pass

def setup(bot):
    bot.add_cog(Guilds(bot))