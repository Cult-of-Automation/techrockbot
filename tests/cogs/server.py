import discord
import io
import json
import logging

from discord.ext import commands
from tests.utils.ftp import Ftp
from tests.utils.xbox import Xblapi
from tests.constants import Server as ServerConfig
from tests.constants import STAFF_ROLES
from tests.decorators import with_role

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

        if not message.channel.id=='661372317212868620':
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

    # Add user to respected server whitelist
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
            for item in perms:
                names.append(item['name'])

            users = '\n'.join(names)

            await ctx.send(f'```{users}```')

        except KeyError:

            await ctx.send(f'`{server}` is an unconfigured alias')
            log.error(f'Config key `{server}` for ftp could not be found.')
            raise

def setup(bot):
    bot.add_cog(Server(bot))