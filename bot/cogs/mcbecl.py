import discord
import aiohttp
import logging
import pickle
import io

from discord.ext import tasks, commands
from lxml import html
from typing import Optional
from datetime import datetime, timedelta

from bot.variables import GuildConfig, _get
from bot.decorators import staff_command

log = logging.getLogger(__name__)

async def fetch(url):
    async with aiohttp.request('GET', url) as resp:
        assert resp.status == 200
        return await resp.read()

class Mcbecl(commands.Cog):

    def __init__(self, bot):
        self.bot = bot
        self.daily.start()

    def cog_unload():
        self.daily.cancel()
        self.bihourly.cancel()

    async def check_feedback_site(self, loop_count='Initialization'):

        log.info(f'Checking feedback site... {loop_count}')
        base_url = 'https://feedback.minecraft.net'
        release_url = 'https://feedback.minecraft.net/hc/en-us/sections/360001186971'
        beta_url = 'https://feedback.minecraft.net/hc/en-us/sections/360001185332'

        # Get release changelogs
        with io.BytesIO(await fetch(release_url)) as page:
            release_tree = html.parse(page).getroot()
        release_vers = release_tree.find_class('article-list-link')

        # Get beta changelogs
        with io.BytesIO(await fetch(beta_url)) as page:
            beta_tree = html.parse(page).getroot()
        beta_vers = beta_tree.find_class('article-list-link')

        # Check if lists successfully obtained
        if not len(release_vers) * len(beta_vers):
            log.warning('Failed to obtain changelogs webpage')
            return

        # Get latest Bedrock update
        for link in release_vers:
            release_text = link.text_content()
            if 'Bedrock' in release_text:
                release_sub_url = link.get('href')
                break

        # Get latest Bedrock Beta update
        beta_text = beta_vers[0].text_content()
        beta_sub_url = beta_vers[0].get('href')

        # Initialize dictionaries
        changelogs = {'release': {},'beta': {}}

        changelogs['release']['version'] = release_text[12:-10]
        changelogs['release']['link'] = base_url + release_sub_url
        changelogs['beta']['version'] = beta_text[17:-31]
        changelogs['beta']['link'] = base_url + beta_sub_url

        # Open cache and update if changed
        with open('mcbecl.pickle', 'r+b') as f:
            cache = pickle.load(f)
            # Cache is up to date
            if changelogs==cache:
                return
            f.seek(0)
            pickle.dump(changelogs, f)

        if changelogs['release'] != cache['release']:
            await self.new_update('Release', changelogs['release']['version'], changelogs['release']['link'])
        if changelogs['beta'] != cache['beta']:
            await self.new_update('Beta', changelogs['beta']['version'], changelogs['beta']['link'])

    async def new_update(self, branch, version, link):
        log.info(f'Posting new {branch} changelog')
        # Get update channel id for update branch from all guild configs
        channels = [_get(guild.id, 'mcbecl', branch.lower()) for guild in self.bot.guilds]
        # Post to all channels
        for channel_id in channels:
            if channel_id is None:
                continue
            channel = self.bot.get_channel(channel_id)
            await channel.send(f'Minecraft Bedrock {branch} {version} Changelog:\n{link}')

    @commands.Cog.listener()
    async def on_ready(self):
        # Check for updates on when bot ready
        await self.check_feedback_site()

    @commands.command(name='latestmcbe')
    async def latestmcbe(self, ctx):
        """Link the latest release changelog for MCBE"""
        with open('mcbecl.pickle', 'rb') as f:
            cache = pickle.load(f)
        release_version =cache['release']['version']
        release_link =cache['release']['link']
        await ctx.send(f'Minecraft Bedrock {release_version} Changelog:\n{release_link}')

    @commands.command(name='latestbeta')
    async def latestbeta(self, ctx):
        """Link the latest beta changelog for MCBE"""
        with open('mcbecl.pickle', 'rb') as f:
            cache = pickle.load(f)
        beta_version =cache['beta']['version']
        beta_link =cache['beta']['link']
        await ctx.send(f'Minecraft Bedrock BETA {beta_version} Changelog:\n{beta_link}')

    @commands.group(name='updates')
    @staff_command()
    async def updates(self, ctx):
        """List/manage the channels where MCBE updates will be posted"""

        if ctx.invoked_subcommand is None:

            # Get guild's update channel dictionary
            channels = _get(ctx.guild.id, 'updates')

            guild_updates = discord.Embed(colour=0x4b4740, title = f'{ctx.guild.name} Update Channels')
            # Loop though update channel dictionary
            for branch in channels:
                channel_id = channels[branch]
                if channel_id is None:
                    guild_updates.add_field(name=branch, value='Not set')
                    continue
                channel = self.bot.get_channel(channel_id)
                guild_updates.add_field(name=branch, value=channel.mention)
            await ctx.send(embed=guild_updates)

    @updates.command(name='set')
    async def updates_set(self, ctx, channel: Optional[discord.TextChannel]=None, branch: str='all'):
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

    @updates.command(name='off')
    async def updates_off(self, ctx, branch: str='all'):
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
    async def daily(self):
        log.info('Feedback site daily check started')
        self.bihourly.start()

    @daily.before_loop
    async def before_daily(self):
        # Gets next T15:00Z
        tea_today = datetime.utcnow().replace(hour=15, minute=0, second=0, microsecond=0)
        tea_next = tea_today if datetime.utcnow().hour < 15 else tea_today + timedelta(1)
        # Sync daily check to T15:00Z
        log.info(f'Bihourly loop will begin at {tea_next}')
        await discord.utils.sleep_until(tea_next)

    @tasks.loop(minutes=30, count=10)
    async def bihourly(self):
        await self.check_feedback_site(self.bihourly.current_loop)

def setup(bot):
    bot.add_cog(Mcbecl(bot))