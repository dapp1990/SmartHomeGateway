from statistics_manager.simple_statistics_manager import SimpleStatisticsManager
from unittest import TestCase


class TestSimpleStatisticsManager(TestCase):

    def test_save_statistics(self):

        results = SimpleStatisticsManager().save_statistics("vfvkntlkntkl")

        self.assertEquals(results, True)
