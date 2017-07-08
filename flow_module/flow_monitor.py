from flow_module.scheduler import Scheduler
from queue import Queue
from threading import Thread
import requests

# reason _packet_in_handler is already asyncronous
# https://thenewstack.io/sdn-series-part-iv-ryu-a-rich


class FlowMonitor:
    """Class that behaves as a broker between the input(controller) and output(
    scheduler) of the network flow.

    Monitor also keep a cache mechanisms to avoid as much as possible the
    request to the actual DataBase. It also in charges of the policy requests.
    """
    def __init__(self):
        self.policy_url = "http://localhost:5002"
        self.statistics_url = "http://localhost:5001"

        self.max_size = 10

        self.accept_update = True
        self.outgoing_flows = {}
        self.bandwidths = {}
        self.cache = {}

        self.local_port = 2  # 4294967294

        self.requests = Queue()
        num_threads = 100
        for i in range(num_threads):
            requests_thread = Thread(target=self.process_request)
            requests_thread.daemon = True
            requests_thread.start()

    def notification(self, function, parameters):
        """Function that receives the incoming notifications of inside the
        module.

        This function behaves as a closure creator and add the closure to the
        synchronous queue. Additionally, it avoids to enqueue a
        bottleneck_notification if there is still one in the queue or in
        execution that has not finished.

        Args:
            function (str): name of the function to be executed in the future.
            parameters ([str]): List of parameters of the given function to
            be executed.
        """
        if function == self.bottleneck_notification and not self.accept_update:
            return
        if function == self.bottleneck_notification:
            self.accept_update = False
        self.requests.put((function, parameters))

    def process_request(self):
        """Worker that executes the tasks in the asynchronous queue.
        """
        while True:
            function, parameters = self.requests.get()

            function(*parameters)

            self.requests.task_done()

    def outgoing_notification(self, id_flow, msg_len, datapath, in_port, msg,
                              parser,time):
        """This function processes the outgoing notifications.

        This function  verifies if the given flow is already
        registered by monitor. If that is not the case, it requests to policy
        WebService a new rate, updates current flow rate if needed,
        and creates a new schedule instance. In any case, it saves the action
        in the cache and forwards action to outgoing_scheduler_allocator

        Args:
            id_flow (str): flow id.
            msg_len (int): size of the packet.
            datapath (Datapath): RYU data structure that represents the
            packet of the given flow.
            in_port (int): port in which the packet is going to be delivered.
            msg (object): RYU data structure which encapsulated the
            message from a OVS switch
            parser (object): RYU instance that enables to parse a RYU message
            object.
            time: time in which the packets arrive to the flow module
        """
        if id_flow not in self.outgoing_flows:
            result = self.get_bandwidth(id_flow)
            if isinstance(result, dict):
                for flow in result:
                    self.set_bandwidth(flow, result[flow])
            else:
                self.set_bandwidth(id_flow, float(result))
            self.cache[id_flow] = [time, None, []]
        self.cache[id_flow][1] = time
        self.cache[id_flow][2].append([msg_len,time])

        self.outgoing_scheduler_allocator(id_flow, msg_len, datapath, in_port,
                                          msg, parser)

    def bottleneck_notification(self, id_flow, request_time):
        """This function processes the bottleneck notifications.

        This function request and update action to the policy WebService,
        updates the rates of the current flows and enables to enqueue new
        bottleneck notification.

        Args:
            id_flow (str): flow id.
            request_time: time of the request made by the scheduler
        """
        flow_dict = self.get_updates(id_flow, request_time)
        for id_flow in flow_dict:
            if flow_dict[id_flow] <= 5:
                self.del_bandwidth(id_flow)
            else:
                self.set_bandwidth(id_flow, flow_dict[id_flow])
        self.accept_update = True

    def get_updates(self, id_flow, request_time):
        """This function wraps all the HTTP requires to send a request to the
        policy WebServices.

        Args:
            id_flow (str): flow id.
            request_time: time of the request made by the scheduler

        Returns:
            str, {str,str} or None: the result of the policy webservice which
            each either a single str ot a dictionary. In there is an error a
            None is returned.
        """
        data = {'flow_id': id_flow, 'current_flows': self.bandwidths,
                'cache': self.cache, 'time_request': request_time}
        res = requests.post(self.policy_url + "/update_bandwidths",
                            json=data,
                            headers={'Content-type': 'application/json'})
        if res.status_code == 200:
            return res.json()['response']
        else:
            print("Impossible to update bandwidths, "
                                "status code {}".format(res.status_code))
            return None

    def get_bandwidth(self, id_flow):
        """This function wraps all the HTTP requires to send a request to the
        policy WebServices.

        Args:
            id_flow (str): flow id.
            request_time: time of the request made by the scheduler

        Returns:
            int: the result of the policy webservice or 1660 otherwise
        """
        data = {'flow_id': id_flow, 'current_flows': self.bandwidths}
        res = requests.post(self.policy_url + "/get_bandwidth",
                            json=data,
                            headers={'Content-type': 'application/json'})
        if res.status_code == 200:
            data = res.json()
            return data['response']
        else:
            print("Impossible to assing width, status code {}".format(
                res.status_code))
            return 1660

    def outgoing_scheduler_allocator(self, id_flow, msg_len, datapath, in_port,
                                     msg, parser):
        """This function creates the the packet and forward the message to
        the scheduler.

        Args:
            id_flow (str): flow id.
            msg_len (int): size of the packet.
            datapath (Datapath): RYU data structure that represents the
            packet of the given flow.
            in_port (int): port in which the packet is going to be delivered.
            msg (object): RYU data structure which encapsulated the
            message from a OVS switch
            parser (object): RYU instance that enables to parse a RYU message
            object.
        """
        if in_port == 1:
            # Send out to local port which is connected with the Linux Kernel
            out_port = self.local_port
        else:
            out_port = 1

        # Create the out packet format to be sent out
        actions = [parser.OFPActionOutput(out_port)]
        out_format = parser.OFPPacketOut(datapath=datapath,
                                         buffer_id=msg.buffer_id,
                                         in_port=in_port,
                                         actions=actions,
                                         data=msg.data)

        self.outgoing_flows[id_flow].add_flow(msg_len, datapath, out_format)

    def set_bandwidth(self, id_flow, bandwidth):
        """This function updates the status of the bandwidths and cache.

        Args:
            id_flow (str): flow id.
            bandwidth (int): new rate for the given flow

        """
        self.bandwidths[id_flow] = bandwidth
        if id_flow in self.outgoing_flows:
            self.outgoing_flows[id_flow].set_rate(bandwidth)
        else:
            self.outgoing_flows[id_flow] = Scheduler(id_flow,
                                                     bandwidth,
                                                     self,
                                                     self.max_size)

    def del_bandwidth(self,id_flow):
        """This function delete cache information and forward the info to the
        save_statistics.

        Args:
            id_flow (str): flow id.
        """
        data = self.cache[id_flow][2]

        del self.bandwidths[id_flow]
        del self.outgoing_flows[id_flow]
        del self.cache[id_flow]

        self.save_statistics(id_flow, data)

    def save_statistics(self, id_flow, cache):
        """This function wraps all the HTTP requires to send a request to the
        statistics WebServices.

        Args:
            id_flow (str): flow id.
            cache: cache object of to be saved in the DataBase
        """
        data = {"id_flow": id_flow, "batch": cache}

        res = requests.post(self.statistics_url + "/save_batch_statistics",
                            json=data,
                            headers={'Content-type': 'application/json'})
        if not res.status_code == 200:
            print("Statistics not saved, "
                  "status code {}".format(res.status_code))