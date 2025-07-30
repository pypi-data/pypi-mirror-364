from unittest import TestCase
from ami_data_parser.entities.queue_member import QueueMember


class MemberTestCase(TestCase):

    def test_instance_member(self):
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
        self.assertEqual(member.type, 'member')
        self.assertEqual(member.name, 'SIP/IP1489')
        self.assertEqual(member.has_paused, False)
        self.assertEqual(member.reason_paused, None)
        self.assertEqual(member.paused_time, 0)
        self.assertEqual(member.logged_time, 0)
        self.assertEqual(member.total_calls, 3)
        self.assertEqual(member.last_call_time, 1912)
        self.assertEqual(member.reason_paused, None)
        self.assertEqual(member.dynamic, None)
        self.assertEqual(member.in_call, False)
    
    def test_instance_member_paused(self):
        received_data = {
            'name': 'SIP/IP1489',
            'has_paused': True,
            'reason_paused': 'Reunião',
            'dynamic': None, 
            'in_call': False,
            'paused_time': 0,
            'logged_time': 0,
            'total_calls': 3,
            'last_call_time': 1912
        }
        member = QueueMember(**received_data)
        self.assertEqual(member.type, 'member')
        self.assertEqual(member.name, 'SIP/IP1489')
        self.assertEqual(member.has_paused, True)
        self.assertEqual(member.reason_paused, 'Reunião')
        self.assertEqual(member.paused_time, 0)
        self.assertEqual(member.logged_time, 0)
        self.assertEqual(member.total_calls, 3)
        self.assertEqual(member.last_call_time, 1912)
        self.assertEqual(member.dynamic, None)
        self.assertEqual(member.in_call, False)
    
    def test_instance_member_equal(self):
        received_data = {
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
        member1 = QueueMember(**received_data)
        received_data = {
            'name': 'SIP/IP1489',
            'has_paused': False,
            'dynamic': None, 
            'in_call': False,
            'paused_time': 0,
            'reason_paused': None,
            'logged_time': 0,
            'total_calls': 3,
            'last_call_time': 2523
        }
        member2 = QueueMember(**received_data)
        self.assertTrue(member1 == member2)
    
    def test_instance_member_not_equal(self):
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
            'last_call_time': 2523
        }
        member2 = QueueMember(**received_data)
        self.assertFalse(member1 == member2)