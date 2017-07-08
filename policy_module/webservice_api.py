import asyncio
import logging as log
from concurrent.futures import ProcessPoolExecutor
from datetime import datetime, timedelta

from aiohttp import ClientSession
from aiohttp import web

from policy_module.base_policy import BasePolicyEngine
from policy_module.basic_engine import PolicyEngine


class PolicyWebService:
    """API class which uses a policy engine as business layer.

    This class creates a asynchronous API via HTTP communication which
    integrates concurrency using the libraries asyncio and aiohttp.

    Args:
        policy_engine (str): Instance of a concrete policy engine.
        url_statistics_server (str): URL of the statistics WebService.
        time_lapse (int): Range of time to be test by the policy engine
        max_statistics (int): Maximum number of statistics to be obtained.
        level (int, optional): Level of logger

    Attributes:
        app (Application): A instance of the aiohttp web Application
    """
    def __init__(self, policy_engine, url_statistics_server, time_lapse,
                 max_statistics, level=log.INFO):

        log.basicConfig(format='%(''asctime)s - %(levelname)s - %(message)s',
                        filemode='w',
                        level=level)
        log.info("initializing PolicyAPI class")

        if not isinstance(policy_engine, BasePolicyEngine):
            raise Exception("{} must be an instance of {}".
                            format(policy_engine.__class__,
                                   BasePolicyEngine.__class__))

        self.p_e = policy_engine

        self.loop = asyncio.get_event_loop()
        self.app = web.Application()

        self.app.router.add_get('/', self.root)
        self.app.router.add_post('/get_bandwidth', self.get_bandwidth)
        self.app.router.add_post('/update_bandwidths', self.update_bandwidths)

        self.uss = url_statistics_server
        self.time_lapse = time_lapse
        self.max_statistics = max_statistics

    async def get_bandwidth(self, request):
        """Function that process a new flow rate request

        This class parses the http request and creates a asynchronous
        corutine in the main executor which get the new bandwidth of the
        given flow according with the policy engine.

        Args:
            request (HTTP object): HTTP object with the information  needed
            to get the new bandwidth of a given flow_id.

        Returns:
            HTTP object: Returns a HTTP object as a response with the final
            result, an error otherwise.
        """
        log.info("get_bandwidth with parameters %s",request)
        data = await request.json()

        parameters = [data['flow_id'], data['current_flows']]

        result = await self.loop.run_in_executor(ProcessPoolExecutor(),
                                                 self.p_e.get_bandwidth,
                                                 *parameters)
        log.info("result of {} get_bandwidth: {}".format(parameters[0], result))
        return web.json_response({'response': result})

    async def update_bandwidths(self, request):
        """Function that process a new flow rate request

        This class parses the http request and creates a asynchronous
        corutine in the main executor which updates/recalculates the bandwidths
        of the current flows.

        Args:
            request (HTTP object): HTTP object with the information  needed
            to update current flows.

        Returns:
            HTTP object: Returns a HTTP object as a response with the final
            recalculation, an error otherwise.
        """
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
                                                 self.p_e.update_bandwidth,
                                                 *parameters)
        log.info("result of update_bandwidths: %s", result)
        return web.json_response({'response': result})

    async def root(self, request):
        """Function that helps to debug concurrency in the WebService.

        This class parses the HTTP request and creates a asynchronous
        corutine using a asynchronous client session in the main executor
        function. It uses the Statistics WebServer and return the result.

        Args:
            request (HTTP object): HTTP object with the information  needed
            to save the statistics.

        Returns:
            HTTP object: Returns a HTTP object as a response with the result
            of Statistics WebService's result.
        """
        log.info("root request")
        async with ClientSession() as session:
            async with session.get(self.uss) as resp:
                data = await resp.json()
        log.info("finish root request")
        return web.json_response({'response': data})

    def run(self, port):
        """Function starts the Web Service as a server.

        Args:
            port (int): Port in which the servcer is going to communicate
            with the clients.
        """
        log.info("Run api")
        web.run_app(self.app, port=port)

    def get_app(self):
        return self.app

if __name__ == '__main__':
    # reserve at 10 times the MTU with overhead
    reserved_bytes = 166 * 10
    # Time lapse as much as it can possible be
    policy_server = PolicyWebService(PolicyEngine(200000, reserved_bytes),
                                     "http://0.0.0.0:5001/", 1, 10000)
    policy_server.run(5002)
