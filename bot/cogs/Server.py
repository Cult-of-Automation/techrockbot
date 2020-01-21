import io
import discord

from discord.ext import commands
from ftp import Ftp
from py_mcpe_stats import Query

server_smp = Query('192.95.23.132')
server_cmp = Query('192.95.37.114')

class Server(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        print('Server tools ready')
    
    # CMP .mcstructure file upload
    @commands.Cog.listener()
    async def on_message(self, message):
        if message.channel.id in [int('661730461206183937'), int('661372317212868620')]:
            for attachment in message.attachments:
                if not attachment.filename.endswith('.mcstructure'):
                    break
                
                name = attachment.filename
                size = attachment.size
                content = io.BytesIO()
                # Retrieve attachment
                await attachment.save(content)
                
                # "Loading" reaction
                await message.add_reaction('\U0001F504')
                
                result = await Ftp.cmp_upload(self, name, size, content, '/behavior_packs/vanilla/structures')
                
                content.close()
                await message.clear_reactions()
                if result==2:
                    # "Duplicate" reaction
                    await message.add_reaction('\U000026A0')
                elif result==1:
                    # "Success" reaction
                    await message.add_reaction('\U00002705')
                elif result==0:
                    # "Failed" reaction
                    await message.add_reaction('\U0000274C')

    # Minecraft server ping
    @commands.command(name='status')
    async def status(self, ctx, content=" "):
        if not content=="cmp":
            smp_data = server_smp.query()
            smp_status = discord.Embed(title="TechRock Survival")
            smp_status.add_field(name="IP", value="survival.techrock.org", inline=False)
            if smp_data.SUCCESS:
                smp_status.colour=0x00ff00
                smp_status.description="Online"
                smp_status.add_field(name="Players", value=f'{smp_data.NUM_PLAYERS}/{smp_data.MAX_PLAYERS}', inline=True)
                smp_status.add_field(name=smp_data.GAME_ID, value=smp_data.GAME_VERSION, inline=True)
            else:
                smp_status.colour=0xff0000
                smp_status.description="Offline"
            await ctx.send(embed=smp_status)
        if not content=="smp":
            cmp_data = server_cmp.query()
            cmp_status = discord.Embed(title="TechRock Creative")
            cmp_status.add_field(name="IP", value="creative.techrock.org", inline=False)
            if cmp_data.SUCCESS:
                cmp_status.colour=0x00ff00
                cmp_status.description="Online"
                cmp_status.add_field(name="Players", value=f'{cmp_data.NUM_PLAYERS}/{cmp_data.MAX_PLAYERS}', inline=True)
                cmp_status.add_field(name=cmp_data.GAME_ID, value=cmp_data.GAME_VERSION, inline=True)
            else:
                cmp_status.colour=0xff0000
                cmp_status.description="Offline"
            await ctx.send(embed=cmp_status)

def setup(bot):
    bot.add_cog(Server(bot))