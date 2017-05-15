#Based on https://pypi.python.org/pypi/token-bucket/0.2.0

import time

class HTB():

    MTU = 1500 + 56  # IEEE802.3 specifies a MTU of 1500 plus overhead generated by TCP protocol

    # HTB on Linux has no different bucket capacities, all the buckkets used same capacity given by the root
    def __init__(self,capacities,rates,num_buckets):
        self._buckets = {}
        for i in range(num_buckets):
            self._buckets[i] = [0, time.time(), rates[i], capacities[i] * self.MTU]

    def update_current_tokens(self, bucket):
        now = time.time()
        new_tokents = min(self._buckets[bucket][3], ((now - self._buckets[bucket][1]) * self._buckets[bucket][2]) +
                        self._buckets[bucket][0])
        self._buckets[bucket][0] = new_tokents

    def consume(self, bucket, num_tokens):
        self.update_current_tokens(bucket)
        if self._buckets[bucket][0] < num_tokens:
            return False

        self._buckets[bucket][0] -= num_tokens
        return True