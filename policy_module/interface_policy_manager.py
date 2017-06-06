import abc


class InterfacePolicy(object):
    """
    Interface for PolicyManager classes
    """
    __metaclass__ = abc.ABCMeta
    # Todo: the class variables were omitted
    # total_capacity (int)
    # devices (dict[int] = int)

    @abc.abstractmethod
    def add_flow(self, flow_id):
        """Abstract method to be implemented by the concrete PolicyManager
        class.

        Args:
            flow_id (str): id of the flow to monitor
        """
        pass

    @abc.abstractmethod
    def statistics_request(self, flow_id, max_stat):
        """Abstract method to be implemented by the concrete PolicyManager
        class.

        Args:
            flow_id (int): The number of the identifier to retrieve
            max_stat (int): Maximum number of list of statistics to retrieve

        Return:
            A list of list of stings with the requested statistics
        """
        pass

    @abc.abstractmethod
    def statistics_handler(self, flow_id, max_stat):
        """Abstract method to be implemented by the concrete PolicyManager
        class.

        Args:
            flow_id (int): The number of the identifier to retrieve
            max_stat (int): Maximum number of list of statistics to retrieve

        Return:
            A list of list of stings with the requested statistics
        """
        pass

    @abc.abstractmethod
    def set_bandwidth(self):
        """Abstract method to be implemented by the concrete PolicyManager
        class.

        Args:
            flow_id (int): The number of the identifier to retrieve
            max_stat (int): Maximum number of list of statistics to retrieve
        """
        pass

    @abc.abstractmethod
    def remove_flow(self):
        """Abstract method to be implemented by the concrete PolicyManager
        class.

        Return:
            A string for the flow to be removed in the QoS table of the flow
            manager
        """