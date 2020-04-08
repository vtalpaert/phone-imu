# python modules
import unittest
import queue
import time
import random

# local code
import imu

random.seed(1)


def get_random_device_data():
    return [
        int(1000 * time.time()),  # [ms]
        random.gauss(0, 1),  # ax
        random.gauss(0, 1),  # ay
        random.gauss(0, 1),  # az
        random.gauss(0, 1),  # gx
        random.gauss(0, 1),  # gy
        random.gauss(0, 1),  # gz
    ]


class TestImu(unittest.TestCase):
    def setUp(self):
        self.imu = imu.IMU()

    def tearDown(self):
        self.imu.close()

    def test_background_task_start_close(self):
        print(self.imu.background_task)
        self.imu.close()
        print(self.imu.background_task)
        self.imu.start()
        print(self.imu.background_task)

    def test_ignore_empty_data(self):
        self.assertRaises(queue.Empty, self.imu.data_queue.get_nowait)
        self.imu.add_data([1, 0, 0, 0, 0, 0, 0])
        self.assertRaises(queue.Empty, self.imu.data_queue.get_nowait)

    @unittest.skip
    def test_latency_request(self):
        self.client.emit('latency_request')
        received = self.client.get_received()
        print(received)
        self.assertGreaterEqual(len(received), 1)
        self.assertEqual(received[-1]['args'][0]['text'], 'I started a latency test')
        for i in range(50):  # TODO latency request can choose another value
            self.client.emit('incoming_data', {'data': get_random_device_data()})
            time.sleep(0.01)
        received = self.client.get_received()
        print(received)
        self.assertGreaterEqual(len(received), 1)

    def test_last_data(self):
        for _ in range(10):
            data_in = get_random_device_data()
            self.imu.add_data(data_in)
        data_out = self.imu.get_last_data()
        self.assertEqual(data_in, data_out)

    def test_mean_data(self):
        for _ in range(10):
            data_in = get_random_device_data()
            self.imu.add_data(data_in)
        # TODO by students


if __name__ == '__main__':
    unittest.main()
