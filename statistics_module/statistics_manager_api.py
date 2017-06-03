from flask import Flask, request
import time
from interface_manager import InterfaceStatistics
from simple_statistics_manager import SimpleStatisticsManager
from threading import Thread
import json
from functools import partial

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
            raise Exception("{} must be an instance of {}".format(statistics_manager.__class__,
                                                                  InterfaceStatistics.__class__))

        self.statistics_manager = statistics_manager

    def parse_request(self):
        # TODO: parse come request here
        w = request.args.get('w')
        if not w: w = 400
        else: w = int(w)

        return "one", "two", "three"

    #@app.get_send_file_max_age()
    def simple_test(self):
        start = time.clock()
        test = self.statistics_manager.save_statistics()
        end = time.clock() - start
        print ("It took {}".format(end))
        return test

    @register_route("/get_statistics")
    def get_statistics(self):
        data = request.get_json()
        parameters = data['flow_id'], data['max_length']
        thread = Thread(target=self.statistics_manager.get_statistics, args=parameters)
        thread.daemon = True
        thread.start()
        return json.dumps({'msg': 'getting_statistics'})

    @register_route("/save_statistics", methods=['POST'])
    def save_statistics(self):
        data = request.get_json()
        parameters = [data['src'], data['dst'], data['size'], data['time']]
        thread = Thread(target=self.statistics_manager.save_statistics, args=[parameters])
        thread.daemon = True
        thread.start()
        return json.dumps({'msg': 'saved'})

    @register_route("/")
    def root(self):
        return json.dumps({'msg': 'dummy_data'})

if __name__ == '__main__':

    s_api = StatisticsApi(SimpleStatisticsManager('testing_database'))
    s_api.debug = True
    s_api.run(port=5001)
