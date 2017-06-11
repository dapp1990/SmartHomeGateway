from .interface_manager import InterfaceStatistics
from tinydb import TinyDB
from tinydb_serialization import SerializationMiddleware
from tinydb import Query
from datetime import datetime
from tinydb_serialization import Serializer
import time


# https://github.com/msiemens/tinydb-serialization
class DateTimeSerializer(Serializer):
    OBJ_CLASS = datetime  # The class this serializer handles

    def encode(self, obj):
        return obj.strftime('%Y-%m-%dT%H:%M:%S')

    def decode(self, s):
        return datetime.strptime(s, '%Y-%m-%dT%H:%M:%S')


class SimpleStatisticsManager(InterfaceStatistics):
    """Naive statistics manager to store and retrieve OVS statistics
    """

    def __init__(self, database_name):
        self.serialization = SerializationMiddleware()
        self.serialization.register_serializer(DateTimeSerializer(), 'TinyDate')
        self.db = TinyDB('{}'.format(database_name),storage=self.serialization)

    def save_statistics(self, statistics):
        flow_id = statistics[0] + statistics[1]
        self.db.insert({'flow_id': flow_id, 'size': statistics[2],
                        'time': datetime.strptime(statistics[3], '%Y-%m-%d '
                                                                 '%H:%M:%S.%f')})
        return True

    def get_statistics(self, flow_id, max_stat, time_from_str, time_to_str):
        time_from = datetime.strptime(time_from_str, '%Y-%m-%d %H:%M:%S.%f')
        time_to = datetime.strptime(time_to_str, '%Y-%m-%d %H:%M:%S.%f')
        query = self.db.search(Query().flow_id == flow_id)
        result = []
        for dic in query:
            if time_from < dic['time'] < time_to:
                result.append(dic['size'])
        size = len(result)
        if size > max_stat:
            return result[size-max_stat:]
        else:
            return result
