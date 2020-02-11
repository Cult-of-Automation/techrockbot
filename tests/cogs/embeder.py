from discord import Embed, Message, TextChannel
from discord.ext import commands
from tests.decorators import staff_command
from tests.constants import Colours, Icons

class Embeder(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    @commands.group(name='embed')
    @staff_command()
    async def _embed(self, ctx):
        """Create/edit embeds"""
        if ctx.invoked_subcommand is None:
            _embed_help = (self.bot.get_command('help'), ctx.command.name)
            await ctx.invoke(*_embed_help)

    @_embed.command(name='create')
    async def _embed_create(self, ctx, title: str, channel: TextChannel=None):
        """
        Create new embed
        Defaults to current channel if not provided
        """
        await ctx.message.delete()
        if channel is None:
            channel = ctx.channel
        embed = Embed(colour=Colours.techrock)
        embed.set_author(name=title, icon_url=Icons.techrock)
        await channel.send(embed=embed)

    @_embed.command(name='add')
    async def _embed_add(self, ctx, message: Message, name: str, value: str):
        """Add a field to an embed"""
        await ctx.message.delete()
        embed = message.embeds[0]
        embed.add_field(name=name, value=value, inline=False)
        await message.edit(embed=embed)

    @_embed.command(name='remove')
    async def _embed_remove(self, ctx, message: Message, index: int=None):
        """
        Remove a field from an embed
        Defaults to bottom-most field if index is not provided
        """
        await ctx.message.delete()
        embed = message.embeds[0]
        if index is None:
            index = len(embed.fields)
        index -= 1
        embed.remove_field(index)
        await message.edit(embed=embed)

def setup(bot):
    bot.add_cog(Embeder(bot))