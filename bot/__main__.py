# Bot for the TechRock Discord
import discord
import os
from discord.ext import commands
from dotenv import load_dotenv

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')

bot = commands.Bot(
    command_prefix='trb ',
    activity=discord.Game(name="Welcome to BE Simulator"),
    case_insensitive=True
)

@bot.event
async def on_ready():
    print("Bot online")

@bot.command(name='alive?')
async def alive(ctx):
    await ctx.message.add_reaction('\U0001F44D')

@bot.group()
@commands.has_role('Admin')
async def cog(ctx):
    if ctx.invoked_subcommand is None:
        await ctx.send('Invalid git command passed...')

@cog.command(name='load')
async def load(ctx, extension):
    bot.load_extension(f'cogs.{extension}')
    print(f'{extension} loaded')
    await ctx.send(f'{extension} loaded')

@cog.command(name='unload')
async def unload(ctx, extension):
    bot.unload_extension(f'cogs.{extension}')
    print(f'{extension} unloaded')
    await ctx.send(f'{extension} unloaded')

@cog.command(name='reload')
async def reload(ctx, extension):
    bot.unload_extension(f'cogs.{extension}')
    bot.load_extension(f'cogs.{extension}')
    print(f'{extension} reloaded')
    await ctx.send(f'{extension} reloaded')

bot.load_extension(f'cogs.Memes')
bot.load_extension(f'cogs.Server')

bot.run(TOKEN)