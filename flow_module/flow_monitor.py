from flow_module.flow_scheduler import FlowScheduler
from queue import Queue
from threading import Thread
import requests
#import asyncio
#from aiohttp import ClientSession

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
        self.statistics_url = "http://localhost:5001"

        self.max_size = 5 # after several test 5 looks a good threashold

        self.accept_update = True
        self.outgoing_flows = {}
        self.bandwidths = {}
        self.cache = {}
        #self.loop = asyncio.get_event_loop()

        self.local_port = 2  # 4294967294

        self.requests = Queue()
        num_threads = 50
        for i in range(num_threads):
            requests_thread = Thread(target=self.process_request)
            requests_thread.daemon = True
            requests_thread.start()

    def notification(self, function, parameters):
        #print("Receive a notification {}".format(function))
        if function ==  self.bottleneck_notification and not self.accept_update:
            return
        if function ==  self.bottleneck_notification:
            self.accept_update = False
        self.requests.put((function, parameters))

    def process_request(self):
        while True:
            function, parameters = self.requests.get()

            function(*parameters)

            self.requests.task_done()

    def outgoing_notification(self, id_flow, msg_len, datapath, in_port, msg,
                              parser,time):
        #print("outgoing notification with {}".format(self.outgoing_flows))
        if id_flow not in self.outgoing_flows:
            bandwidth = self.get_bandwidth(id_flow)
            #print("Setting bandwidth to {}".format(bandwidth))
            #bandwidth = 100000
            self.set_bandwidth(id_flow, bandwidth)
            self.cache[id_flow] = [time, None, []]
            #append
        self.cache[id_flow][1] = time
        self.cache[id_flow][2].append([msg_len,time])

        self.set_outgoing_scheduler(id_flow, msg_len, datapath, in_port, msg,
                                    parser)
        #self.save_statistics(id_flow, msg_len, time)

    def bottleneck_notification(self, id_flow, request_time):
        #if id_flow not in self.bandwidths:
        #    return
        print("before self.get_updates {}".format(self.bandwidths))
        flow_dict = self.get_updates(id_flow, request_time)
        #print("result of policy {}".format(flow_dict))
        for id_flow in flow_dict:
            if flow_dict[id_flow] <= 5:
                self.del_bandwidth(id_flow)
            else:
                self.set_bandwidth(id_flow, flow_dict[id_flow])
        self.accept_update = True
        print("after self.get_updates {}".format(self.bandwidths))

    def get_updates(self, id_flow, request_time):
        # TODO[id:1]: maybe it is better to request the bandwidth of every flow
        data = {'flow_id': id_flow, 'current_flows': self.bandwidths,
                'cache': self.cache, 'time_request': request_time}
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
        print("Deleting bandwdths - >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>")
        #loop = asyncio.new_event_loop()
        #data = self.cache[id_flow][2]
        #task = self.loop.create_task(self.fetch_per_request())
        #future = asyncio.ensure_future(self.save_statistics(id_flow, data))

        #self.save_statistics(id_flow, data)

        del self.bandwidths[id_flow]
        del self.outgoing_flows[id_flow]
        del self.cache[id_flow]

        #loop.run_until_complete(future)
        print("FINISH deleting bandwdth->>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>")

    """
    async def save_statistics(self, id_flow, cache):
        url = self.statistics_url + "/save_statistics"
        async with ClientSession() as session:
            for length, time in cache:
                data = {"id_flow": id_flow,
                        "size": length,
                        "time": time}
                task = asyncio.ensure_future(self.fetch(url, session, data))

    async def fetch(self, url, session, data):
        async with session.post(url, json=data) as response:
            return await response.read()

        data = {"id_flow": id_flow,
                "size": length,
                "time": time}
        url = self.statistics_url + "/save_statistics"
        res = requests.post(url,
                            json=data,
                            headers={'Content-type': 'application/json'})



        for length,time in temp:
            data = {"id_flow": id_flow,
                    "size": length,
                    "time": time}
            url = self.statistics_url + "/save_statistics"
            res = requests.post(url,
                                json=data,
                                headers={'Content-type': 'application/json'})
    """
