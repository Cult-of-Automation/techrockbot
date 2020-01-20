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
    """    
    def __init__(self):
        self.SMP_IP = os.getenv('FTP_SMP_IP')
        self.CMP_IP = os.getenv('FTP_CMP_IP')
        self.SMP_UN = os.getenv('FTP_SMP_USER')
        self.CMP_UN = os.getenv('FTP_CMP_USER')
        self.PASS = os.getenv('FTP_PASS')
    """ 
    async def cmp_upload(self, filename, file_in, path='/', isize=0):
        # Initialize connection
        async with aioftp.ClientSession(CMP_IP, 21, CMP_UN, PASS) as client:
            await client.change_directory(path)
            
            # Check if name already exists
            if await client.exists(filename):
                return 2
            
            # Send file
            print (f'Uploading {attachment.filename}')
            async with client.upload_stream(filename) as stream:
                while True:
                    data = file_in.read()
                    if not data:
                        break
                    await stream.write(data)
            
            # Size verification
            if isize:
                stat = await client.stat(filename)
                osize = int(stat['size'])
                print (f'Origin: {isize} Destination: {osize}')
                return isize == osize