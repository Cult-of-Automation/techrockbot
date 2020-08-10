from typing import Callable
from discord.ext import commands
from discord.ext.commands import Context

from bot.utils.checks import staff_command_check, mod_command_check

def staff_command() -> Callable:
    async def predicate(ctx: Context) -> bool:
        return staff_command_check(ctx)
    return commands.check(predicate)

def mod_command() -> Callable:
    async def predicate(ctx: Context) -> bool:
        return mod_command_check(ctx)
    return commands.check(predicate)