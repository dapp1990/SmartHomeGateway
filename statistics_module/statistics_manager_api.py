from flask import Flask, request
import time
from .interface_manager import InterfaceStatistics
from .simple_statistics_manager import SimpleStatisticsManager
from threading import Thread
import json
from functools import partial
import requests


registered_routes = {}


def register_route(route=None, methods=['GET']):
    #simple decorator for class based views
    def inner(fn):
        registered_routes[route] = (fn, methods)
        return fn
    return inner


class StatisticsApi(Flask):

    def __init__(self,statistics_manager, *args, **kwargs):
        if not args:
            kwargs.setdefault('import_name', __name__)
        Flask.__init__(self, *args, **kwargs)

        # register the routes from the decorator
        for route, (fn, ms) in registered_routes.items():
            partial_fn = partial(fn, self)
            partial_fn.__name__ = fn.__name__
            self.route(route, methods=ms)(partial_fn)

        if not isinstance(statistics_manager, InterfaceStatistics):
            raise Exception("{} must be an instance of {}".
                            format(statistics_manager.__class__,
                                   InterfaceStatistics.__class__))

        self.statistics_manager = statistics_manager

    @register_route("/get_statistics")
    def get_statistics(self):
        data = request.get_json()
        parameters = data['flow_id'], data['max_length']
        url_response = data['response']

        thread = Thread(target=self.request_handler(2, url_response),
                        args=parameters)
        thread.daemon = True
        thread.start()

    @register_route("/save_statistics", methods=['POST'])
    def save_statistics(self):

        data = request.get_json()
        parameters = [data['src'], data['dst'], data['size'], data['time']]
        url_response = data['response']

        thread = Thread(target=self.request_handler(1, url_response),
                        args=[parameters])
        thread.daemon = True
        thread.start()

    @register_route("/")
    def root(self):
        return json.dumps({'response': 'dummy_data'})

    def request_handler(self, command, url_response):
        # Todo: change this switch/dictionary statement with a command pattern
        result = {
            1: self.statistics_manager.save_statistics,
            2: self.statistics_manager.get_statistics,
        }[command]

        data = json.dumps({'response': result})

        # Todo: No failure controller
        r = requests.post(url_response, data=data)


if __name__ == '__main__':

    s_api = StatisticsApi(SimpleStatisticsManager('testing_database'))
    s_api.debug = True
    s_api.run(port=5001)
