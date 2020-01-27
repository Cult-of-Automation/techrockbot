import discord
import io
import json

from discord.ext import commands
from py_mcpe_stats import Query
from bot.utils.ftp import Ftp
from bot.constants import Status

class Server(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        print('Server tools ready')

    # CMP .mcstructure file upload
    @commands.Cog.listener()
    async def on_message(self, message):

        if not message.channel.id in [
            661730461206183937,
            661372317212868620
        ]:
            return
        
        for attachment in message.attachments:
            if not attachment.filename.endswith('.mcstructure'):
                return
            
            name = attachment.filename
            size = attachment.size
            content = io.BytesIO()
            
            # Retrieve attachment
            await attachment.save(content)
            
            # "Loading" reaction
            await message.add_reaction('\U0001F504')
            
            # Upload .mcstructure file
            result = await Ftp.cmp_write(self, name, size, content, '/behavior_packs/vanilla/structures')
            content.close()
            
            # Replace reaction with results
            await message.clear_reactions()
            if result==2: # Duplicate
                await message.add_reaction('\U000026A0')
            elif result==1: # Success
                await message.add_reaction('\U00002705')
            elif result==0: # Failed
                await message.add_reaction('\U0000274C')

    # Add users to role and auto add
    # to respected server whitelist
    @commands.has_role(['Admin', 'Moderator'])
    @commands.group(name='add_role')
    async def add_role(self, ctx):
        pass
    
    @add_role.command(name='smp')
    async def smp(self, ctx, user):
        pass

    @add_role.command(name='cmp')
    async def cmp(self, ctx, user):
        pass

    # List users in whitelist
    @commands.has_role('Admin')
    @commands.command(name='userlist')
    async def userlist(self, ctx):
        
        perms_raw = await Ftp.cmp_read(self, '/permissions.json')
        perms = json.loads(perms_raw)
        
        names = []
        for i in range(len(perms)):
            names.append(perms[i]['name'])

        users = '\n'.join(names)
        
        await ctx.send(f'```{users}```')
    
    # Minecraft server ping
    @commands.command(name='status')
    async def status(self, ctx, ip_port=Status.default):
        
        if ip_port=="all":
            servers = Status.aliases.values()
        else:
            servers = ip_port.split()
        
        # Replace alias from config if parsed
        servers = [Status.aliases.get(i,i) for i in servers]
        
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
    bot.add_cog(Server(bot))