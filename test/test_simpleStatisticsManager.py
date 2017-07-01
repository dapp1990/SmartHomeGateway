from statistics_module.simple_statistics_manager import SimpleStatisticsManager
from unittest import TestCase
from datetime import datetime, timedelta
import os
import time


class TestSimpleStatisticsManager(TestCase):

    def setUp(self):
        self.simple_manager = SimpleStatisticsManager('test_database.json')

    def test_get_nothing(self):
        to_time = datetime.now()
        from_time = to_time - timedelta(seconds=2)

        results = self.simple_manager.get_statistics(
            '192.168.19.20192.168.19.77', 10, str(from_time), str(to_time))

        self.assertEquals(0, len(results))

    def test_naive_retrieve_case(self):

        results = self.simple_manager.save_statistics(
            ['192.168.19.20192.168.19.77','150',str(datetime.now())])

        self.assertEquals(results, True)

        for i in range(100):
            results = self.simple_manager.save_statistics(
                ['192.168.19.20192.168.19.77', '150', str(datetime.now())])

        self.assertEquals(results, True)

        to_time = datetime.now()
        from_time = to_time - timedelta(seconds=2)

        results = self.simple_manager.get_statistics(
            '192.168.19.20192.168.19.77', 10, str(from_time), str(to_time))

        self.assertEquals(10, len(results))

    def test_first_retrieve_case(self):

        for i in range(3):
            self.simple_manager.save_statistics(
                ['192.168.19.20192.168.19.77', '150', str(datetime.now())])

        to_time = datetime.now()
        from_time = to_time - timedelta(seconds=2)

        results = self.simple_manager.get_statistics(
            '192.168.19.20192.168.19.77', 10, str(from_time), str(to_time))

        self.assertEquals(3, len(results))

    def test_second_retrieve_case(self):

        for i in range(100):
            self.simple_manager.save_statistics(
                ['192.168.19.20192.168.19.77', '150', str(datetime.now())])

        to_time = datetime.now()
        from_time = to_time - timedelta(seconds=2)

        results = self.simple_manager.get_statistics(
            '192.168.19.20192.168.19.77', 50, str(from_time), str(to_time))

        self.assertEquals(50, len(results))

    def test_third_retrieve_case(self):

        for i in range(50):
            self.simple_manager.save_statistics(
                ['192.168.19.20192.168.19.77', i, str(datetime.now())])
        time.sleep(5)

        for i in range(50):
            self.simple_manager.save_statistics(
                ['192.168.19.20192.168.19.77', i+50, str(datetime.now())])

        to_time = datetime.now()
        from_time = to_time - timedelta(seconds=2)

        results = self.simple_manager.get_statistics(
            '192.168.19.20192.168.19.77', 25, str(from_time), str(to_time))
        for i in range(25):
            self.assertEquals(i+75, results[i])

    def test_batch_retrieve_case(self):

        data = []
        for i in range(50):
            data.append([i+50, str(datetime.now())])

        self.simple_manager.save_batch_statistics('192.168.19.20192.168.19.77',
                                                  data)

        to_time = datetime.now()
        from_time = to_time - timedelta(seconds=2)

        data2 = []
        for i in range(50):
            data.append([i*3, str(datetime.now())])

        self.simple_manager.save_batch_statistics('192.168.19.9876.168.19.77',
                                                  data2)

    def tearDown(self):
        os.unlink('test_database.json')
        self.simple_manager = None
