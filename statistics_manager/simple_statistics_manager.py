from interface_manager import InterfaceManager
import shelve
from uuid import uuid4

class SimpleStatisticsManager(InterfaceManager):
    """Naive statistics manager to store and retrieve OVS statistics
    """

    def __init__(self, database_name):
        self.db_name = database_name
        self.cache = dict()
        self.max_cache = 50

    def save_statistics(self, statistics):
        flow_id = statistics[0] + statistics[1]
        data_base = shelve.open(self.db_name)

        key = str(uuid4)
        data_base[key] = statistics

        # time is not taking into account, it was neglected due to the constantly update by the client
        if flow_id not in self.cache:
            self.cache[flow_id] = [statistics[2]]
        else:
            self.cache[flow_id] = [statistics[2]] + self.cache[flow_id][:self.max_cache-1]

        return True

    def get_statistics(self, flow_id, max_stat):
        if flow_id not in self.cache:
            return []
        else:
            return self.cache[flow_id][:max_stat]