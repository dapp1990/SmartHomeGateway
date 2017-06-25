from .interface_policy_manager import InterfacePolicy
import logging as log
import numpy as np
from .util import savitzky_golay

# TODO: Make unittest


class MediumPolicyManager(InterfacePolicy):
    """Naive statistics manager to store and retrieve OVS statistics

    This class reserve (MTU * 10) bytes from the max_capacity given to assign
    to every new flow.

    """

    def __init__(self, max_capacity, reserved_bytes, level=log.INFO):
        log.basicConfig(#filename='SimplePolicyManager.log',
                        format='%(''asctime)s - %(levelname)s - %(message)s',
                        filemode='w',
                        level=level)
        log.info("initializing MediumPolicyManager class")

        self.max_capacity = max_capacity - reserved_bytes
        self.reserved_bytes = reserved_bytes

    def get_bandwidth(self, flow_id, current_flows):
        """ Simple algorithm which assign the minimum amount of bandwidth.

        Args:
            flow_id (str): id of the flow to monitor
        """

        current_capacity = sum(current_flows.values())

        if self.max_capacity+self.reserved_bytes <= current_capacity:
            log.warning("Impossible to assign bandwidth, current capacity "
                        "is larger than max_capacity+reserved_capacity")
            return 0

        return self.reserved_bytes

    # Todo: add hard constrains (max and min bandwidth rate)
    def update_bandwidth(self, flow_id, flow_current_bandwidth,
                         flow_statistics, time_lapse):
        """Update the bandwidths of the given flows.

        NOTE: Actually the constrain new_bandwidth < self.reserved_bytes then 0
        is too restrictive. You must fin a better thread off with this
        approach!

        Look over all the given flows and their statistics. Find inactive
        flows. Assign a bandwidth of zero to inactive flows and reduce the
        capacity of the flows if its current bandwidth is greater than the
        actual bandwidth, given by statistics.

        Inactive flow is a flow that, according with the statistics,
        has a bandwidth smaller than the *RESERVED_BYTES*.

        Recalculate current capacity and assigns the smallest value given by
        double bandwidth of the given flow, the available bandwidth of the
        network or the maximum bandwidth rate assigned (in case of hard
        constraint).

        If the available capacity is zero, the bandwidth of the given flow_id
        is not changed.

        Args:
            flow_current_bandwidth: bandwidth of the current flows WITH
            flow_id.
            flow_statistics ([(str,[int])]): Statistics of the last active
            flows without flow_id.
            flow_id (int): The flow id which bandwidth request to be changed.
        """

        reassigned_flow_bandwidth = {}

        for f_id in flow_statistics:
            # Smooth dataset using Savitzky-Golay filter to avoid peak in
            # the bandwidth estimation
            if flow_statistics[f_id]:
                measurements_hat = \
                    savitzky_golay(np.array(flow_statistics[f_id]), 51, 3)
                new_bandwidth = sum(measurements_hat)/time_lapse
            else:
                new_bandwidth = 0

            #if new_bandwidth < self.reserved_bytes:
                #reassigned_flow_bandwidth[f_id] = 0
            # TODO: Even wheter here I can update all the bandwidths according
            # with
            # the global view !
            if new_bandwidth < flow_current_bandwidth[f_id]:
                reassigned_flow_bandwidth[f_id] = new_bandwidth
            else:
                reassigned_flow_bandwidth[f_id] = flow_current_bandwidth[f_id]

        current_capacity = sum(reassigned_flow_bandwidth.values())

        # Todo: new a log to see if there is any warning here!
        available_bandwidth = self.max_capacity - current_capacity
        if available_bandwidth <= 0:
            log.warning("No more bandwidth available for %s", flow_id)
            new_bandwidth = 0
        else:
            new_bandwidth = min([available_bandwidth,
                                 flow_current_bandwidth[flow_id]])

        reassigned_flow_bandwidth[flow_id] = \
            flow_current_bandwidth[flow_id] + new_bandwidth

        current_capacity = sum(reassigned_flow_bandwidth.values())

        if self.max_capacity+self.reserved_bytes < current_capacity:
            log.warning("Capacity overflow max+reserved %s - assigned capacity "
                        "%s",
                        self.max_capacity + self.reserved_bytes,
                        current_capacity)

        return reassigned_flow_bandwidth
