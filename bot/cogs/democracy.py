import logging
import csv
import io
import pickle

from datetime import datetime, timedelta
from discord import Embed, Member
from discord.ext import tasks, commands
from discord.utils import sleep_until

from bot.constants import Colours, Emojis, Icons
from bot.utils.requests import fetch_text

log = logging.getLogger(__name__)

async def get_entries(url):
    """
    Get timestamped rows from csv file
    Returns new rows from last check
    """
    # Get datetime of last check
    now = {'appcheck': datetime.utcnow()}
    with open('.pickle', 'r+b') as f:
        _pickle = pickle.load(f)
        try:
            last_check = _pickle['democracy']['appcheck']
        except KeyError:
            log.warning('Unable to retrieve last check datetime')
            return []
        _pickle.update({'democracy': now})
        f.seek(0)
        pickle.dump(_pickle, f)
        f.truncate()

    # Get list of applications entries with timestamp after last_check
    new_entries = []
    datefmt = '%d/%m/%Y %H:%M:%S'
    with io.StringIO(await fetch_text(url)) as f:
        next(f)
        reader = csv.DictReader(f)
        for row in reader:
            row_timestamp = datetime.strptime(row['.Timestamp'], datefmt)
            if last_check <= row_timestamp:
                new_entries.append(row)
    return new_entries

class Democracy(commands.Cog):

    def __init__(self, bot):
        self.bot = bot
        #self.loop_entries.start()

    def cog_unload():
        #self.loop_entries.cancel()
        pass

    async def cog_check(self, ctx):
        """TechRock-only check"""
        return ctx.guild.id==659832580731961374

    @commands.Cog.listener()
    async def on_ready(self):
        """Check for new application entries on when bot ready"""
        await self.post_entries()
        pass

    @tasks.loop(hours=24)
    async def loop_entries(self):
        await self.post_entries()

    @loop_entries.before_loop
    async def before_loop_entries(self):
        """Sync daily check to T00:00"""
        midnight_today = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
        midnight_next = tea_today if datetime.utcnow().hour < 0 else midnight_today + timedelta(1)
        log.info(f'Next check for application entries at {midnight_next}')
        await sleep_until(midnight_next)

    async def post_entries(self):
        """Post new application entries to guild application channel"""
        log.info('Checking for new application entries')

        checklist_urls = {
            'cmp': 'https://docs.google.com/spreadsheets/d/e/2PACX-1vShlqb3iFZL5HpvWe62-hXeRJ_j6CtSo_TUzjCE2h-lou4bHdFQJKcmDx97VvzjFAze2i9vIzl2ErEs/pub?gid=181078935&single=true&output=csv'
        }

        new_entries = await get_entries(checklist_urls['cmp'])
        userconverter = commands.UserConverter()
        sargs = '#_-'

        cid = 661372317212868620
        entry_channel = self.bot.get_channel(cid)

        for new_entry in new_entries:

            entry_embed = Embed(colour=Colours.techrock)
            for key, value in new_entry.items():

                value = 'None' if value=='' else str(value)

                # Embed Description bool
                if key[0]=='*':
                    if value!='None':
                        entry_embed.description = key[1:]
                    continue

                if key[0]=='.':
                    continue

                inline = True
                while key[0] in sargs:

                    # Title and User Avatar
                    if key[0]=='#':
                        try:
                            entry_user = await userconverter.convert(entry_channel, value)
                            icon_url = entry_user.avatar_url
                        except:
                            icon_url = Icons.techrock

                    elif key[0]=='_':
                        inline = False

                    # Split uploads into hyperlinks
                    elif key[0]=='-' and value!='None':
                        media_links = value.split(', ')
                        value = ''
                        for i, link in enumerate(media_links, 1):
                            value += f'[{i}]({link}) '

                    else:
                        raise

                    key = key[1:]

                entry_embed.add_field(name = key, value=value, inline=inline)

            entry_embed.set_author(name='CMP Application', icon_url=icon_url)
            msg = await entry_channel.send(embed=entry_embed)
            await msg.add_reaction(Emojis.thumbs_up)
            await msg.add_reaction(Emojis.thumbs_down)

    @commands.command(name='nominate')
    @commands.has_role('Helper')
    async def nominate(self, ctx, nominee: Member):

        await ctx.message.delete()

        cid = 661372317212868620
        entry_channel = self.bot.get_channel(cid)

        title = role + ' Role Nomination'

        datefmt = '%Y %b %d'
        join_date = nominee.joined_at.strftime(datefmt)
        regi_date = nominee.created_at.strftime(datefmt)
        
        midnight_today = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
        midnight_next = tea_today if datetime.utcnow().hour < 0 else midnight_today + timedelta(1)
        count_datetime = midnight_next + timedelta(3)
        
        footer_text = 'Votes will be counted on ' + count_datetime.isoformat() + 'Z'

        nomination = Embed(colour=Colours.techrock)
        nomination.set_author(name='Trusted Role Nomination', icon_url = nominee.avatar_url)
        nomination.add_field(name = 'Nominee',      value = nominee.display_name, inline=False)
        nomination.add_field(name = 'Joined',       value = join_date)
        nomination.add_field(name = 'Registered',   value = regi_date)
        nomination.set_footer(text = footer_text, icon_url = Icons.techrock)
        
        msg = await entry_channel.send(embed=nomination)
        await msg.add_reaction(Emojis.thumbs_up)
        await msg.add_reaction(Emojis.thumbs_down)

def setup(bot):
    bot.add_cog(Democracy(bot))