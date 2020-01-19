import os
import discord
import requests

from discord.ext import commands
from dotenv import load_dotenv

class Test(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        print('Test commands ready')

    @commands.command(name='xuid')
    async def xuid(self, ctx, *, content:str):
        username = content
        r = requests.get(f'https://xbl-api.prouser123.me/xuid/{username}/raw')
        await ctx.send(r.text)
            
def setup(bot):
    bot.add_cog(Test(bot))