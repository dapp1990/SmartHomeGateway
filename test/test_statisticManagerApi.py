from statistics_module.simple_statistics_manager import SimpleStatisticsManager
from statistics_module.statistics_manager_api import StatisticsApi
from aiohttp.test_utils import AioHTTPTestCase, unittest_run_loop
import os

BASE_URL = 'http://127.0.0.1/'


class TestStatisticsApi(AioHTTPTestCase):

    def setUp(self):
        super(TestStatisticsApi, self).setUp()

    async def get_application(self):
        self.app = StatisticsApi(SimpleStatisticsManager("test_statistics"))
        return self.app.get_app()

    @unittest_run_loop
    async def test_example(self):
        for i in range(10):
            print(i)

        request = await self.client.request("GET", "/")
        self.assertEquals(request.status, 200)

        for i in range(10):
            print("*")

        response = await request.json()
        self.assertEquals("dummy_data", response['response'])

        for i in range(10,20):
            print(i)
    """
    def test_simple_request(self):
        res = self.app.get(BASE_URL)
        self.assertEquals(res.status_code, 200)
        data = json.loads(res.get_data().decode("utf-8") )
        self.assertEquals(data['response'], "dummy_data")

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
        super(TestStatisticsApi, self).tearDown()
        if os.path.exists('test_statistics.db'):
            os.unlink('test_statistics.db')
        # self.app = None
            