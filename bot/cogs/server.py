import discord
import io
import json
import logging

from discord.ext import commands
from bot.utils.ftp import Ftp
from bot.utils.xbox import getxuid
from bot.variables import _get
from bot.constants import Emojis, Server as ServerConfig
from bot.decorators import staff_command

log = logging.getLogger(__name__)

emote = [
    Emojis.okay,
    Emojis.error,
    Emojis.warning,
    Emojis.loading
]

errors = [
    '           Okay',
    'Transfer Failed',
    ' Already Exists'
]

class Server(commands.Cog):
    """Currently only for TechRock Discord"""

    def __init__(self, bot):
        self.bot = bot

    # Temporary TechRock-only check
    async def cog_check(self, ctx):
        return ctx.guild.id==403047405877985281

    # CMP .mcstructure file upload
    @commands.Cog.listener()
    async def on_message(self, message):

        if message.channel.id != 661730461206183937 or not message.attachments:
            return

        # "Loading" reaction
        await message.add_reaction(emote[3])

        filelog = []
        errno = 0
        for attachment in message.attachments:

            file_name = attachment.filename
            file_size = attachment.size
            path = '/behavior_packs/vanilla/structures'

            if not attachment.filename.endswith('.mcstructure'):
                continue

            with io.BytesIO() as file_in:
                # Retrieve attachment
                await attachment.save(file_in)
                # Upload .mcstructure file
                result = await Ftp._write(self, ServerConfig.ftp['cmp'], file_name, file_size, file_in, path)

            filelog.append(f'{errors[result]} | {file_name}')
            if errno < result:
                errno = result

        # Replace reaction with results
        await message.clear_reactions()
        await message.add_reaction(emote[errno])

        # Send errors on multiple files        
        if len(message.attachments) > 1 and errno:
            error_list = '\n'.join(filelog)
            message.channel.send(f'```{error_list}```')

    # Add user to respected server whitelist
    @commands.command(name='add_user')
    @staff_command()
    async def add_user(self, ctx, server, user):

        try:

            userlist_path = ServerConfig.ftp[server]['userlist']
            
            # "Loading" reaction
            await ctx.message.add_reaction(emote[3])

            # Build dict for JSON entry
            entry = {}
            if userlist_path=='/whitelist.json':
                entry['ignoresPlayerLimit'] = False
            elif userlist_path=='/permissions.json':
                entry['permission'] = 'operator'
            else:
                raise
            entry['name'] = user
            entry['xuid'] = await getxuid(user)
            
            # Fetch permissions.json as list of dicts
            perms_raw = await Ftp._read(self, ServerConfig.ftp[server], userlist_path)
            perms = json.loads(perms_raw)
            
            perms.append(entry)
            
            # Dump list to JSON and upload
            with io.BytesIO() as output:
                size = output.write(json.dumps(perms, indent=4).encode('utf-8'))
                result = await Ftp._write(self, ServerConfig.ftp[server], userlist_path, size, output, '/', True)

            # Replace reaction with results
            await ctx.message.clear_reactions()
            await ctx.message.add_reaction(emote[result])

        except KeyError:

            await ctx.send(f'`{server}` is an unconfigured server alias')
            log.error(f'Config key `{server}` for ftp could not be found.')
            raise

    # List users in whitelist
    @commands.command(name='userlist')
    @staff_command()
    async def userlist(self, ctx, server='cmp'):

        try:
            userlist_path = ServerConfig.ftp[server]['userlist']

            perms_raw = await Ftp._read(self, ServerConfig.ftp[server], userlist_path)
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