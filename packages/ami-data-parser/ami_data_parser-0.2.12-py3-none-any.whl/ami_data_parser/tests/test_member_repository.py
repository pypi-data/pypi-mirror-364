from unittest import TestCase
from ami_data_parser.entities.queue_member import QueueMember
from ami_data_parser.factories.queue_member_factory import get_queue_members
from ami_data_parser.repositories.member_repository import MemberRepository


class MemberRepositoryTestCase(TestCase):

    def test_member_repository_set(self):
        received_data = {
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
        repository = MemberRepository()
        member = QueueMember(**received_data)
        repository.set(member)
        self.assertEqual(member, repository._objects.get('SIP/IP1489'))
    
    def test_member_repository_set_exception(self):
        repository = MemberRepository()
        self.assertRaises(
            ValueError,
            repository.set,
            {'name': 'teste'}
        )
    
    def test_member_repository_get(self):
        received_data = {
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
        repository = MemberRepository()
        member = QueueMember(**received_data)
        repository.set(member)
        self.assertEqual(member, repository.get('SIP/IP1489'))

    def test_member_repository_get_exception(self):
        repository = MemberRepository()
        self.assertRaises(
            QueueMember.DoesExists,
            repository.get,
            'SIP/IP-100'
        )
    
    def test_member_repository_exists(self):
        received_data = {
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
        repository = MemberRepository()
        self.assertFalse(repository.exists('SIP/IP1489'))
        member = QueueMember(**received_data)
        repository.set(member)
        self.assertTrue(repository.exists('SIP/IP1489'))
    
    def test_member_repository_delete(self):
        received_data = {
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
        repository = MemberRepository()
        member = QueueMember(**received_data)
        repository.set(member)
        repository.delete('SIP/IP1489')
        self.assertFalse(repository.exists('SIP/IP1489'))
    
    def test_member_repository_equal(self):
        received_data = {
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
        member = QueueMember(**received_data)
        repository1 = MemberRepository()
        repository2 = MemberRepository()
        repository1.set(member)
        repository2.set(member)
        self.assertTrue(repository1 == repository2)
    
    def test_member_repository_not_equal(self):
        received_data = {
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
        member1 = QueueMember(**received_data)
        received_data = {
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
        member2 = QueueMember(**received_data)
        repository1 = MemberRepository()
        repository2 = MemberRepository()
        repository1.set(member1)
        repository2.set(member2)
        self.assertFalse(repository1 == repository2)
    
    def test_member_repository_diff(self):
        repository = MemberRepository()
        received_data = [
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
            },
            {
                'name': 'SIP/IP1490',
                'has_paused': False,
                'reason_paused': None,
                'dynamic': None, 
                'in_call': False,
                'paused_time': 0,
                'logged_time': 0,
                'total_calls': 1,
                'last_call_time': 1218
            }
        ]
        members = get_queue_members(received_data)
        repository.set(members)
        self.assertListEqual(repository.diff(), [('SIP/IP1489', 'added'), ('SIP/IP1490', 'added')])
        self.assertListEqual(repository.diff(), [])
        received_data = [
            {
                'name': 'SIP/IP1489',
                'has_paused': True,
                'paused_time': 0,
                'reason_paused': None,
                'dynamic': None, 
                'in_call': False,
                'logged_time': 0,
                'total_calls': 3,
                'last_call_time': 1912
            },
            {
                'name': 'SIP/IP1490',
                'has_paused': True,
                'reason_paused': None,
                'dynamic': None, 
                'in_call': False,
                'paused_time': 0,
                'logged_time': 0,
                'total_calls': 1,
                'last_call_time': 1218
            }
        ]
        members = get_queue_members(received_data)
        repository.set(members)
        self.assertListEqual(repository.diff(), [('SIP/IP1490', 'changed')])