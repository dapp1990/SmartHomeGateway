from unittest import TestCase
from policy_module.simple_policy_manager import SimplePolicyManager
import numpy as np


class TestSimplePolicyManager(TestCase):

    def test_simple_zero_update_bandwidth(self):
        simple_policy_manager = SimplePolicyManager(200000)
        data_set = []
        avg_data_set = dict()
        final_capacity = 0

        for i in range(10):
            simple_policy_manager.add_flow(i)

        for i in range(1,10):
            temp = np.ones(20)
            for j in range(20):
                if j%2 == 0: temp[j] = 0
            avg_data_set[i] = np.mean(temp)
            data_set.append([i,temp])

        final_capacity += (simple_policy_manager.__getattribute__("RESERVED_BYTES") * 2)
        simple_policy_manager.update_bandwidth(data_set, 0)

        for i in range(1, 10):
            element = simple_policy_manager.__getattribute__("flows")[i]
            self.assertEquals(element, 0)

        current_capacity = simple_policy_manager.__getattribute__("current_capacity")
        self.assertEquals(current_capacity, final_capacity)

    def test_update_bandwidth_less_capacity(self):
        simple_policy_manager = SimplePolicyManager(200000)
        data_set = []
        avg_data_set = dict()
        final_capacity = 0
        reserved_bytes = simple_policy_manager.__getattribute__("RESERVED_BYTES")

        for i in range(10):
            simple_policy_manager.add_flow(i)

        for i in range(1,10):
            temp = np.zeros(20)
            if i%2:
                for j in range(0,20):
                    if j%2 == 0: temp[j] = reserved_bytes/2
                    else: temp[j] = 0
            avg_data_set[i] = np.mean(temp)
            data_set.append([i,temp])

        final_capacity += simple_policy_manager.__getattribute__("RESERVED_BYTES") * 2
        simple_policy_manager.update_bandwidth(data_set, 0)

        for i in range(1, 10):
            element = simple_policy_manager.__getattribute__("flows")[i]
            self.assertEquals(element, 0)

        current_capacity = simple_policy_manager.__getattribute__("current_capacity")
        self.assertEquals(current_capacity, final_capacity)
