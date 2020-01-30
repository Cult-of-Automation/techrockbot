from typing import Callable, Container, Union

from discord import Colour, Embed, Member
from discord.errors import NotFound
from discord.ext import commands
from discord.ext.commands import CheckFailure, Cog, Context

from tests.utils.checks import with_role_check, without_role_check

class InChannelCheckFailure(CheckFailure):
    def __init__(self, *channels: int):
        self.channels = channels
        channels_str = ', '.join(f"<#{c_id}>" for c_id in channels)
        
        super().__init__(f"Sorry, but you may only use this command within {channels_str}.")

def in_channel(*channels: int) -> Callable:
    def predicate(ctx: Context) -> bool:
        if ctx.channel.id in channels:
            return True
        raise InChannelCheckFailure(*channels)
    return commands.check(predicate)

def with_role(*role_ids: int) -> Callable:
    async def predicate(ctx: Context) -> bool:
        return with_role_check(ctx, *role_ids)
    return commands.check(predicate)

def without_role(*role_ids: int) -> Callable:
    """Returns True if the user does not have any of the roles in role_ids."""
    async def predicate(ctx: Context) -> bool:
        return without_role_check(ctx, *role_ids)
    return commands.check(predicate)
