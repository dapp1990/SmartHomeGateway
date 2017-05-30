import abc


class InterfaceManager(object):
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
    def get_statistics(self, table_id, max_stat):
        """Abstract method to be implemented by the concrete StatisticsManager class.

        Args:
            table_id (int): The number of the identifier to retrieve
            max_stat (int): Maximum number of list of statistics to retrieve

        Return:
            A list of list os stings with the requested statistics
        """
        pass