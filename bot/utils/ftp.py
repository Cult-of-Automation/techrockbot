import io
import asyncio
import aioftp

from bot.constants import Ftp as FtpConfig

class Ftp:

    async def cmp_write(self, name, isize, content, path='/'):
    
        # Initialize connection
        async with aioftp.ClientSession(FtpConfig.cmp_ip, FtpConfig.cmp_pt, FtpConfig.cmp_un, FtpConfig.cmp_pw) as client:
            await client.change_directory(path)
            
            # Check if name already exists
            if await client.exists(name):
                return 2
            
            # Send file
            print (f'Uploading {name}')
            async with client.upload_stream(name) as stream:
                while True:
                    data = content.read()
                    if not data:
                        break
                    await stream.write(data)
            
            # Size verification
            stat = await client.stat(name)
            osize = int(stat['size'])
            print (f'Origin: {isize} Destination: {osize}')
            return isize == osize

    async def cmp_read(self, path):
        
        output = io.BytesIO()
        
        # Initialize connection
        async with aioftp.ClientSession(FtpConfig.cmp_ip, FtpConfig.cmp_pt, FtpConfig.cmp_un, FtpConfig.cmp_pw) as client:
            async with client.download_stream(path) as stream:
                async for block in stream.iter_by_block():
                    output.write(block)
        
        output.seek(0)
        return output.read()