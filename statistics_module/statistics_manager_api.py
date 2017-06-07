from statistics_module.interface_manager import InterfaceStatistics
from statistics_module.simple_statistics_manager import SimpleStatisticsManager
from aiohttp import web
import asyncio
import random


class StatisticsApi:

    def __init__(self,statistics_manager):

        if not isinstance(statistics_manager, InterfaceStatistics):
            raise Exception("{} must be an instance of {}".
                            format(statistics_manager.__class__,
                                   InterfaceStatistics.__class__))

        self.statistics_manager = statistics_manager

        self.app = web.Application()
        self.app.router.add_get('/', self.root)
        self.app.router.add_post('/save_statistics', self.save_statistics)
        self.app.router.add_post('/get_statistics', self.get_statistics)

    async def get_statistics(self, request):
        data = await request.json()

        result = self.statistics_manager.get_statistics(data['flow_id'],
                                                        int(data['max_length']))

        return web.json_response(result)

    async def save_statistics(self, request):

        data = await request.json()
        parameters = [data['src'], data['dst'], data['size'], data['time']]

        result = self.statistics_manager.save_statistics(parameters)

        return web.json_response({'response': result})

    async def root(self, request):
        delay = random.randint(2, 5)
        # await asyncio.sleep(delay)
        print("The request ->", request)
        return web.json_response({'response': 'dummy_data'})

    def run(self, port):
        web.run_app(self.app, port=port)

    def get_app(self):
        return self.app

if __name__ == '__main__':
    test = StatisticsApi(SimpleStatisticsManager("test_db"))
    test.run(5001)
    #pass
