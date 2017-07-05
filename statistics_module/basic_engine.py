from statistics_module.base_engine import BaseStatisticsEngine
from tinydb import TinyDB
from tinydb import Query
from datetime import datetime


class StatisticsEngine(BaseStatisticsEngine):
    """Basic implementation of a Statistics engine.

    This class implements a statistics engine using a TinyDB as database.
    Compact and powerful enough to be implemented din constrained devices
    such as Raspberry Pi.

    Args:
        database_name (str): Name of the database to be created and used by
        the engine.
    """
    def __init__(self, database_name):
        self.db_name = database_name

    def save_statistics(self, statistics):
        """Function to save a single entry in the DataBase.

        This function assumed a list of size 3 creates a new DB if does not
        exists and saves the entry into the DB.

        Args:
            statistics ((str, str, str)): List of three elements flow_id,
            size and time.

        Returns:
            bool: true if successful, False otherwise.
        """
        flow_id, size, time = statistics
        try:
            db = TinyDB('{}'.format(self.db_name))
            db.insert({'flow_id': flow_id, 'size': size, 'time': time})
            db.close()
            return True
        except:
            return False

    def save_batch_statistics(self, statistics):
        """Function to save a batch of entries in the DataBase

        This function assumed a tuple. The batch works over a given flow with
        its given statistics. It creates a new DB if does not exists and
        saves the entries into the DB.

        Args:
            statistics ((str, [(str, str)])): tuple where the first element
            represents the flow id and the second element a list of tuple (
            size, time) of the packets to be stored.

        Returns:
            bool: true if successful, False otherwise.
        """
        flow_id, subinfo = statistics
        try:
            db = TinyDB('{}'.format(self.db_name))
            for el in subinfo:
                size, time = el
                db.insert({'flow_id': flow_id, 'size': size, 'time': time})
            db.close()
            return True
        except:
            return False

    def get_statistics(self, statistics):
        """Function to retriever statistics (size and time) of a given flow id.

        This function a list of 4 elements. It search for the elements of the
        given flow id and it is constrained by the given time range and a
        maximum size of list.

        Args:
            statistics ((str, str, str, str, str)): tuple where the first
            element represents the flow id and the second element a list of
            tuple (size, time) of the packets to be stored.

        Returns:
            list: return a list of tuples (str, str) where the first element
            is the size of the packet and the second element the time in
            which it was caught.
        """
        flow_id, max_stat, time_from_str, time_to_str = statistics

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
