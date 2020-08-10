import discord

from discord.ext import commands
from py_mcpe_stats import Query

from bot.variables import GuildConfig, _get
from bot.decorators import staff_command

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
        Set/show the default server/server alias for the status command
        [e.g. 0.0.0.0:19132] To ping all aliases set to [all]
        """
        alias_value = guildconfig.status['aliases'].get(ip_port, None)
        guild_config = GuildConfig.get_config(ctx.guild.id)

        # Set configuration if argument is given
        if ip_port is None:
            ip_port = guild_config.status['default']
        else:
            guild_config.status['default'] = ip_port

        if ip_port=='all':
            response = (
                '`status` command will ping all aliases by default\n'
                'Run `status_alias` command to get a list of them'
            )
        elif alias_value is not None:
            response = f'`status` command will ping {ip_port} ({alias_value}) by default'
        else:
            response = f'`status` command will ping {ip_port} by default'
        await ctx.send(response)

    @commands.group(name='status_alias')
    async def status_alias(self, ctx):
        """List server aliases for status command"""

        if ctx.invoked_subcommand is None:

            aliases = _get(ctx.guild.id, 'status', 'aliases')
            if aliases is None:
                await ctx.send(f'No server aliases have been set for {ctx.guild.name}')
                return
            title = f'{ctx.guild.name} Status Aliases'
            alias_list = Embed(colour=Colours.techrock)
            alias_list.set_author(name=title, icon_url=Icons.techrock)
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
        guild_config = GuildConfig.get_config(ctx.guild.id)
        try:
            guild_config.status['aliases'].update({alias:ip_port})
        except AttributeError:
            guild_config.status['aliases'] = {alias:ip_port}
        await ctx.send(f'Added `{alias}` as a status alias')

    @status_alias.command(name = 'remove')
    @staff_command()
    async def status_alias_remove(self, ctx, alias):
        """Remove a server alias for the status command"""
        guild_config = GuildConfig.get_config(ctx.guild.id)
        try:
            del guild_config.status['aliases'][alias]
        except KeyError:
            response = f'`{alias}` is not a status alias'
        else:
            response = f'Removed `{alias}` as a status alias'
        finally:
            await ctx.send(response)

def setup(bot):
    bot.add_cog(Status(bot))