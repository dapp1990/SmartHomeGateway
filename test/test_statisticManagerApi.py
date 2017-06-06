from statistics_module.simple_statistics_manager import SimpleStatisticsManager
from unittest import TestCase
from copy import deepcopy
import os
from statistics_module.statistics_manager_api import StatisticsApi
import requests
import flask
import tempfile
import time
import json

BASE_URL = 'http://127.0.0.1:5001/'


class TestStatisticsApi(TestCase):

    def setUp(self):
        self.app = StatisticsApi(
            SimpleStatisticsManager('test_statisticsManagerApi')).test_client()
        self.app.testing = True

    def test_simple_request(self):
        res = self.app.get(BASE_URL)
        self.assertEquals(res.status_code, 200)
        data = json.loads(res.get_data().decode("utf-8") )
        self.assertEquals(data['response'], "dummy_data")

    """
    def test_simple_cycle(self):
        data = {"src": "192.168.10.90", "dst": "192.168.30.201", "size": 20000, "time": time.clock()}
        res = self.app.post(BASE_URL+"save_statistics",
                                 data=json.dumps(data),
                                 content_type='application/json')
        self.assertEqual(res.status_code, 200)
        data = json.loads(res.get_data())
        self.assertEquals(data['msg'], "saved")

        data = {"flow_id": "192.168.10.90192.168.30.201", "max_length": 20}
        res = self.app.get(BASE_URL + "get_statistics",
                            data=json.dumps(data),
                            content_type='application/json')
        self.assertEqual(res.status_code, 200)
        data = json.loads(res.get_data())
        self.assertEquals(data['msg'], "getting_statistics")
    """

    def tearDown(self):
        if os.path.exists('test_statisticsManagerApi.db'):
            os.unlink('test_statisticsManagerApi.db')
        self.app = None