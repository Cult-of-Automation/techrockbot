import discord

from discord.ext import commands
from py_mcpe_stats import Query

from tests.constants import Status as StatusConfig

class Status(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

  # Minecraft server ping
    @commands.command(name='status')
    async def status(self, ctx, ip_port=StatusConfig.default):
        
        if ip_port=="all":
            servers = StatusConfig.aliases.values()
        else:
            servers = ip_port.split()
        
        # Replace alias from config if parsed
        servers = [ServerConfig.aliases.get(i,i) for i in servers]
        
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

def setup(bot):
    bot.add_cog(Status(bot))