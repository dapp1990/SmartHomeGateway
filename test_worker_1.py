import time
import requests

r = 100
url = "http://localhost:5001/2"

start = time.clock
for i in range(r):
    res = requests.get(url.format(i))
    delay = res.json()
    d = res.headers.get("DATE")
    print("{}:{} delay {}".format(d, res.url, delay['delay']))