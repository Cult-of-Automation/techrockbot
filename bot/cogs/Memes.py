import os
import discord

from discord.ext import commands
from dotenv import load_dotenv

class Memes(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        print('Memes are loaded')

    @commands.Cog.listener()
    async def on_message(self, message):
        if ' doesnt work' in message.content.lower():
            await message.channel.send('Welcome to BE')

    @commands.command(name='say')
    @commands.has_role('Admin')
    async def say(self, ctx, *, content:str):
        await ctx.message.delete()
        await ctx.send(content)
            
def setup(bot):
    bot.add_cog(Memes(bot))