from statistics_module.interface_manager import InterfaceStatistics
from statistics_module.simple_statistics_manager import SimpleStatisticsManager
from aiohttp import web
from aiohttp import ClientSession
import asyncio
import random
import time
from concurrent.futures import ProcessPoolExecutor

# Todo: convert manager objects to async operation objects
# Todo: check https://docs.python.org/3/library/asyncio-eventloop.html or
# https://pymotw.com/3/asyncio/executors.html for asyn operations
# using non-asyn objects


class StatisticsApi:

    def __init__(self,statistics_manager):

        if not isinstance(statistics_manager, InterfaceStatistics):
            raise Exception("{} must be an instance of {}".
                            format(statistics_manager.__class__,
                                   InterfaceStatistics.__class__))

        self.s_m = statistics_manager

        self.loop = asyncio.get_event_loop()
        self.app = web.Application()

        self.app.router.add_get('/', self.root)
        self.app.router.add_post('/save_statistics', self.save_statistics)
        self.app.router.add_post('/get_statistics', self.get_statistics)

    async def get_statistics(self, request):
        data = await request.json()

        result = self.s_m.get_statistics(data['flow_id'],
                                         int(data['max_length']))

        return web.json_response(result)

    async def save_statistics(self, request):

        data = await request.json()
        parameters = [data['src'], data['dst'], data['size'], data['time']]

        result = self.s_m.save_statistics(parameters)

        return web.json_response({'response': result})

    # Remember, you don't have parallelism (threads etc.), you have concurrency.
    # https://stackoverflow.com/questions/42279675/syncronous-sleep-into-asyncio-coroutine
    async def root(self, request):
        delay = random.randint(0, 1)
        # Excutor is the solution for multi-processing with corrutines
        # https://stackoverflow.com/questions/43241221/how-can-i-wrap-a-synchronous-function-in-an-async-coroutine/43263397
        result = await self.loop.run_in_executor(ProcessPoolExecutor(),
                                                 self.s_m.delay_method, delay)
        print("The request ->", request)
        return web.json_response({'response': 'dummy_data', 'delay': result})

    def run(self, port):
        web.run_app(self.app, port=port)

    def get_app(self):
        return self.app

if __name__ == '__main__':
    test = StatisticsApi(SimpleStatisticsManager("test_db"))
    test.run(5001)
    #pass
