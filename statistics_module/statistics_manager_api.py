from statistics_module.interface_manager import InterfaceStatistics
from statistics_module.simple_statistics_manager import SimpleStatisticsManager
from threading import Thread
import json
from functools import partial
import requests

import asyncio
from datetime import datetime
from aiohttp import web
import random

import async_timeout


class StatisticsApi:

    def __init__(self,statistics_manager, port=5000):

        if not isinstance(statistics_manager, InterfaceStatistics):
            raise Exception("{} must be an instance of {}".
                            format(statistics_manager.__class__,
                                   InterfaceStatistics.__class__))

        self.statistics_manager = statistics_manager

        app = web.Application()
        app.router.add_get('/', self.root)
        app.router.add_post('/save_statistics', self.save_statistics)
        app.router.add_post('/get_statistics', self.get_statistics)
        web.run_app(app, port=port)

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
        print(request)
        return web.json_response({'response': 'dummy_data'})

    def request_handler(self, command, url_response):
        # Todo: change this switch/dictionary statement with a command pattern
        result = {
            1: self.statistics_manager.save_statistics,
            2: self.statistics_manager.get_statistics,
        }[command]

        data = json.dumps({'response': result})

        # Todo: No failure controller
        r = requests.post(url_response, data=data)

    def run(self, command, url_response):
        # Todo: change this switch/dictionary statement with a command pattern
        result = {
            1: self.statistics_manager.save_statistics,
            2: self.statistics_manager.get_statistics,
        }[command]

        data = json.dumps({'response': result})

        # Todo: No failure controller
        r = requests.post(url_response, data=data)

if __name__ == '__main__':
    tes = StatisticsApi(SimpleStatisticsManager("test_db"), 5001)
    #pass
