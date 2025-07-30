from unittest import TestCase
from ami_data_parser.factories.call_factory import get_calls


class CallFactoryTestCase(TestCase):

    def test_get_calls(self):
        received_data = [
            {
                'channel': 'IAX2/SERVER_2-13471',
                'position': 1,
                'wait_time': 505,
                'priority': 0
            },
            {
                'channel': 'IAX2/SERVER_2-9969',
                'position': 2,
                'wait_time': 29,
                'priority': 0
            }
        ]
        calls = get_calls(received_data)
        self.assertEqual(len(calls), 2)