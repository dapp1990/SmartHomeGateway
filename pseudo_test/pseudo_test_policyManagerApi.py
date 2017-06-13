from statistics_module.simple_statistics_manager import SimpleStatisticsManager
from statistics_module.statistics_manager_api import StatisticsApi
from datetime import datetime, timedelta
import requests
import json
import time

# Todo: create proper unittest, NOW statistics_manager_api AND
# policy_manager_api MUST BE RUNNING

BASE_URL = "http://localhost:5002/"

# setUp
# app = StatisticsApi(SimpleStatisticsManager("test_statistics"))
flows = ['1.0','2.0','3.0','4.0','5.0','6.0','7.0','8.0','9.0']
reserved_bytes = (150 + 16) * 10

# test_simple_request
res = requests.get(BASE_URL)
assert res.status_code == 200
data = res.json()
assert data['response']['response'] == "dummy_data"

# test_simple_cycle

current_flows = {}

for flow in flows:
    data = {'flow_id': flow, 'current_flows':current_flows}
    res = requests.post(BASE_URL + "get_bandwidth", json=json.dumps(data),
                        headers={'Content-type': 'application/json'})
    assert res.status_code == 200
    data = res.json()
    current_flows[flow] = int(data['response'])

assert sum(current_flows.values()) == reserved_bytes*9

data = {'flow_id': '1.0', 'current_flows': current_flows}
res = requests.post(BASE_URL + "update_bandwidths", json=json.dumps(data),
                    headers={'Content-type': 'application/json'})
assert res.status_code == 200
data = res.json()

assert len(data['response']) == 9
assert data['response']['1.0'] == reserved_bytes*2
assert sum(data['response'].values()) == reserved_bytes*2

