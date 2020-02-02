# Bot for the TechRock Discord
import discord
from discord.ext import commands
from discord.ext.commands import when_mentioned_or

from bot.bot import Bot
from bot.constants import Bot as BotConfig

bot = Bot(
    command_prefix=when_mentioned_or(BotConfig.prefix),
    activity=discord.CustomActivity(name='Welcome to BE'),
    case_insensitive=True
)

bot.load_extension("bot.cogs.guilds")
bot.load_extension("bot.cogs.server")

bot.load_extension("bot.cogs.memes")
bot.load_extension("bot.cogs.status")
bot.load_extension("bot.cogs.mcbecl")

bot.run(BotConfig.token)