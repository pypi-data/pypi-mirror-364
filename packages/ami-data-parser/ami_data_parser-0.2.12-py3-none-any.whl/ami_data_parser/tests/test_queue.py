from unittest import TestCase
from ami_data_parser.entities.queue import Queue
from ami_data_parser.repositories.member_repository import MemberRepository
from ami_data_parser.repositories.call_repository import CallRepository


class QueueTestCase(TestCase):

    def test_instance_queue(self):
        received_data = {
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
        }
        queue = Queue(**received_data)
        self.assertEqual(queue.type, 'queue')
        self.assertEqual(queue.queuename, 'Queue_1088')
        self.assertEqual(queue.total_calls, 5)
        self.assertEqual(queue.strategy, 'rrmemory')
        self.assertEqual(queue.wait_mean, 348)
        self.assertEqual(queue.duration_mean, 304)
        self.assertEqual(queue.total_wait_calls, 10)
        self.assertEqual(queue.total_completed_calls, 43)
        self.assertEqual(queue.total_abandoned_calls, 11)
        self.assertEqual(type(queue.members), MemberRepository)
        self.assertEqual(type(queue.waiting_calls), CallRepository)
    
    def test_instance_queue_equal(self):
        received_data = {
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
        }
        queue1 = Queue(**received_data)
        received_data = {
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
        }
        queue2 = Queue(**received_data)
        self.assertTrue(queue1 == queue2)
    
    def test_instance_queue_not_equal(self):
        received_data = {
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
        }
        queue1 = Queue(**received_data)
        received_data = {
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
                    'has_paused': True,
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
        }
        queue2 = Queue(**received_data)
        self.assertFalse(queue1 == queue2)
    
    def test_queue_dict(self):
        received_data = {
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
        }
        expect_data = {'queuename': 'Queue_1088', 'total_calls': 5, 'strategy': 'rrmemory', 'wait_mean': 348, 'duration_mean': 304, 'total_wait_calls': 10, 'total_completed_calls': 43, 'total_abandoned_calls': 11, 'members': [{'name': 'SIP/IP1489', 'has_paused': False, 'reason_paused': None, 'dynamic': None, 'in_call': False, 'paused_time': 0, 'logged_time': 0, 'total_calls': 3, 'last_call_time': 1912, 'type': 'member'}], 'type': 'queue', 'waiting_calls':[]}
        queue = Queue(**received_data)
        self.assertDictEqual(queue.get_dict(), expect_data)