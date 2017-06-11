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
    def get_bandwidth(self, flow_id, current_flows):
        """Abstract method to be implemented by the concrete PolicyManager
        class.

        Args:
            flow_id (str): id of the flow to monitor
            current_flows ({str: int}): dictionary with the current flows in
            the network
        """
        pass

    @abc.abstractmethod
    def update_bandwidth(self, flow_id, flow_current_bandwidth,
                         flows_statistics):
        """Abstract method to be implemented by the concrete PolicyManager
        class.

        Args:
            flow_id (int): The number of the identifier to retrieve
            max_stat (int): Maximum number of list of statistics to retrieve
        """
        pass
