from unittest import TestCase
from policy_module.simple_policy_manager import SimplePolicyManager
import numpy as np


class TestSimplePolicyManager(TestCase):

    def test_simple_zero_update_bandwidth(self):
        reserved_bytes = (150 + 16) * 10
        simple_policy_manager = SimplePolicyManager(200000,reserved_bytes)
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

        final_capacity += reserved_bytes * 2
        simple_policy_manager.update_bandwidth(data_set, 0)

        for i in range(1, 10):
            element = simple_policy_manager.__getattribute__("flows")[i]
            self.assertEquals(element, 0)

        current_capacity = simple_policy_manager.__getattribute__("current_capacity")
        self.assertEquals(current_capacity, final_capacity)

    def test_set_bandwidth_more_capacity_low_statistics(self):
        reserved_bytes = (150 + 16) * 10
        simple_policy_manager = SimplePolicyManager(300000,reserved_bytes)
        data_set = []
        final_capacity = 0

        for i in range(10):
            simple_policy_manager.add_flow(i)

        for i in range(0,10):
            simple_policy_manager.set_bandwidth(i, 20000)

        for i in range(1,10):
            temp = np.zeros(20)
            if i:
                for j in range(0,20):
                    temp[j] = 2000
            final_capacity += 2000
            data_set.append([i,temp])

        # The bandwidth of the others is changed due to the statistics

        simple_policy_manager.update_bandwidth(data_set, 0)

        final_capacity += 40000

        for i in range(1, 10):
            element = simple_policy_manager.__getattribute__("flows")[i]
            self.assertAlmostEqual(2000, element)

        current_capacity = simple_policy_manager.__getattribute__("current_capacity")
        self.assertEquals(current_capacity, final_capacity)

    def test_set_bandwidth_more_capacity_high_statistics(self):
        reserved_bytes = (150 + 16) * 10
        simple_policy_manager = SimplePolicyManager(300000, reserved_bytes)
        data_set = []
        final_capacity = 0

        for i in range(10):
            simple_policy_manager.add_flow(i)

        for i in range(0,10):
            simple_policy_manager.set_bandwidth(i, 20000)

        for i in range(1,10):
            temp = np.zeros(20)
            if i:
                for j in range(0,20):
                    temp[j] = 22000
            final_capacity += 20000
            data_set.append([i,temp])

        # The bandwidth of the others is NOT changed, statistics has bigger numbers and according to policies,
        # the bandwidth can only be reduced, not increased
        simple_policy_manager.update_bandwidth(data_set, 0)

        final_capacity += 40000

        for i in range(1, 10):
            element = simple_policy_manager.__getattribute__("flows")[i]
            self.assertAlmostEqual(20000, element)

        current_capacity = simple_policy_manager.__getattribute__("current_capacity")
        self.assertEquals(current_capacity, final_capacity)

    def test_set_bandwidth_set_free_capacity(self):
        reserved_bytes = (150 + 16) * 10
        simple_policy_manager = SimplePolicyManager(18000,reserved_bytes)
        data_set = []
        final_capacity = 0

        for i in range(10):
            simple_policy_manager.add_flow(i)

        for i in range(1, 10):
            temp = np.zeros(20)
            if i:
                for j in range(0, 20):
                    temp[j] = 22000
            final_capacity += 20000
            data_set.append([i, temp])

        # The bandwidth of the others is NOT changed, statistics has bigger numbers and according to policies,
        # the bandwidth can only be reduced, not increased
        simple_policy_manager.update_bandwidth(data_set, 0)

        final_capacity = 18000 - reserved_bytes

        for i in range(1, 10):
            element = simple_policy_manager.__getattribute__("flows")[i]
            self.assertAlmostEqual(reserved_bytes, element)

        current_capacity = simple_policy_manager.__getattribute__("current_capacity")
        self.assertEquals(current_capacity, final_capacity)

