import logging
from discord.ext import commands
from bot.variables import GuildConfig

log = logging.getLogger('bot')

class Bot(commands.Bot):

    def add_cog(self, cog: commands.Cog) -> None:
        """Adds a "cog" to the bot and logs the operation."""
        super().add_cog(cog)
        log.info(f"Cog loaded: {cog.qualified_name}")

    async def close(self) -> None:
        await super().close()
        GuildConfig.save_all()