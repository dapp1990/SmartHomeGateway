from flask import Flask, request
from flask_restful import Resource,Api
import time
from interface_manager import InterfaceStatistics
from simple_statistics_manager import SimpleStatisticsStatistics
from threading import Thread

application = Flask(__name__)

statistics_manager = SimpleStatisticsStatistics()

if not isinstance(statistics_manager, InterfaceStatistics):
    raise Exception("{} must be an instance of {}".format(statistics_manager.__class__, InterfaceStatistics.__class__))


def parse_request():
    # TODO: parse come request here
    w = request.args.get('w')
    if not w: w = 400
    else: w = int(w)

    return "one", "two", "three"

def simple_test():
    start = time.clock()
    test = statistics_manager.save_statistics("something here!")
    end = time.clock() - start
    print ("It took {}".format(end))
    return test


@application.route('/')
def root():
    thread = Thread(target = simple_test, args=()) #args=(*parse_request())
    thread.daemon = True
    thread.start()
    return 'It was saved'
    # return 'The result is {}'.format(simple_test())
    # return '{} {} {}'.format(*parse_request())


if __name__ == '__main__':
    application.debug=True
    application.run()