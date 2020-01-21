import os
import io
import asyncio
import aioftp

from dotenv import load_dotenv
load_dotenv()
SMP_IP = os.getenv('FTP_SMP_IP')
CMP_IP = os.getenv('FTP_CMP_IP')
SMP_UN = os.getenv('FTP_SMP_USER')
CMP_UN = os.getenv('FTP_CMP_USER')
PASS = os.getenv('FTP_PASS')

class Ftp:
    async def cmp_upload(self, name, isize, content, path='/'):
        # Initialize connection
        async with aioftp.ClientSession(CMP_IP, 21, CMP_UN, PASS) as client:
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