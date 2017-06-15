from policy_module.interface_policy_manager import InterfacePolicy
from policy_module.simple_policy_manager import SimplePolicyManager
from concurrent.futures import ProcessPoolExecutor
from datetime import datetime, timedelta
from aiohttp import ClientSession
from aiohttp import web
import asyncio
import random
import json

# todo: create log


class PolicyApi:

    def __init__(self, policy_manager, url_statistics_server, time_lapse,
                 max_statistics):

        if not isinstance(policy_manager, InterfacePolicy):
            raise Exception("{} must be an instance of {}".
                            format(policy_manager.__class__,
                                   InterfacePolicy.__class__))

        self.p_m = policy_manager

        self.loop = asyncio.get_event_loop()
        self.app = web.Application()

        self.app.router.add_get('/', self.root)
        self.app.router.add_post('/get_bandwidth', self.get_bandwidth)
        self.app.router.add_post('/update_bandwidths', self.update_bandwidths)

        self.uss = url_statistics_server
        self.time_lapse = time_lapse
        self.max_statistics = max_statistics

    async def get_bandwidth(self, request):
        json_str = await request.json()
        data = json.loads(json_str)

        parameters = [data['flow_id'], data['current_flows']]

        result = await self.loop.run_in_executor(ProcessPoolExecutor(),
                                                 self.p_m.get_bandwidth,
                                                 *parameters)
        return web.json_response({'response': result})

    async def update_bandwidths(self, request):
        json_str = await request.json()
        data = json.loads(json_str)

        to_time = datetime.now()
        from_time = to_time - timedelta(seconds=self.time_lapse)

        statistics = {}
        async with ClientSession() as session:
            for flow_id in data['current_flows']:
                if data['flow_id'] is not flow_id:
                    j_data = {'flow_id': flow_id,
                              'max_length': self.max_statistics,
                              'from_time': str(from_time),
                              'to_time': str(to_time)}
                    async with session.post(self.uss+"get_statistics",
                                            json=j_data) as resp:
                        response = await resp.json()
                        statistics[flow_id] = response['response']
        parameters = [data['flow_id'], data['current_flows'], statistics]
        result = await self.loop.run_in_executor(ProcessPoolExecutor(),
                                                 self.p_m.update_bandwidth,
                                                 *parameters)
        return web.json_response({'response': result})

    async def root(self, request):

        async with ClientSession() as session:
            async with session.get(self.uss) as resp:
                data = await resp.json()

        return web.json_response({'response': data})

    def run(self, port):
        web.run_app(self.app, port=port)

    def get_app(self):
        return self.app

if __name__ == '__main__':
    reserved_bytes = (150 + 16) * 10
    policy_server = PolicyApi(SimplePolicyManager(200000, reserved_bytes),
                              "http://0.0.0.0:5001/", 20, 50)
    policy_server.run(5002)
