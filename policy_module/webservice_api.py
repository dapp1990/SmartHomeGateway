import asyncio
import logging as log
from concurrent.futures import ProcessPoolExecutor
from datetime import datetime, timedelta

from aiohttp import ClientSession
from aiohttp import web

from policy_module.base_policy import InterfacePolicy
from policy_module.basic_engine import MediumPolicyManager


class PolicyApi:

    def __init__(self, policy_manager, url_statistics_server, time_lapse,
                 max_statistics, level=log.INFO):

        log.basicConfig(#filename='PolicyAPI.log',
                        format='%(''asctime)s - %(levelname)s - %(message)s',
                        filemode='w',
                        level=level)
        log.info("initializing PolicyAPI class")

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
        log.info("get_bandwidth with parameters %s",request)
        data = await request.json()

        parameters = [data['flow_id'], data['current_flows']]

        result = await self.loop.run_in_executor(ProcessPoolExecutor(),
                                                 self.p_m.get_bandwidth,
                                                 *parameters)
        log.info("result of {} get_bandwidth: {}".format(parameters[0], result))
        return web.json_response({'response': result})

    async def update_bandwidths(self, request):
        log.info("update_bandwidths with parameters %s", request)
        data = await request.json()

        to_time = datetime.now()
        from_time = to_time - timedelta(seconds=self.time_lapse)
        log.info("This is the requester {} ".format(data['flow_id']))

        if not data['cache']:
            statistics = {}
            async with ClientSession() as session:
                for flow_id in data['current_flows']:
                    if flow_id not in statistics \
                            and data['flow_id'] is not flow_id:
                        j_data = {'flow_id': flow_id,
                                  'max_length': self.max_statistics,
                                  'from_time': str(from_time),
                                  'to_time': str(to_time)}
                        async with session.post(self.uss+"get_statistics",
                                                json=j_data) as resp:
                            response = await resp.json()
                            statistics[flow_id] = response['response']
        parameters = [data['flow_id'], data['current_flows'], data['cache'],
                      data['time_request']]
        result = await self.loop.run_in_executor(ProcessPoolExecutor(),
                                                 self.p_m.update_bandwidth,
                                                 *parameters)
        log.info("result of update_bandwidths: %s", result)
        return web.json_response({'response': result})

    async def root(self, request):
        log.info("root request")
        async with ClientSession() as session:
            async with session.get(self.uss) as resp:
                data = await resp.json()
        log.info("finish root request")
        return web.json_response({'response': data})

    def run(self, port):
        log.info("Run api")
        web.run_app(self.app, port=port)

    def get_app(self):
        return self.app

if __name__ == '__main__':
    reserved_bytes = (150 + 16) * 10
    policy_server = PolicyApi(MediumPolicyManager(200000, reserved_bytes),
                              "http://0.0.0.0:5001/", 1, 10000)
    policy_server.run(5002)
