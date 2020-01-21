# Majbot.py
import discord
import os

from discord.ext import commands
from dotenv import load_dotenv

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')

bot = commands.Bot(
    command_prefix='trb ',
    activity=discord.Game(name="Welcome to BE Simulator", emoji="TechRock"),
    case_insensitive=True
)

@bot.event
async def on_ready():
    print("Online")

@bot.command(name='alive?')
async def alive(ctx):
    await ctx.message.add_reaction('\U0001F44D')

@bot.command(name='load')
@commands.has_role('Admin')
async def load(ctx, extension):
    bot.load_extension(f'cogs.{extension}')
    print(f'{extension} loaded')
    await ctx.send(f'{extension} loaded')

@bot.command(name='unload')
@commands.has_role('Admin')
async def unload(ctx, extension):
    bot.unload_extension(f'cogs.{extension}')
    print(f'{extension} unloaded')
    await ctx.send(f'{extension} unloaded')

@bot.command(name='reload')
@commands.has_role('Admin')
async def reload(ctx, extension):
    bot.unload_extension(f'cogs.{extension}')
    bot.load_extension(f'cogs.{extension}')
    print(f'{extension} reloaded')
    await ctx.send(f'{extension} reloaded')

bot.load_extension(f'cogs.Memes')
bot.load_extension(f'cogs.Server')

bot.run(TOKEN)