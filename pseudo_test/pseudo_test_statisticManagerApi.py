from statistics_module.simple_statistics_manager import SimpleStatisticsManager
from statistics_module.statistics_manager_api import StatisticsApi
from datetime import datetime, timedelta
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
    now_str = str(datetime.now())
    data = {"src": "192.168.10.90", "dst": "192.168.30.201", "size": 20000+i,
            "time": now_str}
    res = requests.post(BASE_URL + "save_statistics", json=json.dumps(data),
                        headers={'Content-type': 'application/json'})

    assert res.status_code == 200
    data = res.json()
    assert data['response']

to_time = datetime.now()
from_time = to_time - timedelta(seconds=2)

data = {"flow_id": "192.168.10.90192.168.30.201", "max_length": 20,
        "from_time": str(from_time), "to_time": str(to_time)}
res = requests.post(BASE_URL + "get_statistics", json=json.dumps(data),
                    headers={'Content-type': 'application/json'})
assert res.status_code == 200
data = res.json()
for i in range(20):
    assert 20080+i == data['response'][i]

time.sleep(4)

to_time = datetime.now()
from_time = to_time - timedelta(seconds=2)

data = {"flow_id": "192.168.10.90192.168.30.201", "max_length": 20,
        "from_time": str(from_time), "to_time": str(to_time)}
res = requests.post(BASE_URL + "get_statistics", json=json.dumps(data),
                    headers={'Content-type': 'application/json'})
assert res.status_code == 200
data = res.json()
assert len(data['response']) == 0

