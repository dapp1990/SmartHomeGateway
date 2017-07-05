from .base_policy import InterfacePolicy
import logging as log
from datetime import datetime

# TODO: Make unittest


class MediumPolicyManager(InterfacePolicy):
    """Basic implementation of a Policy engine.

    This class implements a statistics engine. This particular engine
    reserve a given number of bytes to be assigned to new flow in the
    network. This engine is constrained by the maximum capacity of the
    network and ensure that the resources are maximized depending on the
    given statistics.

    Args:
        max_capacity (int): Maximum capacity of the netwrok in terms of bytes
        per second.
        reserved_bytes (int): Reserved bytes which will be assigned as a
        first attempt to a new flow.
        level (int, optional): Level of the logger.
    """

    def __init__(self, max_capacity, reserved_bytes, level=log.INFO):
        log.basicConfig(format='%(''asctime)s - %(levelname)s - %(message)s',
                        filemode='w',
                        level=level)
        log.info("initializing MediumPolicyManager class")

        self.max_capacity = max_capacity - reserved_bytes
        self.reserved_bytes = reserved_bytes

    def get_bandwidth(self, flow_id, current_flows):
        """Function that assigned a rate to a given flow id.

        This function verifies that there is still capacity for the given
        flow and assigns the reserved bytes. In case there is no enough
        space, the function marginalize the bandwidth of the current flows
        and assings a new rate given its percentage in order to allow a
        window of the reserved bytes to be assign to the new flow.

        Args:
            flow_id (str): the id of the new flow.
            current_flows ({str,int}): A dictionary where the keys are the
            ids of all the current flows and the values the rate assigned to
            them.

        Returns:
            dict or int: Either return a dictionary with new rates to all the
            current flows or a single value for the given flow id.
        """
        current_capacity = sum(current_flows.values())

        if self.max_capacity+self.reserved_bytes <= current_capacity:
            log.warning("Full capacity, adjusting bandwidths")
            temp = {}
            for flow in current_flows:
                temp[flow] = (current_flows[flow]/current_capacity)\
                             * self.max_capacity
            temp[flow_id] = self.reserved_bytes
            return temp
        else:
            return self.reserved_bytes

    def update_bandwidth(self, flow_id, flow_current_bandwidth,
                         flow_statistics, time_str):
        """Function that reclculate the rates of the given current flows.

        This function uses the statistics to get an average of the actual flow
        per second of each current flow. Then marginalize the final result to
        obtain percentage and the new rate is calculate multiplying the
        maximum capacity without the reserved bytes and its percentage. This
        allow to never assign more bandwidth which can be handler according
        with the given maximum capacity.

        Args:
            flow_id (str): the id of the new flow.
            flow_current_bandwidth ({str,int}): A dictionary where the keys are
            the ids of all the current flows and the values the rate assigned to
            them.
            flow_statistics ({str,[str,str]}): A dictionary where the keys are
            the ids of all the current flows and the values are a list of two
            elements containg the size and the time in which a packets was
            captured.
            time_str (str): time in which the request was made.

        Returns:
            dict or int: Either return a dictionary with new rates to all the
            current flows or a single value for the given flow id.
        """
        reassigned_flow_bandwidth = {}
        temp_current = flow_current_bandwidth
        temp = {}
        total_bandwidth = 0
        for f_id in flow_statistics:
            del temp_current[f_id]

            initial = datetime.strptime(flow_statistics[f_id][0], '%Y-%m-%d '
                                                                  '%H:%M:%S.%f')
            final = datetime.strptime(flow_statistics[f_id][1], '%Y-%m-%d '
                                                                '%H:%M:%S.%f')
            request_time = datetime.strptime(time_str, '%Y-%m-%d %H:%M:%S.%f')

            delta_time = request_time - final
            total_delta = final - initial

            if delta_time.total_seconds() < 5:
                if 0 == total_delta.total_seconds():
                     new_bandwidth = flow_statistics[f_id][2][0][0]
                else:
                     new_bandwidth = \
                            sum([x[0] for x in flow_statistics[f_id][2]])\
                            /total_delta.total_seconds()
            else:
                new_bandwidth = 0
            total_bandwidth += new_bandwidth
            temp[f_id] = new_bandwidth

        for f_id in temp:
            reassigned_flow_bandwidth[f_id] = \
                (temp[f_id]/total_bandwidth) * self.max_capacity
            log.info("The bandwidth assign  of %s is %s",
                     f_id, reassigned_flow_bandwidth[f_id])

        current_capacity = sum(reassigned_flow_bandwidth.values())

        if self.max_capacity+self.reserved_bytes < current_capacity:
            log.warning("Capacity overflow max+reserved %s - assigned capacity "
                        "%s",
                        self.max_capacity + self.reserved_bytes,
                        current_capacity)
        # Sanity check, all flows that are not in statistics implies no
        # activity, so assign a bandwidth of 0
        for id_flow in temp_current:
            reassigned_flow_bandwidth[id_flow] = 0

        return reassigned_flow_bandwidth
