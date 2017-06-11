from statistics_module.simple_statistics_manager import SimpleStatisticsManager
from statistics_module.statistics_manager_api import StatisticsApi
import requests
import json
import time

# Todo: create proper unittest

BASE_URL = "http://localhost:5001/"

# setUp
# app = StatisticsApi(SimpleStatisticsManager("test_statistics"))

# test_simple_request
res = requests.get(BASE_URL)
assert res.status_code == 200
data = res.json()
assert data['response'] == "dummy_data"


# test_simple_cycle

for i in range(100):
    data = {"src": "192.168.10.90", "dst": "192.168.30.201", "size": 20000+i,
            "time": time.clock()}
    res = requests.post(BASE_URL + "save_statistics", json=json.dumps(data),
                        headers={'Content-type': 'application/json'})

    assert res.status_code == 200
    data = res.json()
    assert data['response']

data = {"flow_id": "192.168.10.90192.168.30.201", "max_length": 20}
res = requests.post(BASE_URL + "get_statistics", json=json.dumps(data),
                    headers={'Content-type':'application/json'})
assert res.status_code == 200
data = res.json()
assert data['response']