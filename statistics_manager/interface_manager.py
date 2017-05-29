import abc


class InterfaceManager(object):
    """
    Interface for StatisticsManager classes
    """
    __metaclass__ = abc.ABCMeta

    @abc.abstractmethod
    def save_statistics(self, ev):
        """Abstract method to be implemented by the concrete StatisticsManager class.

        Args:
            ev ([str]): List of statistics from the datapath
        """
        pass

    @abc.abstractmethod
    def get_statistics(self, number_id, max_stat):
        """Abstract method to be implemented by the concrete StatisticsManager class.

        Args:
            number_id (int): The number of the identifier to retrieve
            max_stat (int): Maximum number of list of statistics to retrieve

        Return:
            A list of list os stings with the requested statistics
        """
        pass