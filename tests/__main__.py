# Bot for the TechRock Discord
import discord
from discord.ext import commands
from discord.ext.commands import when_mentioned_or

from tests.constants import Bot as BotConfig

bot = commands.Bot(
    command_prefix=when_mentioned_or(BotConfig.prefix),
    activity=discord.Game(name="DDLC"),
    case_insensitive=True
)

@bot.event
async def on_ready():
    print("Bot online")

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

bot.load_extension("tests.cogs.guilds")
bot.load_extension("tests.cogs.server")

bot.load_extension("tests.cogs.memes")
bot.load_extension("tests.cogs.status")

bot.run(BotConfig.test_token)