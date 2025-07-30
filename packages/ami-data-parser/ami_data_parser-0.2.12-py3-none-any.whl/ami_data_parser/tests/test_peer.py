from unittest import TestCase
from .utils import PeerTest
from ami_data_parser.entities.peer import Peer


class PeerTestCase(TestCase):

    def test_instance_peer(self):
        received_data = {
            'exten': '104',
            'peername': 'SIP/IP-104-IJ8vP',
            'state': 'Unavailable',
            'presence': 'not_set',
            'watchers': 0
        }
        peer = PeerTest(**received_data)
        self.assertEqual(peer.type, 'peer')
        self.assertEqual(peer.exten, '104')
        self.assertEqual(peer.peername, 'SIP/IP-104-IJ8vP')
        self.assertEqual(peer.state, 'Unavailable')
        self.assertEqual(peer.presence, 'not_set')
        self.assertEqual(peer.timestamp, 1736960329.736009)
        self.assertEqual(peer.watchers, 0)
    
    def test_instance_equal(self):
        received_data = {
            'exten': '104',
            'peername': 'SIP/IP-104-IJ8vP',
            'state': 'Unavailable',
            'presence': 'not_set',
            'watchers': 0
        }
        peer1 = Peer(**received_data)
        received_data = {
            'exten': '104',
            'peername': 'SIP/IP-104-IJ8vP',
            'state': 'Unavailable',
            'presence': 'not_set',
            'watchers': 1
        }
        peer2 = Peer(**received_data)
        self.assertTrue(peer1 == peer2)
    
    def test_instance_not_equal(self):
        received_data = {
            'exten': '104',
            'peername': 'SIP/IP-104-IJ8vP',
            'state': 'Unavailable',
            'presence': 'not_set',
            'watchers': 0
        }
        peer1 = Peer(**received_data)
        received_data = {
            'exten': '104',
            'peername': 'SIP/IP-104-IJ8vP',
            'state': 'Idle',
            'presence': 'not_set',
            'watchers': 0
        }
        peer2 = Peer(**received_data)
        self.assertFalse(peer1 == peer2)
    
    def test_peer_dict(self):
        received_data = {
            'exten': '104',
            'peername': 'SIP/IP-104-IJ8vP',
            'state': 'Unavailable',
            'presence': 'not_set',
            'watchers': 0
        }
        expect_data = {'type': 'peer', 'exten': '104', 'peername': 'SIP/IP-104-IJ8vP', 'state': 'Unavailable', 'presence': 'not_set', 'watchers': 0, 'timestamp': 1736960329.736009}
        peer = PeerTest(**received_data)
        self.assertDictEqual(vars(peer), expect_data)