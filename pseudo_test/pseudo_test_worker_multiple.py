import asyncio
from aiohttp import ClientSession

async def fetch(url, session):
    async with session.get(url) as response:
        return await response.read()

async def run(r):
    url = "http://localhost:5001"
    # url = "http://aiohttp.readthedocs.io/en/stable/"
    tasks = []

    # Fetch all responses within one Client session,
    # keep connection alive for all requests.
    async with ClientSession() as session:
        for i in range(r):
            task = asyncio.ensure_future(fetch(url, session))
            tasks.append(task)

        responses = await asyncio.gather(*tasks)
        # you now have all response bodies in this variable
        print(responses)

def print_responses(result):
    print(result)

loop = asyncio.get_event_loop()
future = asyncio.ensure_future(run(100))

for i in range(100):
    print ("waiting... {}".format(i))

loop.run_until_complete(future)

