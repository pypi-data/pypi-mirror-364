from unittest import TestCase
from ami_data_parser.entities.queue import Queue
from ami_data_parser.factories.queue_factory import get_queues
from ami_data_parser.repositories.queue_repository import QueueRepository


class QueueRepositoryTestCase(TestCase):

    def test_queue_repository_set(self):
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
                    'dynamic': None, 
                    'in_call': False,
                    'paused_time': 0,
                    'reason_paused': None,
                    'logged_time': 0,
                    'total_calls': 3,
                    'last_call_time': 1912
                }
            ],
            'waiting_calls':[]
        }
        queue = Queue(**received_data)
        repository = QueueRepository()
        repository.set(queue)
        self.assertEqual(queue, repository._objects.get('Queue_1088'))

    def test_queue_repository_set_exception(self):
        repository = QueueRepository()
        self.assertRaises(
            ValueError,
            repository.set,
            {'name': 'teste'}
        )
    
    def test_queue_repository_exists(self):
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
                    'paused_time': 0,
                    'reason_paused': None,
                    'dynamic': None, 
                    'in_call': False,
                    'logged_time': 0,
                    'total_calls': 3,
                    'last_call_time': 1912
                }
            ],
            'waiting_calls':[]
        }
        repository = QueueRepository()
        self.assertFalse(repository.exists('Queue_1088'))
        queue = Queue(**received_data)
        repository.set(queue)
        self.assertTrue(repository.exists('Queue_1088'))
    
    def test_queue_repository_delete(self):
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
        repository = QueueRepository()
        queue = Queue(**received_data)
        repository.set(queue)
        repository.delete('Queue_1088')
        self.assertFalse(repository.exists('Queue_1088'))

    def test_queue_repository_diff(self):
        repository = QueueRepository()
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
        repository.set(queues)
        self.assertListEqual(repository.diff(), [('Queue_1088', 'added'), ('Queue_1020', 'added')])
        self.assertListEqual(repository.diff(), [])
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
                        'has_paused': True,
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
        repository.set(queues)
        self.assertListEqual(repository.diff(), [('Queue_1020', 'changed')])
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
            }
        ]
        queues = get_queues(received_data)
        repository.set(queues)
        self.assertListEqual(repository.diff(), [('Queue_1020', 'removed')])