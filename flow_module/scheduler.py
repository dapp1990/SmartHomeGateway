from queue import Queue
from ryu.base import app_manager
from threading import Thread
import time
from datetime import datetime


class Scheduler(app_manager.RyuApp):
    """Class that ensures the correct timing to be dispatched in the network.

    This class uses a synchronous queue with a single worker in order to keep
    flow of the data consistent to the rate flow.

    Args:
        id_flow (str): flow id of to be scheduled.
        rate (int): rate of the flow to be kept.
        monitor (int): reference to the monitor that manages this scheduler
        instance.
        max_size (int): threshold use to notify to the monitor that there
        is a bottleneck.

    Attributes:
        rate (int): the rate assinged to this scheduler
    """
    def __init__(self, id_flow, rate, monitor, max_size, *args, **kwargs):

        super(Scheduler, self).__init__(*args, **kwargs)

        self.monitor = monitor
        self.waiting_response = False
        self.max_size = max_size
        self.id_flow = id_flow
        self.rate = rate

        self.time_checkpoint = time.time()
        self.queue = Queue()

        self.thread = Thread(target=self.scheduler)
        self.thread.daemon = True
        self.thread.start()

    def set_rate(self, rate):
        """Function that update the attribute rate

        Args:
            rate (int): new rate to be assign to this scheduler.
        """
        self.waiting_response = False
        self.rate = rate

    def get_rate(self):
        return self.rate

    def add_flow(self, msg_len, datapath, out_format):
        """Function that adds a new closure to the synchronous queue.

        This function verifies if the threshold is reached and it was not
        notified before to the monitor. If that is the case, scheduler
        notifies monitor and adds the packets to the queue, otherwise the
        this functions only add the packet to the flow.

        Args:
            msg_len (int): Length of the packet.
            datapath (Datapath): RYU data structure that represents the
            packet of the given flow.
            out_format (OFPPacketOut): RYU data structure that represents the
            correct format of a outgoing packet.
        """
        if self.queue.qsize() > self.max_size and not self.waiting_response:
            now_str = str(datetime.now())
            #print("sending burst of {}".format(self.id_flow))
            self.waiting_response = True
            self.monitor.notification(self.monitor.bottleneck_notification,
                                      [self.id_flow, now_str])

        self.queue.put((msg_len, datapath, out_format))

    def scheduler(self):
        """Worker that execut the scheduling mechanisms.

        This function validates if the scheduler has enough amount of
        tokens, if there are not enough tokens the workers waits the N
        amount of miliseconds to restored the capacity and send the packet to
        the OVS controller, otherwise the packet is send and the tokens are
        subtracted.
        """
        while True:
            msg_len, datapath, out_format = self.queue.get()
            now = time.time()
            #print("checkpoint: {}".format(self.time_checkpoint))
            #print("now: {}".format(now))
            new_tokens = ((now - self.time_checkpoint) * self.rate)
            self.time_checkpoint = now
            missing_tokens = msg_len - new_tokens
            #print("rate {}".format(self.rate))
            #print("new_tokens {}".format(new_tokens))
            #print("missing_tokens {}".format(missing_tokens))
            if missing_tokens > 0:
                #print("waiting {}".format(missing_tokens / self.rate))
                time.sleep(missing_tokens / self.rate)  # rate here!

            datapath.send_msg(out_format)

            self.queue.task_done()
