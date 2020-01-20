import os
import io
import discord
import ftplib

from discord.ext import commands
from dotenv import load_dotenv
from py_mcpe_stats import Query

load_dotenv()
SMP_IP = os.getenv('FTP_SMP_IP')
CMP_IP = os.getenv('FTP_CMP_IP')
SMP_UN = os.getenv('FTP_SMP_USER')
CMP_UN = os.getenv('FTP_CMP_USER')
PASS = os.getenv('FTP_PASS')

server_smp = Query('192.95.23.132', 19132)
server_cmp = Query('192.95.37.114', 19132)

class Server(commands.Cog):

    def __init__(self, bot):
        self.bot = bot
        
    @commands.Cog.listener()
    async def on_ready(self):
        print('Server tools ready')
        
    @commands.Cog.listener()
    async def on_message(self, message):
        if message.channel.id == int('661730461206183937'):
            for attachment in message.attachments:
                if attachment.filename.endswith('.mcstructure'):
                    print (f'Uploading {attachment.filename}')
                    await message.add_reaction('\U0001F504')
                    
                    # Retrieve attachment
                    file = io.BytesIO()
                    await attachment.save(file)
                    
                    # Initialize connection
                    session = ftplib.FTP(CMP_IP, CMP_UN, PASS)
                    session.cwd('/behavior_packs/vanilla/structures')
                    
                    # Check if name already exists
                    if attachment.filename in session.nlst():
                        await message.clear_reactions()
                        await message.add_reaction('\U000026A0')
                        file.close()
                        session.quit()
                        return
                    
                    # Send file
                    session.storbinary(f'STOR {attachment.filename}', file)
                    
                    # Size verification
                    session.sendcmd("TYPE i")
                    osize = session.size(f'{attachment.filename}')
                    session.sendcmd("TYPE A")
                    print (f'Origin: {attachment.size} Destination: {osize}')
                    if attachment.size == osize:
                        await message.clear_reactions()
                        await message.add_reaction('\U00002705')
                    else:
                        await message.clear_reactions()
                        await message.add_reaction('\U0000274C')
                    
                    file.close()
                    session.quit()

    @commands.command(name='status')
    async def status(self, ctx):
        server_data = server_cmp.query()
        if server_data.SUCCESS:
            await ctx.send(f'{server_data.SERVER_NAME}\n{server_data.NUM_PLAYERS}/{server_data.MAX_PLAYERS} Online\n{server_data.GAME_ID} {server_data.GAME_VERSION}')
        else:
            await ctx.send('Offline')
        
def setup(bot):
    bot.add_cog(Server(bot))