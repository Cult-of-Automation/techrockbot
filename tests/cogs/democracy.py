import logging
import aiohttp
import csv
import io

from datetime import datetime, timedelta
from discord import Embed
from discord.ext import tasks, commands

log = logging.getLogger(__name__)

async def fetch(url):
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as resp:
            assert resp.status == 200
            return await resp.text()

async def get_applications(url):

    datefmt = '%d/%m/%Y %H:%M:%S'
    now = datetime.utcnow().strftime(datefmt)

    # Get datetime of last check
    with open('lastappcheck', 'r+') as f:
        last_check_raw = f.read()
        f.seek(0)
        f.write(now)
    last_check = datetime.strptime(last_check_raw, datefmt)

    # Get list of apps with timestamp after last_check
    with io.StringIO(await fetch(url)) as f:
        reader = csv.DictReader(f)
        new_apps = [row for row in reader if last_check <= datetime.strptime(row['Timestamp'], datefmt)]
    return new_apps

class Democracy(commands.Cog):

    def __init__(self, bot):
        self.bot = bot
        self.dailyapp.start()

    def cog_unload():
        self.dailyapp.cancel()

    # TechRock-only check
    async def cog_check(self, ctx):
        return ctx.guild.id==659832580731961374

    async def post_new_apps(self):

        log.info('Checking for new applications')

        checklist_urls = {
            'cmp': 'https://docs.google.com/spreadsheets/d/e/2PACX-1vShlqb3iFZL5HpvWe62-hXeRJ_j6CtSo_TUzjCE2h-lou4bHdFQJKcmDx97VvzjFAze2i9vIzl2ErEs/pub?gid=181078935&single=true&output=csv',
            'smp': 'https://docs.google.com/spreadsheets/d/e/2PACX-1vRTqR018lkhKqOf4ToC5RJC4WBFP31Sv7hPD0-eZMXLQf5mmPCo5STU4v1z6s3HIvT2rIG4F1IRqC7N/pub?gid=1666125740&single=true&output=csv'
        }

        new_apps = await get_applications(checklist_urls['cmp'])
        cid = 661372317212868620
        app_channel = self.bot.get_channel(cid)
        userconverter = commands.UserConverter()
        
        for new_app in new_apps:

            app = list(new_app.values())

            app_embed = Embed(colour=0x4b4740)

            # Get user
            try:
                app_user = await userconverter.convert(app_channel, app[2])
                app_embed.set_author(name='CMP Application', icon_url = app_user.avatar_url)
            except:
                app_embed.set_author(name='CMP Application')

            app_embed.add_field(name = 'Discord Username', value = app[2])
            app_embed.add_field(name = 'GamerTag', value = app[3])
            app_embed.add_field(name = 'Age', value = app[4])
            app_embed.add_field(name = 'Technical Niches', value = app[5])
            app_embed.add_field(name = 'Minecraft Experience', value = app[7], inline=False)
            app_embed.add_field(name = 'Social Media', value = app[8])
            app_embed.add_field(name = 'Links', value = app[9])

            # Split uploads into hyperlinks
            if app[6]:
                media_links = ''
                media_links_list = app[6].split(', ')
                for i, link in enumerate(media_links_list, 1):
                    media_links += f'[{i}]({link}) '
            else:
                media_links = 'None'

            app_embed.add_field(name = 'Pictures/Videos', value = media_links)

            msg = await app_channel.send(embed=app_embed)
            await msg.add_reaction('\U0001F44D')
            await msg.add_reaction('\U0001F44E')


    @commands.Cog.listener()
    async def on_ready(self):
        # Check for new apps on when bot ready
        #await self.post_new_apps()
        pass

    @tasks.loop(hours=24)
    async def dailyapp(self):
        #await self.post_new_apps()
        pass

    @dailyapp.before_loop
    async def before_dailyapp(self):
        # Gets next T00:00Z
        midnight_today = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
        midnight_next = tea_today if datetime.utcnow().hour < 0 else midnight_today + timedelta(1)
        # Sync daily check to T00:00Z
        log.info(f'Application loop will begin at {midnight_next}')
        await discord.utils.sleep_until(midnight_next)

def setup(bot):
    bot.add_cog(Democracy(bot))