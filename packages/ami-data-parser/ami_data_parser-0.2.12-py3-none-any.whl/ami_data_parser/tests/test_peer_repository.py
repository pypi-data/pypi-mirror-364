from unittest import TestCase
from ami_data_parser.entities.peer import Peer
from ami_data_parser.factories.peer_factory import get_peers
from ami_data_parser.repositories.peer_repository import PeerRepository


class PeerRepositoryTestCase(TestCase):

    def test_peer_repository_set(self):
        received_data = {
            'exten': '104',
            'peername': 'SIP/IP-104-IJ8vP',
            'state': 'Unavailable',
            'presence': 'not_set',
            'watchers': 0
        }
        peer = Peer(**received_data)
        repository = PeerRepository()
        repository.set(peer)
        self.assertEqual(peer, repository._objects.get('SIP/IP-104-IJ8vP'))

    def test_peer_repository_set_exception(self):
        repository = PeerRepository()
        self.assertRaises(
            ValueError,
            repository.set,
            {'name': 'teste'}
        )
    
    def test_peer_repository_exists(self):
        received_data = {
            'exten': '104',
            'peername': 'SIP/IP-104-IJ8vP',
            'state': 'Unavailable',
            'presence': 'not_set',
            'watchers': 0
        }
        repository = PeerRepository()
        self.assertFalse(repository.exists('SIP/IP-104-IJ8vP'))
        peer = Peer(**received_data)
        repository.set(peer)
        self.assertTrue(repository.exists('SIP/IP-104-IJ8vP'))
    
    def test_peer_repository_delete(self):
        received_data = {
            'exten': '104',
            'peername': 'SIP/IP-104-IJ8vP',
            'state': 'Unavailable',
            'presence': 'not_set',
            'watchers': 0
        }
        repository = PeerRepository()
        peer = Peer(**received_data)
        repository.set(peer)
        repository.delete('SIP/IP-104-IJ8vP')
        self.assertFalse(repository.exists('SIP/IP-104-IJ8vP'))
    
    def test_peer_diff(self):
        repository = PeerRepository()
        received_data = [{'exten': '104', 'peername': 'SIP/IP-104-IJ8vP', 'state': 'Unavailable', 'presence': 'not_set', 'watchers': 0}, {'exten': '104', 'peername': 'SIP/IP-104-7QmO5', 'state': 'Unavailable', 'presence': 'not_set', 'watchers': 0}, {'exten': '105', 'peername': 'SIP/IP-105-rrPi8', 'state': 'Unavailable', 'presence': 'not_set', 'watchers': 0}]
        repository.set(get_peers(received_data))
        self.assertListEqual(repository.diff(), [('SIP/IP-104-IJ8vP', 'added'), ('SIP/IP-104-7QmO5', 'added'), ('SIP/IP-105-rrPi8', 'added')])
        self.assertListEqual(repository.diff(), [])
        received_data = [{'exten': '104', 'peername': 'SIP/IP-104-IJ8vP', 'state': 'Idle', 'presence': 'not_set', 'watchers': 0}, {'exten': '104', 'peername': 'SIP/IP-104-7QmO5', 'state': 'Unavailable', 'presence': 'not_set', 'watchers': 0}, {'exten': '105', 'peername': 'SIP/IP-105-rrPi8', 'state': 'Unavailable', 'presence': 'not_set', 'watchers': 0}]
        repository.set(get_peers(received_data))
        self.assertListEqual(repository.diff(), [('SIP/IP-104-IJ8vP', 'changed')])
        received_data = [{'exten': '104', 'peername': 'SIP/IP-104-IJ8vP', 'state': 'Idle', 'presence': 'not_set', 'watchers': 0}, {'exten': '105', 'peername': 'SIP/IP-105-rrPi8', 'state': 'Unavailable', 'presence': 'not_set', 'watchers': 0}]
        repository.set(get_peers(received_data))
        self.assertListEqual(repository.diff(), [('SIP/IP-104-7QmO5', 'removed')])