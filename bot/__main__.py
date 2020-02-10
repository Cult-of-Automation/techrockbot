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

bot.run(BotConfig.token)