# Bot for the TechRock Discord
import discord
from discord.ext import commands
from discord.ext.commands import when_mentioned_or

from bot.constants import Bot as BotConfig

bot = commands.Bot(
    command_prefix=when_mentioned_or(BotConfig.prefix),
    activity=discord.Game(name="Welcome to BE Simulator"),
    case_insensitive=True
)

@bot.event
async def on_ready():
    print("Bot online")

@bot.command(name='alive')
async def alive(ctx):
    await ctx.message.add_reaction('\U0001F44D')

@bot.group()
@commands.has_role('Admin')
async def cog(ctx):
    if ctx.invoked_subcommand is None:
        pass

@cog.command(name='load')
async def load(ctx, extension):
    bot.load_extension(f'bot.cogs.{extension}')
    print(f'{extension} loaded')
    await ctx.send(f'{extension} loaded')

@cog.command(name='unload')
async def unload(ctx, extension):
    bot.unload_extension(f'bot.cogs.{extension}')
    print(f'{extension} unloaded')
    await ctx.send(f'{extension} unloaded')

@cog.command(name='reload')
async def reload(ctx, extension):
    bot.unload_extension(f'bot.cogs.{extension}')
    bot.load_extension(f'bot.cogs.{extension}')
    print(f'{extension} reloaded')
    await ctx.send(f'{extension} reloaded')

bot.load_extension("bot.cogs.Memes")
bot.load_extension("bot.cogs.Server")

bot.run(BotConfig.token)