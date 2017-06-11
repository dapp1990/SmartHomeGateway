from .interface_policy_manager import InterfacePolicy
import shelve
from uuid import uuid4
import numpy as np
from .util import savitzky_golay

# Todo: add a wrapper that notifies immediately to the flow manager when is
# an update


class SimplePolicyManager(InterfacePolicy):
    """Naive statistics manager to store and retrieve OVS statistics

    This class reserve (MTU * 10) bytes from the max_capacity given to assign
    to every new flow.

    """

    def __init__(self, max_capacity, reserved_bytes):
        self.max_capacity = max_capacity - reserved_bytes
        self.reserved_bytes = reserved_bytes

    def get_bandwidth(self, flow_id, current_flows):
        """ Simple algorithm which assign the minimum amount of bandwidth.

        Args:
            flow_id (str): id of the flow to monitor
        """

        return self.reserved_bytes

    # Todo: add hard constrains (max and min bandwidth rate)
    def update_bandwidth(self, flow_id, flow_current_bandwidth,
                         flow_statistics):
        """Update the bandwidths of the given flows.

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
            flow_current_bandwidth: bandwidth of the current flows.
            flow_statistics ([(str,[int])]): Statistics of the last active
            flows.
            flow_id (int): The flow id which bandwidth request to be changed.
        """

        reassigned_flow_bandwidth = {}

        for f_id, measurements in flow_statistics:
            # Smooth dataset using Savitzky-Golay filter to avoid peak in
            # the bandwidth estimation
            measurements_hat = savitzky_golay(np.array(measurements), 51, 3)
            new_bandwidth = sum(measurements_hat)/len(measurements_hat)

            if new_bandwidth < self.reserved_bytes:
                reassigned_flow_bandwidth[f_id] = 0
            elif new_bandwidth < flow_current_bandwidth[f_id]:
                reassigned_flow_bandwidth[f_id] = new_bandwidth
            else:
                reassigned_flow_bandwidth[f_id] = flow_current_bandwidth[f_id]

        current_capacity = sum(reassigned_flow_bandwidth.values())

        new_bandwidth = min([self.max_capacity - current_capacity,
                             flow_current_bandwidth[flow_id]*2])

        reassigned_flow_bandwidth[flow_id] = new_bandwidth

        return reassigned_flow_bandwidth
