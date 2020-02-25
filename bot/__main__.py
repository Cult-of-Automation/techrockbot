# Bot for the TechRock Discord
import discord
from discord.ext import commands

from bot.bot import Bot
from bot.constants import Bot as BotConfig
from bot.variables import _prefix

bot = Bot(
    command_prefix=_prefix,
    activity=discord.CustomActivity(name='Welcome to BE'),
    case_insensitive=True
)

@bot.group()
@commands.is_owner()
async def cog(ctx):
    if ctx.invoked_subcommand is None:
        pass

@cog.command(name='load')
async def load(ctx, extension):
    bot.load_extension(f'bot.cogs.{extension}')
    print(f'Cog {extension} loaded')
    await ctx.send(f'Cog {extension} loaded')

@cog.command(name='unload')
async def unload(ctx, extension):
    bot.unload_extension(f'bot.cogs.{extension}')
    print(f'Cog {extension} unloaded')
    await ctx.send(f'Cog {extension} unloaded')

@cog.command(name='reload')
async def reload(ctx, extension):
    bot.unload_extension(f'bot.cogs.{extension}')
    bot.load_extension(f'bot.cogs.{extension}')
    print(f'Cog {extension} reloaded')
    await ctx.send(f'Cog {extension} reloaded')

# Commands, bot function
bot.load_extension('bot.cogs.error_handler')
bot.load_extension('bot.cogs.help')
bot.load_extension('bot.cogs.guilds')

# TechRock Cogs
bot.load_extension('bot.cogs.server')
bot.load_extension('bot.cogs.democracy')

# Feature cogs
bot.load_extension('bot.cogs.memes')
bot.load_extension('bot.cogs.status')
bot.load_extension('bot.cogs.mcbecl')
bot.load_extension('bot.cogs.embeder')

bot.run(BotConfig.token)