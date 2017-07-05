import abc
import time


class BaseStatisticsEngine(object):
    """Interface to create Statistics Engines
    """
    __metaclass__ = abc.ABCMeta

    @abc.abstractmethod
    def save_statistics(self, statistics):
        """Function to save a single entry in the DataBase

        This function assumed just a single set of attributes of the element
        to be saved.

        Note:
            Abstract method to be implemented by the concrete Statistics engine.

        Args:
            statistics ([str]): List of strings about the flow to be saved.

        Returns:
            True if successful, False otherwise.
        """
        pass

    @abc.abstractmethod
    def save_batch_statistics(self, statistics):
        """Function to save a batch of entries in the DataBase

        This function assumed a list of set of attributes of N entries to be
        store in the DataBase.

        Note:
            Abstract method to be implemented by the concrete Statistics engine.

        Args:
            statistics (object): Data structure about the flow to be saved.

        Returns:
            bool: True if successful, False otherwise.
        """
        pass

    @abc.abstractmethod
    def get_statistics(self, statistics):
        """Function to get entries from the DataBase

        This function retrieves entries given the input/query. The entries
        are the number of packets and the sizes of a given flow.

        Note:
            Abstract method to be implemented by the concrete Statistics engine.

        Args:
            statistics ([[str]]): List of lists of strings about the flow to
            be saved.

        Returns:
            list(obj): list of general objects which contain the number of
            messages and sizes of the given flow.
        """
        pass

    @staticmethod
    def delay_method(delay):
        """Function to test delay in replies.

        This function delays the given number of seconds.

        Args:
            delay (int): the number of seconds to be delayed.

        Returns:
            int: the delay in seconds.
        """
        time.sleep(delay)
        return delay
