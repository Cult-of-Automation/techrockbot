# Bot for the TechRock Discord
import discord
from discord.ext import commands

from tests.bot import Bot
from tests.constants import Bot as BotConfig
from tests.variables import _prefix

bot = Bot(
    command_prefix=_prefix,
    activity=discord.CustomActivity(name='Welcome to BE'),
    case_insensitive=True
)

@bot.group()
@commands.check(commands.is_owner())
async def cog(ctx):
    if ctx.invoked_subcommand is None:
        pass

@cog.command(name='load')
async def load(ctx, extension):
    bot.load_extension(f'tests.cogs.{extension}')
    print(f'Cog {extension} loaded')
    await ctx.send(f'Cog {extension} loaded')

@cog.command(name='unload')
async def unload(ctx, extension):
    bot.unload_extension(f'tests.cogs.{extension}')
    print(f'Cog {extension} unloaded')
    await ctx.send(f'Cog {extension} unloaded')

@cog.command(name='reload')
async def reload(ctx, extension):
    bot.unload_extension(f'tests.cogs.{extension}')
    bot.load_extension(f'tests.cogs.{extension}')
    print(f'Cog {extension} reloaded')
    await ctx.send(f'Cog {extension} reloaded')

# Commands, bot function
bot.load_extension('tests.cogs.error_handler')
bot.load_extension('tests.cogs.help')
bot.load_extension('tests.cogs.guilds')

# TechRock Cogs
bot.load_extension('tests.cogs.server')
bot.load_extension('tests.cogs.democracy')

# Feature cogs
bot.load_extension('tests.cogs.memes')
bot.load_extension('tests.cogs.status')
bot.load_extension('tests.cogs.mcbecl')
bot.load_extension('tests.cogs.embeder')

bot.run(BotConfig.test_token)