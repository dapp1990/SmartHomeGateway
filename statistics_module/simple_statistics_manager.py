from statistics_module.interface_manager import InterfaceStatistics
from tinydb import TinyDB
from tinydb import Query
from datetime import datetime


class SimpleStatisticsManager(InterfaceStatistics):
    """Naive statistics manager to store and retrieve OVS statistics
    """

    def __init__(self, database_name):
        self.db_name = database_name

    def save_statistics(self, statistics):
        #db = TinyDB('{}'.format(self.db_name))
        #db.insert({'flow_id': statistics[0], 'size': statistics[1], 'time':
        #           statistics[2]})
        #db.close()
        return True

    def get_statistics(self, flow_id, max_stat, time_from_str, time_to_str):
        return []
        """
        db = TinyDB('{}'.format(self.db_name))
        query = db.search(Query().flow_id == flow_id)
        db.close()
        time_from = datetime.strptime(time_from_str, '%Y-%m-%d %H:%M:%S.%f')
        time_to = datetime.strptime(time_to_str, '%Y-%m-%d %H:%M:%S.%f')

        result = []
        for dic in query:
            correct_format = datetime.strptime(dic['time'],
                                               '%Y-%m-%d %H:%M:%S.%f')
            if time_from < correct_format < time_to:
                result.append(dic['size'])
        size = len(result)
        if size > max_stat:
            return result[size-max_stat:]
        else:
            return result
        """
