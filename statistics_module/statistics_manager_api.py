from statistics_module.interface_manager import InterfaceStatistics
from statistics_module.simple_statistics_manager import SimpleStatisticsManager
from aiohttp import web
from aiohttp import ClientSession
import asyncio
import random
import json
from concurrent.futures import ProcessPoolExecutor

# Todo: convert manager objects to async operation objects
# Todo: check https://docs.python.org/3/library/asyncio-eventloop.html or
# https://pymotw.com/3/asyncio/executors.html for asyn operations
# using non-asyn objects
# Todo: possible solution to shared object in multi-thread is using Proxy
# Objects


class StatisticsApi:

    def __init__(self,statistics_manager):

        if not isinstance(statistics_manager, InterfaceStatistics):
            raise Exception("{} must be an instance of {}".
                            format(statistics_manager.__class__,
                                   InterfaceStatistics.__class__))

        # Todo: figure out how you start the proxy object with and object
        # already created
        self.s_m = statistics_manager

        self.loop = asyncio.get_event_loop()
        self.app = web.Application()

        self.app.router.add_get('/', self.root)
        self.app.router.add_post('/save_statistics', self.save_statistics)
        self.app.router.add_post('/get_statistics', self.get_statistics)

    async def get_statistics(self, request):
        json_str = await request.json()
        data = json.loads(json_str)

        parameters = [data['flow_id'], int(data['max_length'])]

        result = await self.loop.run_in_executor(ProcessPoolExecutor(),
                                                 self.s_m.get_statistics,
                                                 *parameters)
        print(result)
        return web.json_response({'response': result})

    async def save_statistics(self, request):

        json_str = await request.json()
        data = json.loads(json_str)

        parameters = [data['src'], data['dst'], data['size'], data['time']]

        # cache mechanism is impossible due to the ProcessPoolExecuter,
        # which is running in other process with other MEMORY, so the cache
        # is always missed!
        # https://stackoverflow.com/questions/30333591/python-3-global-variables-with-asyncio-apscheduler
        result = await self.loop.run_in_executor(ProcessPoolExecutor(),
                                                 self.s_m.save_statistics,
                                                 parameters)

        # result =  self.s_m.save_statistics(parameters)

        return web.json_response({'response': result})

    # Remember, you don't have parallelism (threads etc.), you have concurrency.
    # https://stackoverflow.com/questions/42279675/syncronous-sleep-into-asyncio-coroutine
    async def root(self, request):
        delay = random.randint(0, 5)
        # Executor is the solution for multi-processing with corrutines
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
    sm = SimpleStatisticsManager("another_db")
    test = StatisticsApi(sm)
    test.run(5001)
