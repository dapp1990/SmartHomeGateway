from queue import Queue
from ryu.base import app_manager
from threading import Thread
import time


class FlowScheduler(app_manager.RyuApp):

    def __init__(self, id_flow, rate, monitor, max_size, *args, **kwargs):

        super(FlowScheduler, self).__init__(*args, **kwargs)

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
        self.waiting_response = False
        self.rate = rate

    def get_rate(self):
        return self.rate

    def add_flow(self, msg_len, datapath, out_format):
        if self.queue.qsize() > self.max_size and not self.waiting_response:
            print("sending burst of {}".format(self.id_flow))
            self.waiting_response = True
            self.monitor.notification(self.monitor.bottleneck_notification,
                                      [self.id_flow])

        self.queue.put((msg_len, datapath, out_format))

    def scheduler(self):
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
