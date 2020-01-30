import io
import asyncio
import aioftp

class Ftp:

    async def _write(self, server: dict, name, isize, content, path='/', overwrite=False):
    
        # Initialize connection
        async with aioftp.ClientSession(server['ip'], int(server['pt']), server['un'], server['pw']) as client:
            await client.change_directory(path)
            
            # Check if name already exists
            if await client.exists(name)!=overwrite:
                return 2
            
            if overwrite:
                await client.remove_file(name)
            
            # Send file
            content.seek(0)
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

    async def _read(self, server: dict, path):
        
        file_out = io.BytesIO()
        
        # Initialize connection
        
        async with aioftp.ClientSession(server['ip'], int(server['pt']), server['un'], server['pw']) as client:
            async with client.download_stream(path) as stream:
                async for block in stream.iter_by_block():
                    file_out.write(block)
        
        file_out.seek(0)
        output = file_out.read()
        file_out.close()
        
        return output
