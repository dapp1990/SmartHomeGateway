from multiprocessing import Queue
from ryu.base import app_manager
from threading import Thread
import time


class OutgoingFlowScheduler(app_manager.RyuApp):

    def __init__(self, rate,  *args, **kwargs):

        super(OutgoingFlowScheduler, self).__init__(*args, **kwargs)

        self.rate = rate
        self.time_checkpoint = time.time()
        self.queue = Queue()
        self.thread = Thread(target=self.scheduler)
        self.thread.daemon = True
        self.thread.start()

    def set_rate(self, rate):
        self.rate = rate

    def get_rate(self):
        return self.rate

    def add_flow(self, msg_len, datapath, out_format):
        self.queue.put(msg_len, datapath, out_format)

    def scheduler(self):
        while True:
            msg_len, datapath, out_format = self.queue.get()
            now = time.time()

            new_tokens = ((now - self.time_checkpoint) * self.rate)
            self.time_checkpoint = now
            missing_tokens = msg_len - new_tokens

            if missing_tokens > 0:
                self.logger.info("waiting 1...")
                time.sleep(missing_tokens / self.rate)  # rate here!
                datapath.send_msg(out_format)

            self.queue.task_done()
