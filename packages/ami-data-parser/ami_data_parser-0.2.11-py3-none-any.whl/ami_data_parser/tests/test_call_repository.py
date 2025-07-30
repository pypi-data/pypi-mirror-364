from unittest import TestCase
from ami_data_parser.entities.call import Call
from ami_data_parser.factories.call_factory import get_calls
from ami_data_parser.repositories.call_repository import CallRepository


class CallRepositoryTestCase(TestCase):

    def test_call_repository_set(self):
        received_data = {
            'channel': 'IAX2/SERVER_2-9969',
            'position': 1,
            'wait_time': 60,
            'priority': 0
        }
        repository = CallRepository()
        call = Call(**received_data)
        repository.set(call)
        self.assertEqual(call, repository._objects.get('IAX2/SERVER_2-9969'))
    
    def test_call_repository_set_exception(self):
        repository = CallRepository()
        self.assertRaises(
            ValueError,
            repository.set,
            {'name': 'teste'}
        )
    
    def test_call_repository_get(self):
        received_data = {
            'channel': 'IAX2/SERVER_2-9969',
            'position': 1,
            'wait_time': 60,
            'priority': 0
        }
        repository = CallRepository()
        call = Call(**received_data)
        repository.set(call)
        self.assertEqual(call, repository.get('IAX2/SERVER_2-9969'))
    
    def test_call_repository_get_exception(self):
        repository = CallRepository()
        self.assertRaises(
            Call.DoesExists,
            repository.get,
            'SIP/IP-100-1234'
        )
    
    def test_call_repository_exists(self):
        received_data = {
            'channel': 'IAX2/SERVER_2-9969',
            'position': 1,
            'wait_time': 60,
            'priority': 0
        }
        repository = CallRepository()
        self.assertFalse(repository.exists('IAX2/SERVER_2-9969'))
        call = Call(**received_data)
        repository.set(call)
        self.assertTrue(repository.exists('IAX2/SERVER_2-9969'))
    
    def test_call_repository_delete(self):
        received_data = {
            'channel': 'IAX2/SERVER_2-9969',
            'position': 1,
            'wait_time': 60,
            'priority': 0
        }
        repository = CallRepository()
        call = Call(**received_data)
        repository.set(call)
        repository.delete('IAX2/SERVER_2-9969')
        self.assertFalse(repository.exists('IAX2/SERVER_2-9969'))
    
    def test_call_repository_equal(self):
        received_data = {
            'channel': 'IAX2/SERVER_2-9969',
            'position': 1,
            'wait_time': 60,
            'priority': 0
        }
        repository1 = CallRepository()
        repository2 = CallRepository()
        call1 = Call(**received_data)
        call2 = Call(**received_data)
        repository1.set(call1)
        repository2.set(call2)
        self.assertTrue(repository1 == repository2)
    
    def test_call_repository_not_equal(self):
        received_data = {
            'channel': 'IAX2/SERVER_2-9969',
            'position': 1,
            'wait_time': 60,
            'priority': 0
        }
        call1 = Call(**received_data)
        received_data = {
            'channel': 'IAX2/SERVER_2-9971',
            'position': 1,
            'wait_time': 20,
            'priority': 0
        }
        call2 = Call(**received_data)
        repository1 = CallRepository()
        repository2 = CallRepository()
        repository1.set(call1)
        repository2.set(call2)
        self.assertFalse(repository1 == repository2)
    
    def test_call_repository_diff(self):
        repository = CallRepository()
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
        repository.set(calls)
        self.assertListEqual(repository.diff(), [('IAX2/SERVER_2-13471', 'added'), ('IAX2/SERVER_2-9969', 'added')])
        self.assertListEqual(repository.diff(), [])
        received_data = [
            {
                'channel': 'IAX2/SERVER_2-13471',
                'position': 1,
                'wait_time': 545,
                'priority': 0
            },
            {
                'channel': 'IAX2/SERVER_2-9969',
                'position': 1,
                'wait_time': 69,
                'priority': 0
            }
        ]
        calls = get_calls(received_data)
        repository.set(calls)
        self.assertListEqual(repository.diff(), [('IAX2/SERVER_2-9969', 'changed')])