# python modules
import unittest

# dependencies
import flask_socketio

# local code
import server


class TestServer(unittest.TestCase):
    def setUp(self):
        server.app.testing = True
        self.app = server.app
        self.flask_client = self.app.test_client()
        self.socketio = server.socketio
        self.client = flask_socketio.test_client.SocketIOTestClient(
            self.app,
            self.socketio,
            flask_test_client=self.flask_client
        )

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

    @unittest.skip
    def test_emit_data(self):
        # TODO
        self.client.emit('incoming_data', {'data': [date, ax, ay, az, gx, gy, gz]})

    @unittest.skip
    def test_emit_constant_data(self):
        # TODO
        self.client.emit('incoming_data', {'data': [date, ax, ay, az, gx, gy, gz]})

    @unittest.skip
    def test_latency_request(self):
        # TODO
        self.client.emit('latency_request')

    @unittest.skip
    def test_concurrent_latency_request(self):
        # TODO
        self.client.emit('latency_request')
        self.client.emit('latency_request')


if __name__ == '__main__':
    unittest.main()