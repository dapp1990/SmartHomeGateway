from flask import Flask, request
import time
from interface_manager import InterfaceStatistics
from simple_statistics_manager import SimpleStatisticsManager
from threading import Thread
import json


class StatisticsApi:

    app = Flask(__name__)
    statistics_manager = None

    def __init__(self, statistics_manager):

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

    @staticmethod
    @app.route('/save_statistics', methods=['POST'])
    def root():
        data = request.get_json()
        print data
        thread = Thread(target=self.statistics_manager.save_statistics, args=()) #args=(*parse_request())
        thread.daemon = True
        thread.start()
        return json.dumps({'msg': 'dummy_data'})

    @staticmethod
    @app.route('/')
    def test():
        return json.dumps({'msg': 'dummy_data'})

    def run(self,port=5000,host='0.0.0.0',debug_mode=False):
        self.app.debug = debug_mode
        self.app.run(host=host, port=port)

if __name__ == '__main__':

    s_api = StatisticsApi(SimpleStatisticsManager('testing_database'))
    s_api.run(port=5001,debug_mode=True)
