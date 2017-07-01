import abc
import time


class InterfaceStatistics(object):
    """
    Interface for StatisticsManager classes
    """
    __metaclass__ = abc.ABCMeta

    @abc.abstractmethod
    def save_statistics(self, statistics):
        """Abstract method to be implemented by the concrete StatisticsManager class.

        Args:
            statistics ([str]): List of statistics from the datapath.
                statistics[0] = ip_source
                statistics[1] = ip_dst
                statistics[2] = length of message
                statistics[3] = arriving time
        """
        pass

    @abc.abstractmethod
    def save_batch_statistics(self, flow, data):
        """Abstract method to be implemented by the concrete StatisticsManager class.

        Args:
            statistics ([str]): List of statistics from the datapath.
                statistics[0] = ip_source
                statistics[1] = ip_dst
                statistics[2] = length of message
                statistics[3] = arriving time
        """
        pass

    @abc.abstractmethod
    def get_statistics(self, table_id, max_stat, from_time_str, to_time_str):
        """Abstract method to be implemented by the concrete StatisticsManager class.

        Args:
            table_id (int): The number of the identifier to retrieve
            max_stat (int): Maximum number of list of statistics to retrieve
            from_time_str (string): the initial time
            to_time_str (string): the end time

        Return:
            A list of list os stings with the requested statistics
        """
        pass

    @staticmethod
    def delay_method(delay):
        time.sleep(delay)
        return delay
