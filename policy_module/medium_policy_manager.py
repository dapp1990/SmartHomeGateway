from .interface_policy_manager import InterfacePolicy
import logging as log
from datetime import datetime


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
                         flow_statistics, time_str):
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
            flow_statistics ([(str,[int])]): Statistics of the last active.
            flow_id (int): The flow id which bandwidth request to be changed.
        """

        reassigned_flow_bandwidth = {}

        temp = {}
        total_bandwidth = 0
        for f_id in flow_statistics:

            initial = datetime.strptime(flow_statistics[f_id][0], '%Y-%m-%d '
                                                                  '%H:%M:%S.%f')
            final = datetime.strptime(flow_statistics[f_id][1], '%Y-%m-%d '
                                                                '%H:%M:%S.%f')
            request_time = datetime.strptime(time_str, '%Y-%m-%d %H:%M:%S.%f')

            delta_time = request_time - final
            total_delta = final - initial
            # TODO: must be a clever way to fix this
            if delta_time.total_seconds() < 5 \
                    and 0 < total_delta.total_seconds():
                
                new_bandwidth = \
                    sum([x[0] for x in flow_statistics[f_id][2]])\
                    /total_delta.total_seconds()
            else:
                new_bandwidth = 0
            total_bandwidth += new_bandwidth
            temp[f_id] = new_bandwidth
        log.info("This is the percentage %s", (temp[f_id]/total_bandwidth))

        reassigned_flow_bandwidth[f_id] = \
            (temp[f_id]/total_bandwidth) * self.max_capacity
        log.info("this is the perfectage %s", reassigned_flow_bandwidth[f_id])

        current_capacity = sum(reassigned_flow_bandwidth.values())

        # Todo: new a log to see if there is any warning here!

        if self.max_capacity+self.reserved_bytes < current_capacity:
            log.warning("Capacity overflow max+reserved %s - assigned capacity "
                        "%s",
                        self.max_capacity + self.reserved_bytes,
                        current_capacity)

        return reassigned_flow_bandwidth
