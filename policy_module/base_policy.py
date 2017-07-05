import abc


class InterfacePolicy(object):
    """Interface to create Policy Engines
    """
    __metaclass__ = abc.ABCMeta

    @abc.abstractmethod
    def get_bandwidth(self, flow_id, current_flows):
        """Function to assign flow rate to a given flow id.

        Note:
            Abstract method to be implemented by the concrete policy engine.

        Args:
            flow_id (str): id of the flow to monitor.
            current_flows (object): Data structure with the information
            of current flows in the network.

        Returns:
            object: a object with the rate of the given flow id.
        """
        pass

    @abc.abstractmethod
    def update_bandwidth(self, flow_id, flow_current_bandwidth,
                         flows_statistics):
        """Function to reorganize rates over the current flows.

        Note:
            Abstract method to be implemented by the concrete policy engine.

        Args:
            flow_id (str): id of the flow to monitor.
            flow_current_bandwidth (object): Data structure with the information
            of current flows in the network.
            flows_statistics (object): Data structure with the information
            of the statistics of the current flows.

        Returns:
            object: a object with the recalculated rate of the the current
            flows.
        """
        pass
