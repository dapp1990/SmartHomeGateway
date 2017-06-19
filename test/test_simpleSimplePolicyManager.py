from unittest import TestCase
from policy_module.simple_policy_manager import SimplePolicyManager
import numpy as np


class TestSimplePolicyManager(TestCase):

    def test_simple_zero_update_bandwidth(self):
        reserved_bytes = (150 + 16) * 10
        simple_policy_manager = SimplePolicyManager(200000,reserved_bytes)
        flow_statistics = {}
        flow_bandwidths = {}

        for i in range(10):
            flow_bandwidths[i] = \
                simple_policy_manager.get_bandwidth(i, flow_bandwidths)

        for i in range(1,10):
            temp = np.ones(20)
            for j in range(20):
                if j%2 == 0: temp[j] = 0
            flow_statistics[i] = temp.tolist()

        update_result = \
            simple_policy_manager.update_bandwidth(0, flow_bandwidths,
                                                   flow_statistics)

        for i in range(1, 10):
            element = update_result[i]
            self.assertEquals(element, 0)

    def test_set_bandwidth_more_capacity_low_statistics(self):
        reserved_bytes = (150 + 16) * 10
        simple_policy_manager = SimplePolicyManager(300000, reserved_bytes)
        flow_statistics = {}
        flow_bandwidths = {}

        for i in range(10):
            flow_bandwidths[i] = \
                simple_policy_manager.get_bandwidth(i, flow_bandwidths)

        for i in range(0, 10):
            flow_bandwidths[i] = 20000

        for i in range(1,10):
            temp = np.zeros(20)
            if i:
                for j in range(0,20):
                    temp[j] = 2000

            flow_statistics[i] = temp.tolist()

        # The bandwidth of the others is changed due to the statistics

        update_result = simple_policy_manager.update_bandwidth(0,
                                                               flow_bandwidths,
                                                               flow_statistics)

        for i in range(1, 10):
            element = update_result[i]
            self.assertAlmostEqual(2000, element)

    def test_set_bandwidth_more_capacity_high_statistics(self):
        reserved_bytes = (150 + 16) * 10
        simple_policy_manager = SimplePolicyManager(300000, reserved_bytes)
        flow_statistics = {}
        flow_bandwidths = {}

        for i in range(10):
            flow_bandwidths[i] = \
                simple_policy_manager.get_bandwidth(i, flow_bandwidths)

        for i in range(0, 10):
            flow_bandwidths[i] = 20000

        for i in range(1,10):
            temp = np.zeros(20)
            if i:
                for j in range(0,20):
                    temp[j] = 22000
            flow_statistics[i] = temp.tolist()

        # The bandwidth of the others is NOT changed, statistics has bigger
        # numbers and according to policies, the bandwidth can only be
        # reduced, not increased

        update_result = \
            simple_policy_manager.update_bandwidth(0, flow_bandwidths,
                                                   flow_statistics)

        for i in range(1, 10):
            element = update_result[i]
            self.assertAlmostEqual(20000, element)

    def test_set_bandwidth_set_free_capacity(self):
        reserved_bytes = (150 + 16) * 10
        simple_policy_manager = SimplePolicyManager(18000,reserved_bytes)
        flow_statistics = {}
        flow_bandwidths = {}

        for i in range(10):
            flow_bandwidths[i] = \
                simple_policy_manager.get_bandwidth(i, flow_bandwidths)

        for i in range(1, 10):
            temp = np.zeros(20)
            if i:
                for j in range(0, 20):
                    temp[j] = 22000

            flow_statistics[i] = temp.tolist()

        # The bandwidth of the others is NOT changed, statistics has bigger
        # numbers and according to policies, the bandwidth can only be
        # reduced, not increased
        update_result = \
            simple_policy_manager.update_bandwidth(0, flow_bandwidths,
                                                   flow_statistics)

        for i in range(1, 10):
            element = update_result[i]
            self.assertAlmostEqual(reserved_bytes, element)

        capacity = sum(update_result.values())
        self.assertEquals(capacity, 18000)
