from statistics_module.simple_statistics_manager import SimpleStatisticsManager
from unittest import TestCase
from copy import deepcopy
import os
from statistics_module.statistics_manager_api import StatisticsApi
import requests
import flask
import tempfile

BASE_URL = 'http://127.0.0.1:5001/'


class TestStatisticsApi(TestCase):

    def setUp(self):
        self.app = StatisticsApi(SimpleStatisticsManager('testing_database')).app.test_client()
        self.app.testing = True
 
    def test_simple_request(self):
        response = self.app.get(BASE_URL)