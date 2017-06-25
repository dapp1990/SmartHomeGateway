from flow_module.flow_scheduler import FlowScheduler
from queue import Queue
from threading import Thread
import requests
import json

# reason _packet_in_handler is already asyncronous
# https://thenewstack.io/sdn-series-part-iv-ryu-a-rich


class FlowMonitor:
    """ In order to have quick responses, two queue where implement. One for
    the outgoing request and one for the fire bottleneck requests.

    Monitor will only store one update_bandwidth request. after it is
    processed, then it is possible to accept anothe update_bandwidth request.

    this is for later, let's try FIFO first
    Using priority queue we ensure than get_bandwidth request are more
    important than bottleneck_alerts.
    """

    def __init__(self):
        self.policy_url = "http://localhost:5002"

        self.max_size = 10

        self.accept_update = True
        self.outgoing_flows = {}
        self.bandwidths = {}

        self.local_port = 2  # 4294967294

        self.requests = Queue()

        self.requests_thread = Thread(target=self.process_request)
        self.requests_thread.daemon = True
        self.requests_thread.start()

    def notification(self, function, parameters):
        #print("Receive a notification {}".format(function))
        self.requests.put((function, parameters))

    def process_request(self):
        while True:
            function, parameters = self.requests.get()

            function(*parameters)

            self.requests.task_done()

    def outgoing_notification(self, id_flow, msg_len, datapath, in_port, msg,
                              parser):
        #print("outgoing notification with {}".format(self.outgoing_flows))
        if id_flow not in self.outgoing_flows:
            bandwidth = self.get_bandwidth(id_flow)
            #print("Setting bandwidth to {}".format(bandwidth))
            #bandwidth = 100000
            self.set_bandwidth(id_flow, bandwidth)

        self.set_outgoing_scheduler(id_flow, msg_len, datapath, in_port, msg,
                                    parser)

    def bottleneck_notification(self, id_flow):
        if id_flow not in self.bandwidths:
            return
        print("before self.get_updates {}".format(self.bandwidths))
        flow_dict = self.get_updates(id_flow)
        #FIXME: seems that even the receiver is delete!
        print("result of policy {}".format(flow_dict))
        for id_flow in flow_dict:
            #TODO: maybe it is better to make it variable
            if flow_dict[id_flow] <= 5:
                self.del_bandwidth(id_flow)
            else:
                self.set_bandwidth(id_flow, flow_dict[id_flow])
        print("after self.get_updates {}".format(self.bandwidths))

    def get_updates(self, id_flow):
        #print("update_bandwidths with id {}".format(id_flow))
        #print("content of bandwidths {}".format(id_flow))
        # TODO[id:1]: maybe it is better to request the bandwidth of every flow
        data = {'flow_id': id_flow, 'current_flows': self.bandwidths}
        res = requests.post(self.policy_url + "/update_bandwidths",
                            json=data,
                            headers={'Content-type': 'application/json'})
        # TODO: what happen if response is not 2000
        if res.status_code == 200:
            return res.json()['response']
        else:
            print("Impossible to update bandwidths, "
                                "status code {}".format(res.status_code))
            return None

    def get_bandwidth(self, id_flow):
        print("getting bandwidth {}".format(id_flow))
        data = {'flow_id': id_flow, 'current_flows': self.bandwidths}
        res = requests.post(self.policy_url + "/get_bandwidth",
                            json=data,
                            headers={'Content-type': 'application/json'})
        if res.status_code == 200:
            data = res.json()
            return float(data['response'])
        else:
            print("Impossible to assing width, "
                                "status code {}".format(res.status_code))
            return -1

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

    #TODO[id:1]: maybe it is better to request the bandwidth of every flow
    # scheduler and not make this cache here
    def set_bandwidth(self,id_flow, bandwidth):
        self.bandwidths[id_flow] = bandwidth
        if id_flow in self.outgoing_flows:
            self.outgoing_flows[id_flow].set_rate(bandwidth)
        else:
            self.outgoing_flows[id_flow] = FlowScheduler(id_flow,
                                                         bandwidth,
                                                         self,
                                                         self.max_size)

    def del_bandwidth(self,id_flow):
        #TODO: be sure that the flow_scheduler is really dead, that a thread
        # is not just appearing.
        # FIXME: if you set to zero only, it will be like that for ever!!!
        # it must be prunning somehow. Solution is controlling update
        # parameters
        del self.bandwidths[id_flow]
        del self.outgoing_flows[id_flow]
        print("after deliting bandwidths {}".format(self.bandwidths))
        print("after deliting outgoiing {}".format(self.outgoing_flows))
