from discord import Colour, Embed, Member
from discord.errors import NotFound
from discord.ext import commands
from discord.ext.commands import CheckFailure, Cog, Context

class InChannelCheckFailure(CheckFailure):
    def __init__(self, *channels: int):
        self.channels = channels
        pass

def in_channel(*channels: int):
    def predicate(ctx: Context) -> bool:
        if ctx.channel.id in channels:
            return True
        raise InChannelCheckFailure(*channels)
    return commands.check(predicate)

def with_role(*role_ids: int) -> Callable:
    async def predicate(ctx: Context) -> bool:
        return with_role_check(ctx, *role_ids)
    return commands.check(predicate)

