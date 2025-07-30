from unittest import TestCase
from ami_data_parser.factories.queue_factory import get_queues


class QueueFactoryTestCase(TestCase):

    def test_get_queues(self):
        received_data = [
            {
                'queuename': 'Queue_1088',
                'total_calls': 5,
                'strategy': 'rrmemory',
                'wait_mean': 348,
                'duration_mean': 304,
                'total_wait_calls': 10,
                'total_completed_calls': 43,
                'total_abandoned_calls': 11,
                'members': [
                    {
                        'name': 'SIP/IP1489',
                        'has_paused': False,
                        'reason_paused': None,
                        'dynamic': None, 
                        'in_call': False,
                        'paused_time': 0,
                        'logged_time': 0,
                        'total_calls': 3,
                        'last_call_time': 1912
                    }
                ],
                'waiting_calls':[]
            },
            {
                'queuename': 'Queue_1020',
                'total_calls': 4,
                'strategy': 'rrmemory',
                'wait_mean': 50,
                'duration_mean': 90,
                'total_wait_calls': 3,
                'total_completed_calls': 41,
                'total_abandoned_calls': 2,
                'members': [
                    {
                        'name': 'SIP/IP1488',
                        'has_paused': False,
                        'reason_paused': None,
                        'dynamic': None, 
                        'in_call': False,
                        'paused_time': 0,
                        'logged_time': 0,
                        'total_calls': 2,
                        'last_call_time': 1242
                    }
                ],
                'waiting_calls':[]
            }
        ]
        queues = get_queues(received_data)
        self.assertEqual(len(queues), 2)