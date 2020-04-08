# python modules
import unittest
import queue
import time
import random

# dependencies
import flask_socketio

# local code
import server


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

def get_test_clients():
    server.app.testing = True
    flask_client = server.app.test_client()
    client = flask_socketio.test_client.SocketIOTestClient(
        server.app,
        server.socketio,
        flask_test_client=flask_client
    )
    return flask_client, client


class TestServerCommunication(unittest.TestCase):
    def setUp(self):
        server.app.testing = True
        self.flask_client, self.client = get_test_clients()

    def test_home(self):
        result = self.flask_client.get('/')

    def test_connect(self):
        self.assertTrue(self.client.is_connected())
        received = self.client.get_received()
        # [{'name': 'server_response', 'args': [{'text': 'Client is connected'}], 'namespace': '/'}]
        self.assertEqual(len(received), 1)
        self.assertEqual(received[0]['args'][0]['text'], 'Client is connected')
        self.client.disconnect()
        self.assertFalse(self.client.is_connected())

    def test_action_request(self):
        #self.client.get_received() # flush connection message
        for i in range(1, 11):
            self.client.emit('action_request')
            received = self.client.get_received()
            #print('received', received)
            self.assertGreaterEqual(len(received), 1)
            self.assertEqual(len(received[-1]['args'][0]), 2)
            self.assertEqual(received[-1]['name'], 'server_response')
            self.assertEqual(received[-1]['args'][0]['count'], i)

    def test_emit_data(self):
        self.client.emit('incoming_data', {'data': get_random_device_data()})

    def test_latency_request(self):
        self.client.emit('latency_request')
        received = self.client.get_received()
        self.assertGreaterEqual(len(received), 1)
        self.assertEqual(received[-1]['args'][0]['text'], 'I started a latency test')
        for i in range(50):  # TODO latency request can choose another value
            self.client.emit('incoming_data', {'data': get_random_device_data()})
            time.sleep(0.01)
        received = self.client.get_received()
        print(received)
        self.assertGreaterEqual(len(received), 1)

    @unittest.skip
    def test_latency_request_on_empty_data(self):
        # TODO we expect a timeout during the get, so latency should be -1
        self.client.emit('latency_request')

    @unittest.skip
    def test_concurrent_latency_request(self):
        # TODO request another latency test while one is already running
        self.client.emit('latency_request')
        self.client.emit('latency_request')


class ImuTest(unittest.TestCase):
    def setUp(self):
        _, self.client = get_test_clients()
        self.imu = server.imu

    def test_start_background_task(self):
        self.assertTrue(self.client.is_connected())
        self.assertTrue(self.imu.is_started())

    def test_ignore_empty_data(self):
        self.assertRaises(queue.Empty, self.imu.data_queue.get_nowait)
        self.client.emit('incoming_data', {'data': [1, 0, 0, 0, 0, 0, 0]})
        self.assertRaises(queue.Empty, self.imu.data_queue.get_nowait)

    def test_data_in_queue(self):
        data_sent = get_random_device_data()
        self.client.emit('incoming_data', {'data': data_sent})
        data_received = self.imu.data_queue.get(timeout=1)
        self.assertEqual(data_sent, data_received)


if __name__ == '__main__':
    unittest.main()
