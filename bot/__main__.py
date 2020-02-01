# Bot for the TechRock Discord
import discord
from discord.ext.commands import when_mentioned_or

from bot.bot import Bot
from bot.constants import Bot as BotConfig

bot = Bot(
    command_prefix=when_mentioned_or(BotConfig.prefix),
    activity=discord.CustomActivity(name="Welcome to BE"),
    case_insensitive=True
)

@bot.event
async def on_ready():
    print("TechRockBot online")

bot.load_extension("tests.cogs.guilds")
bot.load_extension("tests.cogs.server")

bot.load_extension("tests.cogs.memes")
bot.load_extension("tests.cogs.status")
bot.load_extension("tests.cogs.mcbecl")

bot.run(BotConfig.token)