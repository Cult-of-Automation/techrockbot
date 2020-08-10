import logging
import pickle

from lxml import html
from typing import Optional
from datetime import datetime, timedelta
from discord import Embed, TextChannel
from discord.ext import tasks, commands
from discord.utils import sleep_until

from bot.constants import Colours, Icons
from bot.variables import GuildConfig, _get
from bot.decorators import staff_command
from bot.utils.requests import fetch_text

log = logging.getLogger(__name__)

async def get_changelogs():
    """Get latest changelogs from feedback site"""
    base_url = 'https://feedback.minecraft.net'
    checklist = [
        {
            '_branch': 'release',
            '_suburl': '/hc/en-us/sections/360001186971',
            'keyword': 'Bedrock',
            'trimnum': (12, -10)
        },
        {
            '_branch': 'beta',
            '_suburl': '/hc/en-us/sections/360001185332',
            'keyword': 'Android',
            'trimnum': (17, -31)
        }
    ]

    changelogs = {}
    for branch in checklist:

        # Get list of changelogs from site
        furl = base_url + branch['_suburl']
        tree = html.fromstring(await fetch_text(furl))
        vers = tree.find_class('article-list-link')

        # Check if list successfully obtained
        if not vers:
            log.warning('Failed to obtain changelogs webpage')
            continue

        # Get latest changelog
        for link in vers:
            text = link.text_content()
            if branch['keyword'] in text:
                suburl = link.get('href')
                break

        # Initialize branch dictionary
        branch_name = branch['_branch']
        branch_dict = {branch_name: {}}

        # Trim and add values
        trim_in, trim_out = branch['trimnum']
        text_trimmed = text[trim_in:trim_out]
        suburl_trimmed = suburl[0:31]
        branch_dict[branch_name]['version'] = text_trimmed
        branch_dict[branch_name]['link'] = base_url + suburl_trimmed
        changelogs.update(branch_dict)

    return changelogs

class Mcbecl(commands.Cog, name='MCBE Changelog'):

    def __init__(self, bot):
        self.bot = bot
        with open('.pickle', 'rb') as f:
            self.cache = pickle.load(f)['mcbecl']
        # self.dailyups.start()

    def cog_unload():
        # self.dailyups.cancel()
        # self.bihourly.cancel()
        pass

    @commands.Cog.listener()
    async def on_ready(self):
        # Check for updates on when bot ready
        # updates = await self.get_new_updates('Initialization')
        # if updates:
        #     await self.post_updates(updates)
        pass

    @tasks.loop(hours=24)
    async def dailyups(self):
        log.info('Feedback site daily check started')
        self.bihourly.start()

    @dailyups.before_loop
    async def before_daily(self):
        # Gets next T15:00Z
        tea_today = datetime.utcnow().replace(hour=15, minute=0, second=0, microsecond=0)
        tea_next = tea_today if datetime.utcnow().hour < 15 else tea_today + timedelta(1)
        # Sync daily check to T15:00Z
        log.info(f'Bihourly loop will begin at {tea_next}')
        await sleep_until(tea_next)

    @tasks.loop(minutes=30, count=10)
    async def bihourly(self):
        log_msg = 'Check ' + str(self.bihourly.current_loop)
        updates = await self.get_new_updates(log_msg)
        if updates:
            await self.post_updates(updates)

    async def get_new_updates(self, log_msg='Not Stated'):
    
        log.info(f'Checking for new updates... {log_msg}')
        changelogs = await get_changelogs()

        # Cache is up to date
        if self.cache==changelogs:
            return

        # Compile post payloads for changelog branch if new
        updates = {}
        for branch in changelogs:
            if changelogs[branch] != self.cache[branch]:
                update = 'Minecraft Bedrock '
                update += branch.capitalize()
                update += ' '
                update += changelogs[branch]['version']
                update += ' Changelog:\n'
                update += changelogs[branch]['link']
                updates.update({branch: update})

        # Update pickle
        with open('.pickle', 'r+b') as f:
            _pickle = pickle.load(f)
            _pickle.update({'mcbecl': changelogs})
            f.seek(0)
            pickle.dump(_pickle, f)
            f.truncate()

        # Update cache
        self.cache = changelogs
    
        return updates

    async def post_updates(self, updates):

        for branch in updates:

            log.info(f'Posting new {branch} changelogs...')
            payload = updates[branch]

            # Get update channel id for update branch from all guild configs
            channels = [_get(guild.id, 'updates', branch) for guild in self.bot.guilds]

            # Post to all channels
            for channel_id in channels:
                if channel_id is None:
                    continue
                channel = self.bot.get_channel(channel_id)
                print(payload)

    @commands.command(name='mcbecl_check')
    @commands.is_owner()
    async def mcbecl_check(self, ctx):
        updates = await self.get_new_updates('Manual')
        if updates:
            await self.post_updates(updates)

    @commands.command(name='latest')
    async def latest(self, ctx, branch='release'):
        """Get link for the latest changelog"""
        vers = self.cache[branch]['version']
        link = self.cache[branch]['link']
        await ctx.send(f'Minecraft Bedrock {vers} Changelog:\n{link}')

    @commands.group(name='updates')
    @staff_command()
    async def _updates(self, ctx):
        """List the channels where MCBE updates will be posted"""

        if ctx.invoked_subcommand is None:

            # Get guild's update channel dictionary
            channels = _get(ctx.guild.id, 'updates')

            title = f'{ctx.guild.name} Update Channels'
            guild_updates = Embed(colour=Colours.techrock)
            guild_updates.set_author(name=title, icon_url=Icons.techrock)
            # Loop though update channel dictionary
            for branch in channels:
                channel_id = channels[branch]
                if channel_id is None:
                    guild_updates.add_field(name=branch, value='Not set')
                    continue
                channel = self.bot.get_channel(channel_id)
                guild_updates.add_field(name=branch, value=channel.mention)
            await ctx.send(embed=guild_updates)

    @_updates.command(name='set')
    async def _updates_set(self, ctx, channel: Optional[TextChannel]=None, branch: str='all'):
        """Enable MCBE updates for a channel"""

        # Defaults to current channel
        if channel is None:
            channel = ctx.channel

        branch = branch.lower()
        guild_config = GuildConfig.get_config(ctx.guild.id)

        # Get guild's update channel dictionary
        update_channels = guild_config.updates
        all_branches = list(update_channels.keys())

        # Default to all update branches
        # Check [branch] argument
        if branch=='all':
            setlist = all_branches
        elif branch in all_branches:
            setlist = [branch]
        else:
            valid = ', '.join(all_branches)
            await ctx.send(f'`{branch}` is not a valid update branch: {valid}')

        for _branch in setlist:
            guildconfig.updates[_branch] = channel.id

        await ctx.send(f'Channel for {branch} updates set to {channel.mention}')

    @_updates.command(name='off')
    async def _updates_off(self, ctx, branch: str='all'):
        """Disable MCBE updates for a channel"""

        branch = branch.lower()

        with GuildConfigEdit(ctx.guild.id) as guildconfig:

            # Get guild's update channel dictionary
            update_channels = guildconfig['updates']
            all_branches = list(update_channels.keys())

            # Default to all update branches
            # Check [branch] argument
            if branch=='all':
                setlist = all_branches
            elif branch in all_branches:
                setlist = [branch]
            else:
                valid = ', '.join(all_branches)
                await ctx.send(f'`{branch}` is not a valid update branch: {valid}')

            for _branch in setlist:
                guildconfig['updates'][_branch] = None

        await ctx.send(f'Disabled receiving {branch} updates')

def setup(bot):
    bot.add_cog(Mcbecl(bot))