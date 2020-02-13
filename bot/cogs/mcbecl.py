import logging
import aiohttp
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

log = logging.getLogger(__name__)

async def fetch(url):
    async with aiohttp.request('GET', url) as resp:
        assert resp.status == 200
        return await resp.text()

async def get_changelogs():

    base_url = 'https://feedback.minecraft.net'
    checklist = [
        {
            '_branch': 'release',
            '_suburl': '/hc/en-us/sections/360001186971',
            'keyword': 'Bedrock',
            'trimnum': [12, -10]
        },
        {
            '_branch': 'beta',
            '_suburl': '/hc/en-us/sections/360001185332',
            'keyword': 'Android',
            'trimnum': [17, -31]
        }
    ]

    changelogs = {}
    for branch in checklist:

        # Get list of changelogs from site
        furl = base_url + branch['_suburl']
        tree = html.fromstring(await fetch(furl))
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
        text_trimmed = text[branch['trimnum'][0]:branch['trimnum'][1]]
        suburl_trimmed = suburl[0:31]
        branch_dict[branch_name]['version'] = text_trimmed
        branch_dict[branch_name]['link'] = base_url + suburl_trimmed
        changelogs.update(branch_dict)

    return changelogs

async def get_new_updates(log_msg='Not Stated'):

    log.info(f'Checking for new updates... {log_msg}')
    changelogs = await get_changelogs()

    # Open cache and update if changed
    with open('mcbecl.pickle', 'r+b') as f:
        cache = pickle.load(f)
        # Cache is up to date
        if changelogs==cache:
            return
        f.seek(0)
        pickle.dump(changelogs, f)

    updates = {}
    for branch in changelogs:
        if changelogs[branch] != cache[branch]:
            update = 'Minecraft Bedrock '
            update += branch.capitalize()
            update += ' '
            update += changelogs[branch]['version']
            update += ' Changelog:\n'
            update += changelogs[branch]['link']
            updates.update({branch: update})

    return updates

class Mcbecl(commands.Cog, name='MCBE Changelog'):

    def __init__(self, bot):
        self.bot = bot
        self.dailyups.start()

    def cog_unload():
        self.dailyups.cancel()
        self.bihourly.cancel()

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
                channel.send(payload)

    @commands.Cog.listener()
    async def on_ready(self):
        # Check for updates on when bot ready
        updates = await get_new_updates('Initialization')
        if updates:
            await self.post_updates(updates)

    @commands.command(name='latestmcbe')
    async def latestmcbe(self, ctx):
        """Link the latest release changelog for MCBE"""
        with open('mcbecl.pickle', 'rb') as f:
            cache = pickle.load(f)
        release_version = cache['release']['version']
        release_link = cache['release']['link']
        await ctx.send(f'Minecraft Bedrock {release_version} Changelog:\n{release_link}')

    @commands.command(name='latestbeta')
    async def latestbeta(self, ctx):
        """Link the latest beta changelog for MCBE"""
        with open('mcbecl.pickle', 'rb') as f:
            cache = pickle.load(f)
        beta_version = cache['beta']['version']
        beta_link = cache['beta']['link']
        await ctx.send(f'Minecraft Bedrock BETA {beta_version} Changelog:\n{beta_link}')

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

        with GuildConfig(ctx.guild.id) as guildconfig:

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
                guildconfig['updates'][_branch] = channel.id

        await ctx.send(f'Channel for {branch} updates set to {channel.mention}')

    @_updates.command(name='off')
    async def _updates_off(self, ctx, branch: str='all'):
        """Disable MCBE updates for a channel"""

        branch = branch.lower()

        with GuildConfig(ctx.guild.id) as guildconfig:

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
        log_msg = 'Check ' + self.bihourly.current_loop
        updates = await get_new_updates(log_msg)
        if updates:
            await self.post_updates(updates)

def setup(bot):
    bot.add_cog(Mcbecl(bot))