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
    print("TechRockBot online")

bot.load_extension("bot.cogs.server")

bot.load_extension("bot.cogs.memes")
bot.load_extension("bot.cogs.status")

bot.run(BotConfig.token)