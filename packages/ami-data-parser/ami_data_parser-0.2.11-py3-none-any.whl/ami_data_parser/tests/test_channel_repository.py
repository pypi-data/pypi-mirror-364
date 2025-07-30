from unittest import TestCase
from ami_data_parser.entities.channel import Channel
from ami_data_parser.factories.channel_factory import get_channels
from ami_data_parser.repositories.channel_repository import ChannelRepository


class ChannelRepositoryTestCase(TestCase):

    def test_channel_repository_set(self):
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
        channel = Channel(**received_data)
        repository = ChannelRepository()
        repository.set(channel)
        self.assertEqual(channel, repository._objects.get('SIP/IP-7436-QPQGE-00000002'))
    
    def test_channel_repository_get(self):
        received_data = [
            {
                'channel': 'SIP/IP-7436-QPQGE-00000002',
                'context': 'C_1_ENT',
                'exten': '997799298',
                'priority': '1',
                'state': 'Down',
                'application': 'AppDial',
                'app_data': '(Outgoing Line)',
                'callerid_num': '997799298',
                'uniqueid': '1740760337.2'
            },
            {
                'channel': 'SIP/IP-101-Q14V2-00000001',
                'context': 'macro-externa',
                'exten': 's',
                'priority': '22',
                'state': 'Ring',
                'application': 'Dial',
                'app_data': 'SIP/IP-7436-QPQGE/997799298,90,TtM(saida_atendimento)',
                'callerid_num': '101',
                'uniqueid': '1740760337.1'
            }
        ]
        channels = get_channels(received_data)
        repository = ChannelRepository()
        repository.set(channels)
        channel = repository.get(name='SIP/IP-7436-QPQGE-00000002')
        self.assertEqual(channel.channel, 'SIP/IP-7436-QPQGE-00000002')
        channel = repository.get(peername='SIP/IP-101-Q14V2')
        self.assertEqual(channel.channel, 'SIP/IP-101-Q14V2-00000001')

    def test_channel_repository_set_exception(self):
        repository = ChannelRepository()
        self.assertRaises(
            ValueError,
            repository.set,
            {'name': 'teste'}
        )

    def test_channel_repository_exists(self):
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
        channel = Channel(**received_data)
        repository = ChannelRepository()
        repository.set(channel)
        self.assertTrue(repository.exists('SIP/IP-7436-QPQGE-00000002'))
    
    def test_channel_repository_delete(self):
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
        channel = Channel(**received_data)
        repository = ChannelRepository()
        repository.set(channel)
        repository.delete('SIP/IP-7436-QPQGE-00000002')
        self.assertFalse(repository.exists('SIP/IP-7436-QPQGE-00000002'))

    def test_channel_diff(self):
        received_data = [
            {
                'channel': 'SIP/IP-7436-QPQGE-00000002',
                'context': 'C_1_ENT',
                'exten': '997799298',
                'priority': '1',
                'state': 'Down',
                'application': 'AppDial',
                'app_data': '(Outgoing Line)',
                'callerid_num': '997799298',
                'uniqueid': '1740760337.2'
            },
            {
                'channel': 'SIP/IP-101-Q14V2-00000001',
                'context': 'macro-externa',
                'exten': 's',
                'priority': '22',
                'state': 'Ring',
                'application': 'Dial',
                'app_data': 'SIP/IP-7436-QPQGE/997799298,90,TtM(saida_atendimento)',
                'callerid_num': '101',
                'uniqueid': '1740760337.1'
            }
        ]
        channels = get_channels(received_data)
        repository = ChannelRepository()
        repository.set(channels)
        self.assertListEqual(repository.diff(), [('SIP/IP-7436-QPQGE-00000002', 'added'), ('SIP/IP-101-Q14V2-00000001', 'added')])
        received_data = [
            {
                'channel': 'SIP/IP-7436-QPQGE-00000002',
                'context': 'C_1_ENT',
                'exten': '997799298',
                'priority': '1',
                'state': 'Ring',
                'application': 'AppDial',
                'app_data': '(Outgoing Line)',
                'callerid_num': '997799298',
                'uniqueid': '1740760337.2'
            },
            {
                'channel': 'SIP/IP-101-Q14V2-00000001',
                'context': 'macro-externa',
                'exten': 's',
                'priority': '22',
                'state': 'Ring',
                'application': 'Dial',
                'app_data': 'SIP/IP-7436-QPQGE/997799298,90,TtM(saida_atendimento)',
                'callerid_num': '101',
                'uniqueid': '1740760337.1'
            }
        ]
        channels = get_channels(received_data)
        repository.set(channels)
        self.assertListEqual(repository.diff(), [('SIP/IP-7436-QPQGE-00000002', 'changed')])
        received_data = [
            {
                'channel': 'SIP/IP-101-Q14V2-00000001',
                'context': 'macro-externa',
                'exten': 's',
                'priority': '22',
                'state': 'Ring',
                'application': 'Dial',
                'app_data': 'SIP/IP-7436-QPQGE/997799298,90,TtM(saida_atendimento)',
                'callerid_num': '101',
                'uniqueid': '1740760337.1'
            }
        ]
        channels = get_channels(received_data)
        repository.set(channels)
        self.assertListEqual(repository.diff(), [('SIP/IP-7436-QPQGE-00000002', 'removed')])