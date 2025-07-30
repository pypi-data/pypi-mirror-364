from unittest import TestCase
from ami_data_parser.entities.call import Call


class CallTestCase(TestCase):

    def test_instance_call(self):
        received_data = {
            'channel': 'IAX2/SERVER_2-9969',
            'position': 2,
            'wait_time': 29,
            'priority': 0
        }
        call = Call(**received_data)
        self.assertEqual(call.channel, 'IAX2/SERVER_2-9969')
        self.assertEqual(call.position, 2)
        self.assertEqual(call.wait_time, 29)
        self.assertEqual(call.priority, 0)
        self.assertEqual(call.get_key(), 'IAX2/SERVER_2-9969')

    def test_instance_equal(self):
        received_data = {
            'channel': 'IAX2/SERVER_2-9969',
            'position': 2,
            'wait_time': 29,
            'priority': 0
        }
        call1 = Call(**received_data)
        received_data = {
            'channel': 'IAX2/SERVER_2-9969',
            'position': 2,
            'wait_time': 45,
            'priority': 0
        }
        call2 = Call(**received_data)
        self.assertEqual(call1, call2)

    def test_instance_not_equal(self):
        received_data = {
            'channel': 'IAX2/SERVER_2-9969',
            'position': 2,
            'wait_time': 29,
            'priority': 0
        }
        call1 = Call(**received_data)
        received_data = {
            'channel': 'IAX2/SERVER_2-9969',
            'position': 1,
            'wait_time': 60,
            'priority': 0
        }
        call2 = Call(**received_data)
        self.assertNotEqual(call1, call2)
    
    def test_call_dict(self):
        received_data = {
            'channel': 'IAX2/SERVER_2-9969',
            'position': 2,
            'wait_time': 29,
            'priority': 0
        }
        expected_data = {'channel': 'IAX2/SERVER_2-9969', 'position': 2, 'wait_time': 29, 'priority': 0, 'type': 'call'}
        call = Call(**received_data)
        self.assertDictEqual(vars(call), expected_data)