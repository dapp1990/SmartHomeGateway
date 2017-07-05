from statistics_module.base_engine import BaseStatisticsEngine
from statistics_module.basic_engine import StatisticsEngine
from aiohttp import web
import logging as log
import asyncio
import random
from concurrent.futures import ProcessPoolExecutor
from threading import Thread
from queue import Queue

# Note: check https://docs.python.org/3/library/asyncio-eventloop.html or
# https://pymotw.com/3/asyncio/executors.html for asyn operations
# using non-asyn objects
# Note: possible solution to shared object in multi-thread is using Proxy
# Objects


class StatisticsWebService:
    """API class which uses a statistics engine as business layer.

    This class creates a asynchronous API via HTTP communication which
    integrates concurrency using the libraries asyncio and aiohttp.
    Additionally it implements synchronous queue with one worker to avoid
    conflicts during the saving process.

    Args:
        statistics_engine (str): Instance of a concrete statistics engine.
        level (int, optional): Level of the logger.
     Attributes:
        app (Application): A instance of the aiohttp web Application
    """
    def __init__(self, statistics_engine, level=log.INFO):

        log.basicConfig(format='%(''asctime)s - %(levelname)s - %(message)s',
                        filemode='w',
                        level=level)

        log.info("initializing StatisticsApi class")

        if not isinstance(statistics_engine, BaseStatisticsEngine):
            raise Exception("{} must be an instance of {}".
                            format(statistics_engine.__class__,
                                   BaseStatisticsEngine.__class__))

        self.s_e = statistics_engine

        self.loop = asyncio.get_event_loop()
        self.app = web.Application()

        self.app.router.add_get('/', self.root)
        self.app.router.add_post('/save_statistics', self.save_statistics)
        self.app.router.add_post('/save_batch_statistics',
                                 self.save_batch_statistics)
        self.app.router.add_post('/get_statistics', self.get_statistics)

        self.requests = Queue()
        self.requests_thread = Thread(target=self.process_request)
        self.requests_thread.daemon = True
        self.requests_thread.start()

    async def get_statistics(self, request):
        """Function that process a retriever statistics request

        This class parses the http request and creates a asynchronous
        corutine in the main executor which retrievers the data according
        with the statistics engine.

        Args:
            request (HTTP object): HTTP object with the information  needed
            to retriever the statistics of a given flow_id.

        Returns:
            HTTP object: Returns a HTTP object as a response with the final
            result, an error otherwise.
        """
        log.info("get_statistics with parameters %s", request)
        data = await request.json()

        parameters = [data['flow_id'], int(data['max_length']),
                      data['from_time'], data['to_time']]

        result = await self.loop.run_in_executor(ProcessPoolExecutor(),
                                                 self.requests.put,
                                                 [1,
                                                 parameters])
        log.info("result of get_statistics %s", result)
        return web.json_response({'response': result})

    async def save_statistics(self, request):
        """Function that process a saving statistics request

        This class parses the HTTP request and adds a new closure to the
        synchronous queue.

        Args:
            request (HTTP object): HTTP object with the information  needed
            to save the statistics.

        Returns:
            HTTP object: Returns a HTTP object as a response with True as a
            result if the function could add the closure correctly,
            False otherwise.
        """
        log.info("save_statistics with parameters %s", request)
        data = await request.json()

        parameters = [data['id_flow'], data['size'], data['time']]

        result = self.requests.put([self.s_e.save_statistics, parameters])

        # result =  self.s_m.save_statistics(parameters)
        log.info("result of save_statistics %s", result)
        return web.json_response({'response': result})

    async def save_batch_statistics(self, request):
        """Function that process a saving in batch statistics request

        This class parses the HTTP request and adds a new closure to the
        synchronous queue.

        Args:
            request (HTTP object): HTTP object with the information  needed
            to save the statistics.

        Returns:
            HTTP object: Returns a HTTP object as a response with True as a
            result if the function could add the closure correctly,
            False otherwise.
        """
        log.info("save_batch_statistics with parameters %s", request)
        data = await request.json()

        parameters = [data['id_flow'], data['batch']]
        result = self.requests.put([self.s_e.save_batch_statistics, parameters])

        log.info("result of save_statistics %s", result)
        return web.json_response({'response': result})

    async def root(self, request):
        """Function that helps to debug concurrency in the WebService.

        This class parses the HTTP request and creates a asynchronous
        corutine in the main executor using the delay_method function of the
        given instance of the concrete statistics engine.

        Args:
            request (HTTP object): HTTP object with the information  needed
            to save the statistics.

        Returns:
            HTTP object: Returns a HTTP object as a response with
            'dummy_data' as string and the delay that took the function.
            as a result, an error otherwise.
        """
        log.info("root request")
        delay = random.randint(0, 1)
        log.info("delay %s", delay)
        result = await self.loop.run_in_executor(ProcessPoolExecutor(),
                                                 self.s_e.delay_method, delay)
        log.info("root finish")
        return web.json_response({'response': 'dummy_data', 'delay': result})

    def run(self, port):
        """Function starts the Web Service as a server.

        Args:
            port (int): Port in which the servcer is going to communicate
            with the clients.
        """
        log.info("Running api")
        web.run_app(self.app, port=port)

    def get_app(self):
        return self.app

    def process_request(self):
        """Worker which execute the closure elements in the synchronous
        queue.
        """
        while True:
            function, parameters = self.requests.get()

            function(parameters)

            self.requests.task_done()

if __name__ == '__main__':
    statistics_server = StatisticsWebService(StatisticsEngine("statistics_db"))
    statistics_server.run(5001)




