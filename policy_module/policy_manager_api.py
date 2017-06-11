from policy_module.interface_policy_manager import InterfacePolicy
from policy_module.simple_policy_manager import SimplePolicyManager
from concurrent.futures import ProcessPoolExecutor
from aiohttp import web
import asyncio
import random


class PolicyApi:

    def __init__(self, policy_manager):

        if not isinstance(policy_manager, InterfacePolicy):
            raise Exception("{} must be an instance of {}".
                            format(policy_manager.__class__,
                                   InterfacePolicy.__class__))

        self.p_m = policy_manager

        self.loop = asyncio.get_event_loop()
        self.app = web.Application()

        self.app.router.add_get('/', self.root)
        self.app.router.add_post('/get_bandwidth', self.get_bandwidth)
        self.app.router.add_post('/get_statistics', self.get_statistics)

    async def get_bandwidth(self, response):
        # Todo: implement logic to update the
        pass

    async def burst_event(self, response):
        # Todo: implement logic to update the
        pass

    async def burst_event(self, response):
        # Todo: implement logic to update the
        pass

    async def root(self, request):
        delay = random.randint(0, 5)

        result = await self.loop.run_in_executor(ProcessPoolExecutor(),
                                                 self.s_m.delay_method, delay)
        return web.json_response({'response': 'dummy_data', 'delay': result})

if __name__ == '__main__':
    policy_server = PolicyApi(SimplePolicyManager())
    policy_server.run(5002)
