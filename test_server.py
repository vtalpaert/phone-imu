# python modules
import unittest
import time
import random

# dependencies
import flask_socketio

# local code
import server


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
        # all test will have a client
        server.app.testing = True
        self.flask_client, self.client = get_test_clients()

    @classmethod
    def tearDownClass(self):
        # after all tests are done, close imu background thread
        # do not close after each test since the imu object is shared
        # and unique for the server
        server.imu.close()

    def test_home(self):
        result = self.flask_client.get('/')

    def test_connect(self):
        self.assertTrue(self.client.is_connected())
        received = self.client.get_received()
        # [{'name': 'server_response', 'args': [{'text': 'Client is connected'}], 'namespace': '/'}]
        self.assertEqual(len(received), 2)
        self.assertEqual(received[0]['args'][0]['text'], 'Client is connected')
        self.assertEqual(received[1]['args'][0]['interval'], server.imu.client_send_interval)
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
            self.assertListEqual(list(received[-1]['args'][0].keys()), ['text', 'recording'])

    def test_emit_data(self):
        self.client.emit('incoming_data', {'data': ['Latest data!']})

if __name__ == '__main__':
    unittest.main()
