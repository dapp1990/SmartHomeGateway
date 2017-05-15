from ryu.base import app_manager
from ryu.controller import ofp_event
from ryu.controller.handler import CONFIG_DISPATCHER, MAIN_DISPATCHER
from ryu.controller.handler import set_ev_cls
from ryu.ofproto import ofproto_v1_3
from ryu.lib.packet import packet
from ryu.lib.packet import ethernet
from ryu.lib.packet import ether_types
from ryu.lib import hub
import htb

# Global variables
queue_frames = []  # In theory lists are thread-safe
# rate NOT: 2kbps because it takes 2000000 cycles to storage MTU
# so a single packet with 1556 is delayed ~ 2 seconds

rate = 50000  # bytes/second
capacity = 1  # 32 -> 49792 -> roughly 50000


class QoSManager(app_manager.RyuApp):
    OFP_VERSIONS = [ofproto_v1_3.OFP_VERSION]

    def __init__(self, *args, **kwargs):
        super(QoSManager, self).__init__(*args, **kwargs)
        self.scheduler_thread = hub.spawn(self._TBF_scheduler)

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
        inst = [parser.OFPInstructionActions(ofproto.OFPIT_APPLY_ACTIONS, actions)]

        # Send flow_mod message, store flow on table-miss
        mod = parser.OFPFlowMod(datapath=datapath, priority=1, match=match, instructions=inst)
        datapath.send_msg(mod)

    @set_ev_cls(ofp_event.EventOFPPacketIn, MAIN_DISPATCHER)
    def _packet_in_handler(self, ev):

        # Print whether message is truncated
        if ev.msg.msg_len < ev.msg.total_len:
            self.logger.info("packet truncated!: only %s of %s bytes", ev.msg.msg_len, ev.msg.total_len)

        # Process message
        msg = ev.msg
        datapath = msg.datapath
        ofproto = datapath.ofproto
        parser = datapath.ofproto_parser
        in_port = msg.match['in_port']  # it'll be used for getting ip_address and allocate the correct QoS

        pkt = packet.Packet(msg.data)
        eth = pkt.get_protocols(ethernet.ethernet)[0]

        # No need to forward lldp packet, so they are ignored
        if eth.ethertype == ether_types.ETH_TYPE_LLDP:
            return

        """ Debug """
        dst = eth.dst
        src = eth.src
        dpid = datapath.id

        self.logger.info("packet in %s %s %s %s", dpid, src, dst, in_port)
        """ End debug """

        if in_port == 1:
            # Send out to local port which is connected with the Linux Kernel
            # out_port = 4294967294L
            out_port = 4294967294
        else:
            out_port = 1

        # This is in case we have a buffer on OvS, but it must not due to the configuration of the OvS with OFP_NO_BUFFER
        if msg.buffer_id != ofproto.OFP_NO_BUFFER:
            self.logger.info("A valid buffer was found!: %s", msg.buffer_id)
            # return

        # Create the out package format to be sent
        data = msg.data  # problably not useful
        actions = [parser.OFPActionOutput(out_port)]
        out = parser.OFPPacketOut(datapath=datapath, buffer_id=msg.buffer_id, in_port=in_port, actions=actions,
                                  data=data)

        # Todo: Assign QoS to datapath
        """
        if out_port == 4294967294:
            datapath.send_msg(out)
        else:
            queue_frames.append((ev.msg.msg_len, datapath, out)) #only assign QoS to downlink transmition
        """
        queue_frames.append((ev.msg.msg_len, datapath, out))

    def _fifo_scheduler(self):
        while True:
            if queue_frames:
                msg_len, datapath, out_format = queue_frames.pop()
                datapath.send_msg(out_format)
            # Delay
            hub.sleep(0.001)

    def _TBF_scheduler(self):
        # The limit is given by queue_frames,
        tbf = htb.HTB([capacity], [rate], 1)

        msg_len = 0
        datapath = None
        out_format = None
        consume_package = True

        self.logger.info("TBF scheduler: %s", msg_len)
        while True:
            if queue_frames:
                if consume_package:
                    msg_len, datapath, out_format = queue_frames.pop()
                    consume_package = False

            if not consume_package:
                if tbf.consume(0, msg_len):
                    datapath.send_msg(out_format)
                    consume_package = True
            hub.sleep(0.001)  # a sleep greater than 0.001 does not work properly... a big delay is encountered