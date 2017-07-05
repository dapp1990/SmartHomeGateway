from statistics_module.basic_engine import StatisticsEngine
from statistics_module.webservice_api import StatisticsWebService
from datetime import datetime, timedelta
import requests
import json
import time

# Todo: create proper unittest, NOW statistics_manager_api MUST BE RUNNING

BASE_URL = "http://localhost:5001/"

# setUp
# app = StatisticsApi(SimpleStatisticsManager("test_statistics"))

# test_simple_request
res = requests.get(BASE_URL)
assert res.status_code == 200
data = res.json()
assert data['response'] == "dummy_data"


# test_simple_cycle

# for i in range(100):
#     now_str = str(datetime.now())
#     data = {"id_flow": "192.168.10.90192.168.30.201", "size": 20000+i,
#             "time": now_str}
#     res = requests.post(BASE_URL + "save_statistics", json=data,
#                         headers={'Content-type': 'application/json'})
#
#     assert res.status_code == 200
#     data = res.json()
#     assert data['response']
#
# to_time = datetime.now()
# from_time = to_time - timedelta(seconds=2)
#
# data = {'flow_id': '192.168.10.90192.168.30.201', 'max_length': 20,
#         'from_time': str(from_time), 'to_time': str(to_time)}
# res = requests.post(BASE_URL + "get_statistics", json=data,
#                     headers={'Content-type': 'application/json'})
# assert res.status_code == 200
# data = res.json()
# for i in range(20):
#     assert 20080+i == data['response'][i]
#
# time.sleep(4)
#
# to_time = datetime.now()
# from_time = to_time - timedelta(seconds=2)
#
# data = {"flow_id": "192.168.10.90192.168.30.201", "max_length": 20,
#         "from_time": str(from_time), "to_time": str(to_time)}
# res = requests.post(BASE_URL + "get_statistics", json=data,
#                     headers={'Content-type': 'application/json'})
# assert res.status_code == 200
# data = res.json()
# assert len(data['response']) == 0

data2 = []
for i in range(100):
    now_str = str(datetime.now())
    data2.append([30000+i, now_str])

data = {"id_flow": "192.168.10.90192.168.30.201", "batch": data2}

res = requests.post(BASE_URL + "save_batch_statistics",
                    json=data,
                    headers={'Content-type': 'application/json'})
assert res.status_code == 200



