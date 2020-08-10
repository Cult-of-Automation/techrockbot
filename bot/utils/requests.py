import logging
import io
import asyncio
import aiohttp
import aioftp

log = logging.getLogger(__name__)

async def fetch_text(url):
    """Fetch text content from url"""
    async with aiohttp.request('GET', url) as resp:
        assert resp.status == 200
        return await resp.text()

async def fetch_xuid(username):
    """Fetch XUID from Xbox username"""
    return fetch_text(f'https://xbl-api.prouser123.me/xuid/{username}/raw')

block_size = 512

async def ftp_write(server: dict, name, isize, file_in, path='/', overwrite=False):

    ip, pt, un, pw, _ = server.values()

    log.info(f'Uploading {name} to {ip}')
    # Initialize connection
    async with aioftp.ClientSession(ip, pt, un, pw) as client:
        await client.change_directory(path)
        
        # Check if name already exists
        if await client.exists(name):
            if not overwrite:
                log.warning(f'{path}{name} already exists')
                return 2
            log.info(f'Overwriting {path}{name}')
            await client.remove_file(name)
        
        # Send file
        file_in.seek(0)
        async with client.upload_stream(name) as stream:
            while True:
                data = file_in.read(block_size)
                if not data:
                    break
                await stream.write(data)
        
        # Size verification
        stat = await client.stat(name)
        dsize = int(stat['size'])
        log.info(f'Origin: {isize} Destination: {dsize}')
        return isize != dsize

async def ftp_read(server: dict, path):

    ip, pt, un, pw, _ = server.values()

    with io.BytesIO() as file_out:
        # Initialize connection
        log.info(f'Downloading {path} from {ip}')
        async with aioftp.ClientSession(ip, pt, un, pw) as client:
            async with client.download_stream(path) as stream:
                async for block in stream.iter_by_block(block_size):
                    file_out.write(block)
        file_out.seek(0)
        return file_out.read()
