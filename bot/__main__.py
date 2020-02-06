# Bot for the TechRock Discord
import discord

from bot.bot import Bot
from bot.constants import Bot as BotConfig
from bot.variables import _prefix

bot = Bot(
    command_prefix=_prefix,
    activity=discord.CustomActivity(name='Welcome to BE'),
    case_insensitive=True
)

# Commands, bot function
bot.load_extension('tests.cogs.error_handler')
bot.load_extension('tests.cogs.help')
bot.load_extension('tests.cogs.guilds')
bot.load_extension('tests.cogs.server')

# Feature cogs
bot.load_extension('tests.cogs.memes')
bot.load_extension('tests.cogs.status')
bot.load_extension('tests.cogs.mcbecl')

bot.run(BotConfig.token)