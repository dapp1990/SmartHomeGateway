from interface_manager import InterfaceManager
import shelve
from uuid import uuid4

class SimpleStatisticsManager(InterfaceManager):
    """Naive statistics manager to store and retrieve OVS statistics
    """

    def __init__(self):
        self.data_base = shelve.open('ovs_statistics.dat')

    def save_statistics(self, ev):
        key = str(uuid4)
        self.data_base[key] = ev
        return True

    def get_statistics(self, number_id, max_stat):
        # TODO(dapp): implement get_statistics!
        pass