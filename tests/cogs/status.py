import discord

from discord.ext import commands
from py_mcpe_stats import Query

from tests.variables import GuildConfig, _get
from tests.decorators import staff_command

class Status(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

  # Minecraft server ping
    @commands.command(name='status')
    async def status(self, ctx, ip_port=None):
        """Ping an MCBE server for info"""
        
        if ip_port is None:
            ip_port = _get(ctx.guild.id, 'status', 'default')
        
        if ip_port=="all":
            status_aliases = _get(ctx.guild.id, 'status', 'aliases')
            if status_aliases==None:
                await ctx.send(f'ctx.guild.name has yet no status defaults,') 
                return
            servers = status_aliases.values()
        else:
            servers = ip_port.split()
        
        # Replace alias from config if parsed
        servers = [_get(ctx.guild.id, 'status', 'aliases').get(i,i) for i in servers]
        
        for server in servers:
            
            # Set portless input to default port, 19132
            try:
                server_ip, server_port = server.split(":")
            except:
                server_ip = server
                server_port = 19132

            # Ping server
            q = Query(server_ip, int(server_port))
            server_data = q.query()

            if server_data is None:
                await ctx.send(f'Failed to get ping data from {server}')

            # Set-up embed
            server_status = discord.Embed(
                title=server_ip,
                description="Offline",
                colour=0xff0000
            )

            if server_data.SUCCESS:
                server_status.colour=0x00ff00
                server_status.description="Online"
                server_status.add_field(
                    name="Name",
                    value=server_data.SERVER_NAME,
                    inline=False
                )
                server_status.add_field(
                    name="Players",
                    value=f'{server_data.NUM_PLAYERS}/{server_data.MAX_PLAYERS}',
                    inline=True
                )
                server_status.add_field(
                    name=server_data.GAME_ID,
                    value=server_data.GAME_VERSION,
                    inline=True
                )
            
            await ctx.send(embed=server_status)

    @commands.command(name='status_default')
    @staff_command()
    async def status_default(self, ctx, ip_port=None):
        """
        Set the default server/server alias for the status command
        [e.g. 0.0.0.0:19132] To ping all aliases set to [all]
        """
        with GuildConfig(ctx.guild.id) as guildconfig:
            if ip_port is None:
                ip_port = guildconfig['status']['default']
            else:
                guildconfig['status']['default'] = ip_port
            try:
                alias_value = guildconfig['status']['aliases'][ip_port]
            except:
                alias_value = None

        if ip_port=='all':
            await ctx.send('`status` command will ping all aliases by default\nRun `status_aliases` to get a list of them')
        elif alias_value is not None:
            await ctx.send(f'`status` command will ping {ip_port} ({alias_value}) by default')
        else:
            await ctx.send(f'`status` command will ping {ip_port} by default')

    @commands.group(name='status_alias')
    async def status_alias(self, ctx):
        """List server aliases for status command"""

        if ctx.invoked_subcommand is None:

            aliases = _get(ctx.guild.id, 'status', 'aliases')
            if aliases is None:
                await ctx.send(f'No server aliases have been set for {ctx.guild.name}')
                return
            alias_list = discord.Embed(title=f'{ctx.guild.name} Status Aliases',colour=0x4b4740)
            for alias in aliases:
                alias_list.add_field(name=alias,value=aliases[alias])
            await ctx.send(embed=alias_list)

    @status_alias.command(name = 'add')
    @staff_command()
    async def status_alias_add(self, ctx, alias, ip_port):
        """
        Add a server alias for the status command
        [e.g. 0.0.0.0:19132]
        """
        with GuildConfig(ctx.guild.id) as guildconfig:
            try:
                guildconfig['status']['aliases'].update({alias:ip_port})
            except:
                guildconfig['status']['aliases'] = {alias:ip_port}
        await ctx.send(f'Added `{alias}` as a status alias')

    @status_alias.command(name = 'remove')
    @staff_command()
    async def status_alias_remove(self, ctx, alias):
        """Remove a server alias for the status command"""
        with GuildConfig(ctx.guild.id) as guildconfig:
            if alias not in guildconfig['status']['aliases']:
                await ctx.send(f'`{alias}` is not a status alias')
                return
            del guildconfig['status']['aliases'][alias]
        await ctx.send(f'Removed `{alias}` as a status alias')

def setup(bot):
    bot.add_cog(Status(bot))