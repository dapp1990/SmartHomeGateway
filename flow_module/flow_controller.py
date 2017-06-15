from ryu.base import app_manager
from ryu.controller import ofp_event
from ryu.controller.handler import CONFIG_DISPATCHER, MAIN_DISPATCHER
from ryu.controller.handler import set_ev_cls
from ryu.ofproto import ofproto_v1_3
from ryu.lib.packet import packet
from ryu.lib.packet import ethernet
from ryu.lib.packet import ether_types
from datetime import datetime
from ryu.lib import hub
from flow_module.outgoing_flow_scheduler import OutgoingFlowScheduler
import requests
import json


# why _packet_in_handler is already asyncronous
# https://thenewstack.io/sdn-series-part-iv-ryu-a-rich


class FlowController(app_manager.RyuApp):
    OFP_VERSIONS = [ofproto_v1_3.OFP_VERSION]

    def __init__(self, *args, **kwargs):
        super(FlowController, self).__init__(*args, **kwargs)
        self.policy_url = "http://localhost:5002"
        self.statistics_url = "http://localhost:5001"
        self.outgoing_flows = {}
        self.bandwidths = {}
        self.local_port = 2#4294967294

        self.monitor_thread = hub.spawn(self._flow_monitor)


    @set_ev_cls(ofp_event.EventOFPSwitchFeatures, CONFIG_DISPATCHER)
    def switch_features_handler(self, ev):
        self.logger.info("table-miss configuration")
        datapath = ev.msg.datapath
        ofproto = datapath.ofproto
        parser = datapath.ofproto_parser

        # Install table-miss flow entry

        # Match all the incoming datapaths to the OvS
        match = parser.OFPMatch()

        # OFPActionOutput(port, max_len=65509, type_=None, len_=None)
        # OFPP_CONTROLLER indicates to send to controller
        # OFPCML_NO_BUFFER maximun len, all packets send to controller
        actions = [parser.OFPActionOutput(ofproto.OFPP_CONTROLLER,
                                          ofproto.OFPCML_NO_BUFFER)]

        # Construct flow_mod message
        # OFPIT_APPLY_ACTIONS erase previous actions and add new actions
        inst = [parser.OFPInstructionActions(ofproto.OFPIT_APPLY_ACTIONS,
                                             actions)]

        # Send flow_mod message, store flow on table-miss
        mod = parser.OFPFlowMod(datapath=datapath,
                                priority=1,
                                match=match,
                                instructions=inst)
        datapath.send_msg(mod)

    @set_ev_cls(ofp_event.EventOFPPacketIn, MAIN_DISPATCHER)
    async def _packet_in_handler(self, ev):

        msg = ev.msg
        pkt = packet.Packet(msg.data)
        eth = pkt.get_protocols(ethernet.ethernet)[0]

        # No need to forward lldp packet, so they are ignored
        if eth.ethertype == ether_types.ETH_TYPE_LLDP:
            return

        # Print whether message is truncated
        if ev.msg.msg_len < ev.msg.total_len:
            self.logger.info("packet truncated!: only %s of %s bytes",
                             ev.msg.msg_len, ev.msg.total_len)

        # Process message
        datapath = msg.datapath
        parser = datapath.ofproto_parser
        in_port = msg.match['in_port']
        dst = eth.dst
        src = eth.src
        id_flow = str(eth.dst) + str(eth.src)

        """ Debug """
        dpid = datapath.id
        self.logger.info("packet in %s %s %s %s", dpid, src, dst, in_port)
        """ End debug"""

        if id_flow not in self.outgoing_flows:
            # FIXME: be sure that this syncronous call is working correctly
            # with the asyn method packet_in
            response = await self.get_bandwidth(id_flow)
            self.set_bandwidth(id_flow, int(response['response']))

        self.set_outgoing_scheduler(id_flow,
                                    ev.msg.total_len,
                                    datapath,
                                    in_port,
                                    msg,
                                    parser)

        #FIXME: create a new asyn queue to handle the saving statistics request
        await self.save_statistics(dst, ev, src)

    async def save_statistics(self, dst, ev, src):
        now_str = str(datetime.now())
        data = {"src": src,
                "dst": dst,
                "size": ev.msg.total_len,
                "time": now_str}
        res = requests.post(self.statistics_url + "/save_statistics",
                            json=data,
                            headers={'Content-type': 'application/json'})

    async def get_bandwidth(self, id_flow):
        data = {'flow_id': id_flow, 'current_flows': self.bandwidths}
        res = requests.post(self.policy_url + "/get_bandwidth",
                            json=json.dumps(data),
                            headers={'Content-type': 'application/json'})
        response = res.json()
        return response

    def set_bandwidth(self,id_flow, bandwidth):
        self.outgoing_flows[id_flow] = bandwidth
        self.outgoing_flows[id_flow] = OutgoingFlowScheduler(bandwidth)

    def set_outgoing_scheduler(self, id_flow, msg_len, datapath, in_port,
                               msg, parser):
        if in_port == 1:
            # Send out to local port which is connected with the Linux Kernel
            out_port = self.local_port
        else:
            out_port = 1

        # Create the out paket format to be sent out
        actions = [parser.OFPActionOutput(out_port)]
        out_format = parser.OFPPacketOut(datapath=datapath,
                                         buffer_id=msg.buffer_id,
                                         in_port=in_port,
                                         actions=actions,
                                         data=msg.data)

        self.outgoing_flows[id_flow].add_flow(msg_len, datapath, out_format)

    def _monitor(self):
        while True:
            for dp in self.datapaths.values():
                self._request_stats(dp)
            hub.sleep(10)
