import discord
import io
import json
import logging

from discord.ext import commands
from py_mcpe_stats import Query
from bot.utils.ftp import Ftp
from bot.utils.xbox import Xblapi
from bot.constants import Server as ServerConfig
from bot.constants import STAFF_ROLES
from bot.decorators import with_role

log = logging.getLogger(__name__)

emote = ['\U0000274C', '\U00002705', '\U000026A0', '\U0001F504']

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
            await message.add_reaction(emote[3])
            
            # Upload .mcstructure file
            result = await Ftp._write(self, ServerConfig.ftp['cmp'], name, size, content, '/behavior_packs/vanilla/structures')
            content.close()
            
            # Replace reaction with results
            await message.clear_reactions()
            await message.add_reaction(emote[result])

    # Add users to role and auto add
    # to respected server whitelist
    @with_role(*STAFF_ROLES)
    @commands.command(name='add_user')
    async def add_user(self, ctx, server, user):

        try:

            userlist_path = ServerConfig.ftp[server]['userlist']

            # Build dict for JSON entry
            entry = {}
            if userlist_path=='/whitelist.json':
                entry['ignoresPlayerLimit'] = False
            elif userlist_path=='/permissions.json':
                entry['permission'] = 'operator'
            else:
                raise
            entry['name'] = user
            entry['xuid'] = await Xblapi.xuid(user)
            
            # Fetch permissions.json as list of dicts
            perms_raw = await Ftp._read(self, ServerConfig.ftp[server], userlist_path)
            perms = json.loads(perms_raw)
            
            # "Loading" reaction
            await ctx.message.add_reaction(emote[3])
            
            perms.append(entry)
            
            # Dump list to JSON and upload
            output = io.BytesIO()
            size = output.write(json.dumps(perms, indent=4).encode('utf-8'))
            result = await Ftp._write(self, ServerConfig.ftp[server], userlist_path, size, output, '/', True)
            output.close()

            # Replace reaction with results
            await ctx.message.clear_reactions()
            await ctx.message.add_reaction(emote[result])

        except KeyError:

            await ctx.send(f'`{server}` is an unconfigured alias')
            log.error(f'Config key `{server}` for ftp could not be found.')
            raise

    # List users in whitelist
    @with_role(*STAFF_ROLES)
    @commands.command(name='userlist')
    async def userlist(self, ctx, server='cmp'):

        try:

            path = ServerConfig.ftp[server]['userlist']

            perms_raw = await Ftp._read(self, ServerConfig.ftp[server], path)
            perms = json.loads(perms_raw)

            names = []
            for item in range(len(perms)):
                names.append(perms[item]['name'])

            users = '\n'.join(names)

            await ctx.send(f'```{users}```')

        except KeyError:

            await ctx.send(f'`{server}` is an unconfigured alias')
            log.error(f'Config key `{server}` for ftp could not be found.')
            raise

    # Minecraft server ping
    @commands.command(name='status')
    async def status(self, ctx, ip_port=ServerConfig.status_default):
        
        if ip_port=="all":
            servers = ServerConfig.aliases.values()
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
    bot.add_cog(Server(bot))