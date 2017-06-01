from interface_policy_manager import InterfacePolicy
import shelve
from uuid import uuid4
import numpy as np
import util

# Todo: add a wrapper that notifies immediately to the flow manager when there is an update
class SimplePolicyManager(InterfacePolicy):
    """Naive statistics manager to store and retrieve OVS statistics

    This class reserve (MTU * 10) bytes from the max_capacity given to assign to every new flow.

    """

    def __init__(self, max_capacity, reserved_bytes):
        self.flows = dict()
        self.requests = []
        self.max_capacity = max_capacity - reserved_bytes
        self.reserved_bytes = reserved_bytes
        self.current_capacity = 0

    def add_flow(self, flow_id):
        """Abstract method to be implemented by the concrete PolicyManager class.

        Args:
            flow_id (str): id of the flow to monitor
        """
        self.flows[flow_id] = self.reserved_bytes
        self.current_capacity += self.reserved_bytes

        # Todo: send response to flow manager

    def bottleneck_request(self, flow_id):
        """Abstract method to be implemented by the concrete PolicyManager class.

        Args:
            flow_id (str): id of the flow to monitor
        """

        self.requests = [flow_id]

        # Todo: send response to flow manager

    def remove_flow(self):
        if 3 == 4:
            return 4
        pass

    def statistics_handler(self, message, type):
        """Abstract method to be implemented by the concrete PolicyManager class.


        Args:
            flow_id (int): The number of the identifier to retrieve
            max_stat (int): Maximum number of list of statistics to retrieve

        Return:
            A list of list os stings with the requested statistics
        """

        # Todo: use dynamic dispatching here for a proper OOP!

        self.update_bandwidth(self, message[1:], message[0](0))

        # Todo: send to flow module

    # Todo: add hard constrains (max and min bandwidth rate)
    def update_bandwidth(self, flows, flow_id):
        """Update the bandwidths of the given flows.

        Look over all the active flows and look for inactive flows. Assign a bandwidth of zero to inactive flows and
        reduce the capacity of the flows if its current bandwidth is greater than the actual bandwidth, given
        by statistics.
        Inactive flow is a flow that, according with the statistics, has a bandwidth smaller than the *RESERVED_BYTES*
        Recalculate current capacity and assigns the smallest value given by double bandwidth of the given flow,
        the available bandwidth of the network or the maximum bandwidth rate assigned (in case of hard constraint).
        If the available capacity is zero, the bandwidth of the given flow_id is not changed.

        Args:
            flows ([(str,[int])]): Statistics of the last active flows
            flow_id (int): The flow id which bandwidth request to change.
        """

        for id_flow, measurements in flows:
            # Smooth dataset using Savitzky-Golay filter to avoid peak in the bandwidth estimation
            measurements_hat = util.savitzky_golay(np.array(measurements), 51, 3)
            new_bandwidth = sum(measurements_hat)/len(measurements_hat)
            if new_bandwidth < self.reserved_bytes:
                self.current_capacity -= self.flows[id_flow]
                self.flows[id_flow] = 0
            elif new_bandwidth < self.flows[id_flow]:
                self.current_capacity -= self.flows[id_flow]
                self.flows[id_flow] = new_bandwidth
                self.current_capacity += new_bandwidth

        new_bandwidth = min([self.max_capacity - self.current_capacity, self.flows[flow_id]])
        new_bandwidth += self.flows[flow_id]

        self.current_capacity -= self.flows[flow_id]
        self.flows[flow_id] = new_bandwidth
        self.current_capacity += new_bandwidth

    def statistics_request(self, flow_id, max_stat):
        """Abstract method to be implemented by the concrete PolicyManager class.

        Args:
            flow_id (int): The number of the identifier to retrieve
            max_stat (int): Maximum number of list of statistics to retrieve

        Return:
            A list of list os stings with the requested statistics
        """
        pass

    def set_bandwidth(self, flow_id, bandwidth):
        """This method set new bandwidth to the given flow.

        Args:
            flow_id (int): The number of the identifier to retrieve
            bandwidth (int): New minimum bandwidth capacity to be assigned

        Raises:
            AttributeError: If the new bandwidth is bigger than the current free capacity.
        """
        total_bandwidth = bandwidth - self.flows[flow_id]

        if self.max_capacity - self.current_capacity < total_bandwidth:
            raise AttributeError("Bandwidth exceeds current capacity")

        self.flows[flow_id] = bandwidth
        self.current_capacity += total_bandwidth

        # todo notify to flow manager

