import discord
import aiohttp
import logging
import pickle
import io

from discord.ext import tasks, commands
from lxml import html
from datetime import datetime, timedelta

from tests.bot import Bot

log = logging.getLogger(__name__)

async def fetch(url):
    async with aiohttp.request('GET', url) as resp:
        assert resp.status == 200
        return await resp.read()

def next_tea():
    now = datetime.utcnow()
    tom = timedelta(1)
    tea = now.replace(hour=15, minute=0, second=0, microsecond=0)
    if now.hour >= 16:
        return tea + tom
    return tea

class Mcbecl(commands.Cog):

    def __init__(self, bot: Bot):
        self.bot = bot
        self.daily.start()

    def cog_unload():
        self.daily.cancel()
        self.bihourly.cancel()

    async def check_feedback_site(self):

        log.info('Checking feedback site...')
        release_url = 'https://feedback.minecraft.net/hc/en-us/sections/360001186971'
        beta_url = 'https://feedback.minecraft.net/hc/en-us/sections/360001185332'

        changelogs = {
            'release': {'version': None, 'link': None},
            'beta': {'version': None, 'link': None}
        }

        # Check for new release changelogs
        with io.BytesIO(await fetch(release_url)) as page:
            release_tree = html.parse(page).getroot()
        release_vers = release_tree.find_class('article-list-link')

        # Get latest Bedrock update
        for link in release_vers:
            release_linktext = link.text_content()
            if 'Bedrock' in release_linktext:
                release_sublink = link.get('href')
                break

        changelogs['release']['version'] = release_linktext[12:-10]
        changelogs['release']['link'] = f'https://feedback.minecraft.net{release_sublink}'

        # Check for new beta changelogs
        with io.BytesIO(await fetch(beta_url)) as page:
            beta_tree = html.parse(page).getroot()
        beta_vers = beta_tree.find_class('article-list-link')
        release_linktext = beta_vers[0].text_content()
        release_sublink = beta_vers[0].get('href')
        changelogs['beta']['version'] = release_linktext[17:-31]
        changelogs['beta']['link'] = f'https://feedback.minecraft.net{release_sublink}'

        # Open cache and update if changed
        with open('mcbecl.pickle', 'r+b') as f:
            cache = pickle.load(f)
            if changelogs==cache:
                return
            f.seek(0)
            pickle.dump(changelogs, f)
        if not changelogs['release']==cache['release']:
            await self.new_update('Release', changelogs['release']['version'], changelogs['release']['link'])
        if not changelogs['beta']==cache['beta']:
            await self.new_update('Beta', changelogs['beta']['version'], changelogs['beta']['link'])

    async def new_update(self, type, version, link):
        log.info(f'Posting new {type} changelog')
        channels = [661372317212868620]
        for channel_id in channels:
            channel = self.bot.get_channel(channel_id)
            await channel.send(f'Minecraft Bedrock {version} Changelog:\n{link}')

    @commands.Cog.listener()
    async def on_ready(self):
        # Check for updates on when bot ready
        await self.check_feedback_site()

    @commands.command(name='latestmcbe')
    async def latestmcbe(self, ctx):
        with open('mcbecl.pickle', 'rb') as f:
            cache = pickle.load(f)
        release_version =cache['release']['version']
        release_link =cache['release']['link']
        await ctx.send(f'Minecraft Bedrock {release_version} Changelog:\n{release_link}')

    @commands.command(name='latestbeta')
    async def latestbeta(self, ctx):
        with open('mcbecl.pickle', 'rb') as f:
            cache = pickle.load(f)
        beta_version =cache['beta']['version']
        beta_link =cache['beta']['link']
        await ctx.send(f'Minecraft Bedrock BETA {beta_version} Changelog:\n{beta_link}')

    @tasks.loop(hours=24)
    async def daily(self):
        log.info('Checking feedback site for new changelogs...')
        self.bihourly.start()

    @daily.before_loop
    async def before_daily(self):
        # Sync daily check to T15:00Z
        log.info(f'Bihourly loop will begin at {next_tea()}')
        await discord.utils.sleep_until(next_tea())
        log.info('Feedback site daily check started')

    @tasks.loop(minutes=30, count=10)
    async def bihourly(self):
        await self.check_feedback_site()

def setup(bot):
    bot.add_cog(Mcbecl(bot))