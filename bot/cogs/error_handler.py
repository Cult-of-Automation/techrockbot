import logging

from discord.ext.commands import (
    BadArgument,
    BotMissingPermissions,
    CheckFailure,
    CommandError,
    CommandInvokeError,
    CommandNotFound,
    CommandOnCooldown,
    DisabledCommand,
    MissingPermissions,
    NoPrivateMessage,
    UserInputError,
)
from discord.ext.commands import Cog, Context

log = logging.getLogger(__name__)

class ErrorHandler(Cog):

    def __init__(self, bot):
        self.bot = bot

    @Cog.listener()
    async def on_command_error(self, ctx: Context, e: CommandError) -> None:

        command = ctx.command
        parent = None

        if command is not None:
            parent = command.parent

        # Retrieve the help command for the invoked command.
        if parent and command:
            help_command = (self.bot.get_command("help"), parent.name, command.name)
        elif command:
            help_command = (self.bot.get_command("help"), command.name)
        else:
            help_command = (self.bot.get_command("help"),)

        if hasattr(e, "handled"):
            log.trace(f"Command {command} had its error already handled locally; ignoring.")
            return

        # Try to look for a tag with the command's name if the command isn't found.
        if isinstance(e, CommandNotFound) and not hasattr(ctx, "invoked_from_error_handler"):
            await ctx.message.add_reaction('\U0001F914')

        elif isinstance(e, BadArgument):
            await ctx.send(f"Bad argument: {e}\n")
            await ctx.invoke(*help_command)

        elif isinstance(e, UserInputError):
            await ctx.send("Something about your input seems off. Check the arguments:")
            await ctx.invoke(*help_command)
            log.debug(
                f"Command {command} invoked by {ctx.message.author} with error "
                f"{e.__class__.__name__}: {e}"
            )

        elif isinstance(e, NoPrivateMessage):
            await ctx.send("Sorry, this command can't be used in a private message!")

        elif isinstance(e, BotMissingPermissions):
            await ctx.send(f"Sorry, it looks like I don't have the permissions I need to do that.")
            log.warning(
                f"The bot is missing permissions to execute command {command}: {e.missing_perms}"
            )

        elif isinstance(e, MissingPermissions):
            log.debug(
                f"{ctx.message.author} is missing permissions to invoke command {command}: "
                f"{e.missing_perms}"
            )

        elif isinstance(e, (CheckFailure, CommandOnCooldown, DisabledCommand)):
            log.debug(
                f"Command {command} invoked by {ctx.message.author} with error "
                f"{e.__class__.__name__}: {e}"
            )

        elif isinstance(e, CommandInvokeError):
            await self.handle_unexpected_error(ctx, e.original)

        else:
            await self.handle_unexpected_error(ctx, e)

    @staticmethod
    async def handle_unexpected_error(ctx: Context, e: CommandError) -> None:
        """Generic handler for errors without an explicit handler."""
        await ctx.send(
            f"Sorry, an unexpected error occurred. Please let us know!\n\n"
            f"```{e.__class__.__name__}: {e}```"
        )
        log.error(
            f"Error executing command invoked by {ctx.message.author}: {ctx.message.content}"
        )
        raise e


def setup(bot) -> None:
    bot.add_cog(ErrorHandler(bot))