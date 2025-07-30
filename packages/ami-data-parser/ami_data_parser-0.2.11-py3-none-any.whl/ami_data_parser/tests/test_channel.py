from unittest import TestCase
from .utils import ChannelTest


class ChannelTestCase(TestCase):

    def test_instance_channel(self):
        received_data = {
            'channel': 'SIP/IP-7436-QPQGE-00000002',
            'context': 'C_1_ENT',
            'exten': '997799298',
            'priority': '1',
            'state': 'Down',
            'application': 'AppDial',
            'app_data': '(Outgoing Line)',
            'callerid_num': '997799298',
            'uniqueid': '1740760337.2'
        }
        channel = ChannelTest(**received_data)
        self.assertEqual(channel.channel, 'SIP/IP-7436-QPQGE-00000002')
        self.assertEqual(channel.context, 'C_1_ENT')
        self.assertEqual(channel.exten, '997799298')
        self.assertEqual(channel.priority, '1')
        self.assertEqual(channel.state, 'Down')
        self.assertEqual(channel.application, 'AppDial')
        self.assertEqual(channel.app_data, '(Outgoing Line)')
        self.assertEqual(channel.callerid_num, '997799298')
        self.assertEqual(channel.uniqueid, '1740760337.2')
        self.assertEqual(channel.timestamp, 1736960329.736009)
        self.assertEqual(channel.get_key(), 'SIP/IP-7436-QPQGE-00000002')
    
    def test_instance_equal(self):
        received_data = {
            'channel': 'SIP/IP-7436-QPQGE-00000002',
            'context': 'C_1_ENT',
            'exten': '997799298',
            'priority': '1',
            'state': 'Down',
            'application': 'AppDial',
            'app_data': '(Outgoing Line)',
            'callerid_num': '997799298',
            'uniqueid': '1740760337.2'
        }
        channel1 = ChannelTest(**received_data)
        received_data = {
            'channel': 'SIP/IP-7436-QPQGE-00000002',
            'context': 'C_1_ENT',
            'exten': '997799298',
            'priority': '1',
            'state': 'Down',
            'application': 'AppDial',
            'app_data': '(Outgoing Line)',
            'callerid_num': '997799298',
            'uniqueid': '1740760337.2'
        }
        channel2 = ChannelTest(**received_data)
        self.assertTrue(channel1 == channel2)
    
    def test_instance_not_equal(self):
        received_data = {
            'channel': 'SIP/IP-7436-QPQGE-00000002',
            'context': 'C_1_ENT',
            'exten': '997799298',
            'priority': '1',
            'state': 'Down',
            'application': 'AppDial',
            'app_data': '(Outgoing Line)',
            'callerid_num': '997799298',
            'uniqueid': '1740760337.2'
        }
        channel1 = ChannelTest(**received_data)
        received_data = {
            'channel': 'SIP/IP-7436-QPQGE-00000002',
            'context': 'C_1_ENT',
            'exten': '997799298',
            'priority': '1',
            'state': 'Ring',
            'application': 'AppDial',
            'app_data': '(Outgoing Line)',
            'callerid_num': '997799298',
            'uniqueid': '1740760337.2'
        }
        channel2 = ChannelTest(**received_data)
        self.assertFalse(channel1 == channel2)

    def test_channel_dict(self):
        received_data = {
            'channel': 'SIP/IP-7436-QPQGE-00000002',
            'context': 'C_1_ENT',
            'exten': '997799298',
            'priority': '1',
            'state': 'Down',
            'application': 'AppDial',
            'app_data': '(Outgoing Line)',
            'callerid_num': '997799298',
            'uniqueid': '1740760337.2'
        }
        expected_data = {
            'channel': 'SIP/IP-7436-QPQGE-00000002',
            'context': 'C_1_ENT',
            'exten': '997799298',
            'priority': '1',
            'state': 'Down',
            'application': 'AppDial',
            'app_data': '(Outgoing Line)',
            'callerid_num': '997799298',
            'uniqueid': '1740760337.2',
            'timestamp': 1736960329.736009,
            'type': 'channel'
        }
        channel = ChannelTest(**received_data)
        self.assertDictEqual(vars(channel), expected_data)