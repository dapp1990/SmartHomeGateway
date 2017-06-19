from statistics_module.interface_manager import InterfaceStatistics
from statistics_module.simple_statistics_manager import SimpleStatisticsManager
from aiohttp import web
import logging as log
import asyncio
import random
from concurrent.futures import ProcessPoolExecutor


# Note: check https://docs.python.org/3/library/asyncio-eventloop.html or
# https://pymotw.com/3/asyncio/executors.html for asyn operations
# using non-asyn objects
# Note: possible solution to shared object in multi-thread is using Proxy
# Objects


class StatisticsApi:

    def __init__(self,statistics_manager, level=log.INFO):

        log.basicConfig(filename='StatisticsApi.log',
                        format='%(''asctime)s - %(levelname)s - %(message)s',
                        filemode='w',
                        level=level)

        log.info("initializing StatisticsApi class")

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
        log.info("get_statistics with parameters %s", request)
        data = await request.json()

        parameters = [data['flow_id'], int(data['max_length']),
                      data['from_time'], data['to_time']]

        result = await self.loop.run_in_executor(ProcessPoolExecutor(),
                                                 self.s_m.get_statistics,
                                                 *parameters)
        log.info("result of get_statistics %s", result)
        return web.json_response({'response': result})

    async def save_statistics(self, request):
        log.info("save_statistics with parameters %s", request)
        data = await request.json()

        parameters = [data['src'], data['dst'], data['size'], data['time']]

        # cache mechanism is impossible due to the ProcessPoolExecuter,
        # which is running in other process with other MEMORY, so the cache
        # is always missed!
        # https://stackoverflow.com/questions/30333591/python-3-global-variables-with-asyncio-apscheduler
        result = await self.loop.run_in_executor(ProcessPoolExecutor(),
                                                 self.s_m.save_statistics,
                                                 parameters)

        # result =  self.s_m.save_statistics(parameters)
        log.info("result of save_statistics %s", result)
        return web.json_response({'response': result})

    # Remember, you don't have parallelism (threads etc.), you have concurrency.
    # https://stackoverflow.com/questions/42279675/syncronous-sleep-into-asyncio-coroutine
    async def root(self, request):
        log.info("root request")
        delay = random.randint(0, 1)
        log.info("delay %s", delay)
        # Executor is the solution for multi-processing with corrutines
        # https://stackoverflow.com/questions/43241221/how-can-i-wrap-a-synchronous-function-in-an-async-coroutine/43263397

        result = await self.loop.run_in_executor(ProcessPoolExecutor(),
                                                 self.s_m.delay_method, delay)
        log.info("root finish")
        return web.json_response({'response': 'dummy_data', 'delay': result})

    def run(self, port):
        log.info("Running api")
        web.run_app(self.app, port=port)

    def get_app(self):
        return self.app

if __name__ == '__main__':
    statistics_server = StatisticsApi(SimpleStatisticsManager("statistics_db"))
    statistics_server.run(5001)
