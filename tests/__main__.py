# Bot for the TechRock Discord
import discord
from discord.ext import commands
from discord.ext.commands import when_mentioned_or

from tests.bot import Bot
from tests.constants import Bot as BotConfig

bot = Bot(
    command_prefix=when_mentioned_or(BotConfig.prefix),
    activity=discord.CustomActivity(name="Welcome to BE"),
    case_insensitive=True
)

@bot.group()
@commands.has_role('Admin')
async def cog(ctx):
    if ctx.invoked_subcommand is None:
        pass

@cog.command(name='load')
async def load(ctx, extension):
    bot.load_extension(f'tests.cogs.{extension}')
    print(f'Cog {extension} loaded')
    await ctx.send(f'{extension} loaded')

@cog.command(name='unload')
async def unload(ctx, extension):
    bot.unload_extension(f'tests.cogs.{extension}')
    print(f'Cog {extension} unloaded')
    await ctx.send(f'{extension} unloaded')

@cog.command(name='reload')
async def reload(ctx, extension):
    bot.unload_extension(f'tests.cogs.{extension}')
    bot.load_extension(f'tests.cogs.{extension}')
    print(f'Cog {extension} reloaded')
    await ctx.send(f'{extension} reloaded')

bot.load_extension("tests.cogs.guilds")
bot.load_extension("tests.cogs.server")

bot.load_extension("tests.cogs.memes")
bot.load_extension("tests.cogs.status")
bot.load_extension("tests.cogs.mcbecl")

bot.run(BotConfig.test_token)