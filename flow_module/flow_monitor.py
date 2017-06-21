from flow_module.flow_scheduler import FlowScheduler
from queue import Queue
from threading import Thread
import requests
import json

# reason _packet_in_handler is already asyncronous
# https://thenewstack.io/sdn-series-part-iv-ryu-a-rich


class FlowMonitor:
    """ In order to have quick responses, two queue where implement. One for
    the outgoing request and one for the fire bottleneck requests
    """

    def __init__(self):
        self.policy_url = "http://localhost:5002"

        self.max_size = 100

        self.outgoing_flows = {}
        self.bandwidths = {}

        self.local_port = 2  # 4294967294

        self.outgoing_queue = Queue()
        self.outgoing_thread = Thread(target=self.send_message)
        self.outgoing_thread.daemon = True
        self.outgoing_thread.start()

        self.burst_queue = Queue()
        self.burst_thread = Thread(target=self.send_burst_request)
        self.burst_thread.daemon = True
        self.burst_thread.start()

    def process_burst(self, id_flow):
        self.burst_queue.put(id_flow)

    def process_message(self, id_flow, msg_len, datapath, in_port, msg, parser):
        self.outgoing_queue.put(
            [id_flow, msg_len, datapath, in_port, msg, parser])

    def send_burst_request(self):
        while True:
            id_flow = self.burst_queue.get()

            self.update_bandwidths(id_flow)

            self.burst_queue.task_done()

    def send_message(self):
        while True:
            id_flow, msg_len, datapath, in_port, msg, parser = \
                self.outgoing_queue.get()

            if id_flow not in self.outgoing_flows:
                bandwidth = self.get_bandwidth(id_flow)
                print("Setting bandwidht to {}".format(bandwidth))
                # bandwidth = 100000
                self.set_bandwidth(id_flow, bandwidth)

            self.set_outgoing_scheduler(id_flow, msg_len, datapath, in_port, msg,
                                        parser)
            self.outgoing_queue.task_done()

    def get_bandwidth(self, id_flow):
        data = {'flow_id': id_flow, 'current_flows': self.bandwidths}
        res = requests.post(self.policy_url + "/get_bandwidth",
                            json=json.dumps(data),
                            headers={'Content-type': 'application/json'})
        data = res.json()
        return float(data['response'])

    def update_bandwidths(self, id_flow):
        print("update_bandwidths... ")
        # TODO[id:1]: maybe it is better to request the bandwidth of every flow
        data = {'flow_id': id_flow, 'current_flows': self.bandwidths}
        res = requests.post(self.policy_url + "/update_bandwidths",
                            json=json.dumps(data),
                            headers={'Content-type': 'application/json'})
        #TODO: what happen if response is not 2000
        if res.status_code == 200:
            flow_dict = res.json()['response']
            for id_flow in flow_dict:
                self.bandwidths[id_flow] = flow_dict[id_flow]
                self.outgoing_flows[id_flow].set_rate(flow_dict[id_flow])


    #TODO[id:1]: maybe it is better to request the bandwidth of every flow
    # scheduler and not make this cache here
    def set_bandwidth(self,id_flow, bandwidth):
        self.outgoing_flows[id_flow] = bandwidth
        self.outgoing_flows[id_flow] = FlowScheduler(id_flow,
                                                     bandwidth,
                                                     self,
                                                     self.max_size)

    def set_outgoing_scheduler(self, id_flow, msg_len, datapath, in_port,
                               msg, parser):
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
