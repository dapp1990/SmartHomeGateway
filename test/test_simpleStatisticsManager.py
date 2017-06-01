from statistics_module.simple_statistics_manager import SimpleStatisticsStatistics
from unittest import TestCase
import os


class TestSimpleStatisticsManager(TestCase):

    def setUp(self):
        self.simple_manager = SimpleStatisticsStatistics('test_database')

    def test_naive_retrieve_case(self):

        results = self.simple_manager.save_statistics(['192.168.19.20', '192.168.19.77', '150', '1233445664'])

        self.assertEquals(results, True)

        for i in range(100):
            results = self.simple_manager.save_statistics(['192.168.19.20', '192.168.19.77', '150', '1233445664'])

        self.assertEquals(results, True)

        results = self.simple_manager.get_statistics('192.168.19.20192.168.19.77', 10)

        self.assertEquals(10, len(results))

    def test_first_retrieve_case(self):

        for i in range(3):
            self.simple_manager.save_statistics(['192.168.19.20', '192.168.19.77', '150', '1233445664'])

        results = self.simple_manager.get_statistics('192.168.19.20192.168.19.77', 10)

        self.assertEquals(3, len(results))


    def test_second_retrieve_case(self):

        for i in range(100):
            self.simple_manager.save_statistics(['192.168.19.20', '192.168.19.77', '150', '1233445664'])

        results = self.simple_manager.get_statistics('192.168.19.20192.168.19.77', 100)

        self.assertEquals(50, len(results))

    def test_second_retrieve_case(self):

        for i in range(100):
            self.simple_manager.save_statistics(['192.168.19.20', '192.168.19.77', i, '1233445664'])

        results = self.simple_manager.get_statistics('192.168.19.20192.168.19.77', 100)

        for i in range(50):
            self.assertEquals(99-i, results[i])

    def tearDown(self):
        os.unlink('test_database.db')
        self.simple_manager = None
