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
        if message.channel.id == int('661730461206183937'):
            for attachment in message.attachments:
                if not attachment.filename.endswith('.mcstructure'):
                    break
                
                # Retrieve attachment
                file = io.BytesIO()
                await attachment.save(file)
                
                # "Loading" reaction
                await message.add_reaction('\U0001F504')
                
                result = await Ftp.cmp_upload(self, attachment.filename, file, '/behavior_packs/vanilla/structures', attachment.size)
                
                file.close()
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

    # CMP server ping
    @commands.command(name='status')
    async def status(self, ctx):
        server_data = server_cmp.query()
        if server_data.SUCCESS:
            await ctx.send(f'{server_data.SERVER_NAME}\n{server_data.NUM_PLAYERS}/{server_data.MAX_PLAYERS} Online\n{server_data.GAME_ID} {server_data.GAME_VERSION}')
        else:
            await ctx.send('Offline')

def setup(bot):
    bot.add_cog(Server(bot))