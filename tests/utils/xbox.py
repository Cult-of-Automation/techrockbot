import aiohttp

async def getxuid(username):

    async with aiohttp.ClientSession() as session:
        async with session.get(f'https://xbl-api.prouser123.me/xuid/{username}/raw') as r:
            if r.status == 200:
                xuid = await r.text()
                return xuid