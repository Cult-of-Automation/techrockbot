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

    async def cmp_upload(self, name, file, path='/', isize=0):
        # Initialize connection
        async with aioftp.ClientSession(CMP_IP, CMP_UN, PASS) as client:
            await client.change_directory(path)
            
            # Check if name already exists
            if await client.exists(name):
                return 1
            
            # Send file
            async with client.upload_stream(filename, offset=size) as stream:
                while True:
                    data = file.read(block_size)
                    if not data:
                        break
                    await stream.write(data)
            print("sending")
            
            # Size verification
            if isize:
                osize = await client.stat(name)
                print (f'Origin: {isize} Destination: {osize}')
                if not attachment.size == osize:
                    return 0