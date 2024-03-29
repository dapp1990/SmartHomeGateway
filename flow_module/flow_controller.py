#!/usr/bin/python3

from ryu.base import app_manager
from ryu.controller import ofp_event
from ryu.controller.handler import CONFIG_DISPATCHER, MAIN_DISPATCHER
from ryu.controller.handler import set_ev_cls
from ryu.ofproto import ofproto_v1_3
from ryu.lib.packet import packet
from ryu.lib.packet import ethernet
from ryu.lib.packet import ether_types
from datetime import datetime
from flow_module.flow_monitor import FlowMonitor


# reason _packet_in_handler is already asyncronous
# https://thenewstack.io/sdn-series-part-iv-ryu-a-rich

class FlowController(app_manager.RyuApp):
    OFP_VERSIONS = [ofproto_v1_3.OFP_VERSION]

    def __init__(self, *args, **kwargs):
        super(FlowController, self).__init__(*args, **kwargs) 

        self.logger.info("Initializing FlowMonitor")
        self.monitor = FlowMonitor()

        self.logger.info("Initializing Queues")

        self.logger.info("Finishing ryu app")

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
    def _packet_in_handler(self, ev):
        now_str = str(datetime.now())
        msg = ev.msg
        pkt = packet.Packet(msg.data)
        eth = pkt.get_protocols(ethernet.ethernet)[0]

        # No need to forward lldp packets, so they are ignored
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
        # each flow uplink and downlink are individuals
        id_flow = str(eth.src) + str(eth.dst)
        # each uplink and downlink is one flow
        #if in_port == 1:
        #    id_flow = str(eth.src) + str(eth.dst)
        #else:
        #    id_flow = str(eth.dst) + str(eth.src)

        """ Debug """
        #dpid = datapath.id
        #self.logger.info("packet in %s %s %s %s", dpid, src, dst, in_port)
        """ End debug"""

        parameters = [id_flow, ev.msg.total_len, datapath, in_port, msg,
                      parser, now_str]

        self.monitor.notification(self.monitor.outgoing_notification,
                                  parameters)
