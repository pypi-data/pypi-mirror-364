from unittest import TestCase
from ami_data_parser.controller import Controller
from ami_data_parser.entities.channel import Channel
from ami_data_parser.entities.peer import Peer
from ami_data_parser.entities.queue import Queue
from .utils import (
    ChannelTest,
    PeerTest, 
    get_channels_test,
    get_peers_test
)


class ControllerTestCase(TestCase):

    def test_update(self):
        received_data = ['Response: Success\r\n', 'ActionID: server-00000003\r\n', 'Message: Command output follows\r\n', 'Output: \r\n', 'Output:     -= Registered Asterisk Dial Plan Hints =-\r\n', 'Output: 100@BLF_1           : SIP/IP-100-CdFaT      State:Idle     Presence:not_set         Watchers  0\r\n', 'Output: 104@BLF_3           : SIP/IP-104-7QmO5      State:Unavailable     Presence:not_set         Watchers  0\r\n', 'Output: ----------------\r\n', 'Output: - 2 hints registered\r\n']
        expected_data = [{'exten': '100', 'peername': 'SIP/IP-100-CdFaT', 'state': 'Idle', 'presence': 'not_set', 'watchers': 0, 'type': 'peer', 'event': 'added', 'timestamp': 1736960329.736009 }, {'exten': '104', 'peername': 'SIP/IP-104-7QmO5', 'state': 'Unavailable', 'presence': 'not_set', 'watchers': 0, 'type': 'peer', 'event': 'added', 'timestamp': 1736960329.736009 }]
        controller = Controller()
        controller._get_peers = get_peers_test
        controller._peer_repository._entitie = PeerTest
        controller._get_channels = get_channels_test
        controller._channel_repository._entitie = ChannelTest
        data = controller.update(received_data)
        self.assertListEqual(data, expected_data)
        received_data = ['Response: Success\r\n', 'ActionID: server-00000002\r\n', 'Message: Command output follows\r\n', "Output: Queue_11 has 0 calls (max unlimited) in 'rrmemory' strategy (0s holdtime, 0s talktime), W:0, C:0, A:0, SL:0.0%, SL2:0.0% within 0s\r\n", 'Output:    Members: \r\n', 'Output:       SIP/IP-100-CdFaT (ringinuse disabled) (paused was 2930362 secs ago) (Not in use) has taken no calls yet (login was 2930362 secs ago)\r\n', 'Output:       SIP/IP-101 (ringinuse disabled) (Not in use) has taken no calls yet (login was 2930362 secs ago)\r\n', 'Output:    No Callers\r\n', 'Output: \r\n', "Output: Queue_27 has 0 calls (max unlimited) in 'rrmemory' strategy (0s holdtime, 0s talktime), W:0, C:0, A:0, SL:0.0%, SL2:0.0% within 0s\r\n", 'Output:    No Members\r\n', 'Output:    No Callers\r\n', 'Output: \r\n', "Output: Queue_44 has 0 calls (max unlimited) in 'rrmemory' strategy (0s holdtime, 0s talktime), W:0, C:0, A:0, SL:0.0%, SL2:0.0% within 0s\r\n", 'Output:    Members: \r\n', 'Output:       SIP/IP-100-boazN (ringinuse disabled) (Unavailable) has taken no calls yet (login was 2930362 secs ago)\r\n', 'Output:       SIP/IP-101-Iathq (ringinuse disabled) (Unavailable) has taken no calls yet (login was 2930362 secs ago)\r\n', 'Output:    No Callers\r\n', 'Output: \r\n', "Output: Queue_47 has 0 calls (max unlimited) in 'rrmemory' strategy (0s holdtime, 0s talktime), W:0, C:0, A:0, SL:0.0%, SL2:0.0% within 0s\r\n", 'Output:    No Members\r\n', 'Output:    No Callers\r\n', 'Output: \r\n', 'Output: \r\n']
        expected_data = [{'queuename': 'Queue_11', 'total_calls': 0, 'strategy': 'rrmemory', 'wait_mean': 0, 'duration_mean': 0, 'total_wait_calls': 0, 'total_completed_calls': 0, 'total_abandoned_calls': 0, 'members': [{'name': 'SIP/IP-100-CdFaT', 'has_paused': True, 'reason_paused': None, 'dynamic': None, 'in_call': False, 'paused_time': 2930362, 'logged_time': 2930362, 'total_calls': 0, 'last_call_time': 0, 'type': 'member'}, {'name': 'SIP/IP-101', 'has_paused': False, 'reason_paused': None, 'dynamic': None, 'in_call': False, 'paused_time': 0, 'logged_time': 2930362, 'total_calls': 0, 'last_call_time': 0, 'type': 'member'}], 'waiting_calls': [], 'type': 'queue', 'event': 'added'}, {'queuename': 'Queue_27', 'total_calls': 0, 'strategy': 'rrmemory', 'wait_mean': 0, 'duration_mean': 0, 'total_wait_calls': 0, 'total_completed_calls': 0, 'total_abandoned_calls': 0, 'members': [], 'waiting_calls': [], 'type': 'queue', 'event': 'added'}, {'queuename': 'Queue_44', 'total_calls': 0, 'strategy': 'rrmemory', 'wait_mean': 0, 'duration_mean': 0, 'total_wait_calls': 0, 'total_completed_calls': 0, 'total_abandoned_calls': 0, 'members': [{'name': 'SIP/IP-100-boazN', 'has_paused': False, 'reason_paused': None, 'dynamic': None, 'in_call': False, 'paused_time': 0, 'logged_time': 2930362, 'total_calls': 0, 'last_call_time': 0, 'type': 'member'}, {'name': 'SIP/IP-101-Iathq', 'has_paused': False, 'reason_paused': None, 'dynamic': None, 'in_call': False, 'paused_time': 0, 'logged_time': 2930362, 'total_calls': 0, 'last_call_time': 0, 'type': 'member'}], 'waiting_calls': [], 'type': 'queue', 'event': 'added'}, {'queuename': 'Queue_47', 'total_calls': 0, 'strategy': 'rrmemory', 'wait_mean': 0, 'duration_mean': 0, 'total_wait_calls': 0, 'total_completed_calls': 0, 'total_abandoned_calls': 0, 'members': [], 'waiting_calls': [], 'type': 'queue', 'event': 'added'}]
        data = controller.update(received_data)
        self.assertListEqual(data, expected_data)
        received_data = ['Response: Success\r\n', 'ActionID: server-00000003\r\n', 'Message: Command output follows\r\n', 'Output: \r\n', 'Output:     -= Registered Asterisk Dial Plan Hints =-\r\n', 'Output: 100@BLF_1           : SIP/IP-100-CdFaT      State:InUse     Presence:not_set         Watchers  0\r\n', 'Output: 104@BLF_3           : SIP/IP-104-7QmO5      State:Unavailable     Presence:not_set         Watchers  0\r\n', 'Output: ----------------\r\n', 'Output: - 2 hints registered\r\n']
        expected_data = [{'exten': '100', 'peername': 'SIP/IP-100-CdFaT', 'state': 'InUse', 'presence': 'not_set', 'watchers': 0, 'type': 'peer', 'event': 'changed', 'timestamp': 1736960329.736009 }, {'queuename': 'Queue_11', 'total_calls': 0, 'strategy': 'rrmemory', 'wait_mean': 0, 'duration_mean': 0, 'total_wait_calls': 0, 'total_completed_calls': 0, 'total_abandoned_calls': 0, 'members': [{'name': 'SIP/IP-100-CdFaT', 'has_paused': True, 'reason_paused': None, 'dynamic': None, 'in_call': False, 'paused_time': 2930362, 'logged_time': 2930362, 'total_calls': 0, 'last_call_time': 0, 'type': 'member'}, {'name': 'SIP/IP-101', 'has_paused': False, 'reason_paused': None, 'dynamic': None, 'in_call': False, 'paused_time': 0, 'logged_time': 2930362, 'total_calls': 0, 'last_call_time': 0, 'type': 'member'}], 'waiting_calls': [], 'type': 'queue', 'event': 'changed'}]
        data = controller.update(received_data)
        self.assertListEqual(data, expected_data)
        received_data = ['Response: Success\r\n', 'ActionID: tatianno-ThinkPad-L470-00000001\r\n', 'Message: Command output follows\r\n', 'Output: SIP/IP-7436-QPQGE-00000002!C_1_ENT!997799298!1!Down!AppDial!(Outgoing Line)!997799298!3!3!3!2!!1740760337.2\r\n', 'Output: SIP/IP-101-Q14V2-00000001!macro-externa!s!22!Ring!Dial!SIP/IP-7436-QPQGE/997799298,90,TtM(saida_atendimento)!101!3!!3!2!!1740760337.1\r\n']
        expected_data = [{'channel': 'SIP/IP-7436-QPQGE-00000002', 'context': 'C_1_ENT', 'exten': '997799298', 'priority': '1', 'state': 'Down', 'application': 'AppDial', 'app_data': '(Outgoing Line)', 'callerid_num': '997799298', 'uniqueid': '1740760337.2', 'timestamp': 1736960329.736009, 'type': 'channel', 'event': 'added'}, {'channel': 'SIP/IP-101-Q14V2-00000001', 'context': 'macro-externa', 'exten': 's', 'priority': '22', 'state': 'Ring', 'application': 'Dial', 'app_data': 'SIP/IP-7436-QPQGE/997799298,90,TtM(saida_atendimento)', 'callerid_num': '101', 'uniqueid': '1740760337.1', 'timestamp': 1736960329.736009, 'type': 'channel', 'event': 'added'}]
        data = controller.update(received_data)
        self.assertListEqual(data, expected_data)
    
    def test_update_queue_attr_changed(self):
        received_data = ['Response: Success\r\n', 'ActionID: server-00000003\r\n', 'Message: Command output follows\r\n', 'Output: \r\n', 'Output:     -= Registered Asterisk Dial Plan Hints =-\r\n', 'Output: 100@BLF_1           : SIP/IP-100-CdFaT      State:Idle     Presence:not_set         Watchers  0\r\n', 'Output: ----------------\r\n', 'Output: - 1 hints registered\r\n']
        controller = Controller()
        controller._get_peers = get_peers_test
        controller._peer_repository._entitie = PeerTest
        controller._get_channels = get_channels_test
        controller._channel_repository._entitie = ChannelTest
        controller.update(received_data)
        received_data = ['Response: Success\r\n', 'ActionID: server-00000002\r\n', 'Message: Command output follows\r\n', "Output: Queue_11 has 0 calls (max unlimited) in 'rrmemory' strategy (0s holdtime, 0s talktime), W:0, C:0, A:0, SL:0.0%, SL2:0.0% within 0s\r\n", 'Output:    Members: \r\n', 'Output:       SIP/IP-100-CdFaT (ringinuse disabled) (paused was 2930382 secs ago) (Not in use) has taken no calls yet (login was 2930362 secs ago)\r\n', 'Output:    No Callers\r\n', 'Output: \r\n', 'Output: \r\n']
        controller.update(received_data)
        received_data = ['Response: Success\r\n', 'ActionID: server-00000002\r\n', 'Message: Command output follows\r\n', "Output: Queue_11 has 0 calls (max unlimited) in 'rrmemory' strategy (40s holdtime, 180s talktime), W:0, C:0, A:0, SL:0.0%, SL2:0.0% within 0s\r\n", 'Output:    Members: \r\n', 'Output:       SIP/IP-100-CdFaT (ringinuse disabled) (paused was 2930420 secs ago) (Not in use) has taken no calls yet (login was 2934322 secs ago)\r\n', 'Output:    No Callers\r\n', 'Output: \r\n', 'Output: \r\n']
        data = controller.update(received_data)
        queue = controller.get('Queue_11', 'queue')
        member = queue.members.get('SIP/IP-100-CdFaT')
        self.assertEqual(len(data), 0)
        self.assertEqual(40, queue.wait_mean)
        self.assertEqual(180, queue.duration_mean)
        self.assertEqual(2930420, member.paused_time)
        self.assertEqual(2934322, member.logged_time)

    def test_type_peer_output(self):
        received_data = ['Response: Success\r\n', 'ActionID: server-00000003\r\n', 'Message: Command output follows\r\n', 'Output: \r\n', 'Output:     -= Registered Asterisk Dial Plan Hints =-\r\n', 'Output: 104@BLF_1           : SIP/IP-104-IJ8vP      State:Unavailable     Presence:not_set         Watchers  0\r\n', 'Output: 104@BLF_3           : SIP/IP-104-7QmO5      State:Unavailable     Presence:not_set         Watchers  0\r\n', 'Output: ----------------\r\n', 'Output: - 2 hints registered\r\n']
        expected_type = 'peer'
        controller = Controller()
        data_type = controller._get_data_type(received_data)
        self.assertEqual(data_type, expected_type)
    
    def test_type_queue_output(self):
        received_data = ['Response: Success\r\n', 'ActionID: server-00000002\r\n', 'Message: Command output follows\r\n', "Output: Queue_11 has 0 calls (max unlimited) in 'rrmemory' strategy (0s holdtime, 0s talktime), W:0, C:0, A:0, SL:0.0%, SL2:0.0% within 0s\r\n", 'Output:    Members: \r\n', 'Output:       SIP/IP-100-CdFaT (ringinuse disabled) (paused was 2930362 secs ago) (Not in use) has taken no calls yet (login was 2930362 secs ago)\r\n', 'Output:       SIP/IP-101 (ringinuse disabled) (Not in use) has taken no calls yet (login was 2930362 secs ago)\r\n', 'Output:    No Callers\r\n', 'Output: \r\n', "Output: Queue_27 has 0 calls (max unlimited) in 'rrmemory' strategy (0s holdtime, 0s talktime), W:0, C:0, A:0, SL:0.0%, SL2:0.0% within 0s\r\n", 'Output:    No Members\r\n', 'Output:    No Callers\r\n', 'Output: \r\n', "Output: Queue_44 has 0 calls (max unlimited) in 'rrmemory' strategy (0s holdtime, 0s talktime), W:0, C:0, A:0, SL:0.0%, SL2:0.0% within 0s\r\n", 'Output:    Members: \r\n', 'Output:       SIP/IP-100-boazN (ringinuse disabled) (Unavailable) has taken no calls yet (login was 2930362 secs ago)\r\n', 'Output:       SIP/IP-101-Iathq (ringinuse disabled) (Unavailable) has taken no calls yet (login was 2930362 secs ago)\r\n', 'Output:    No Callers\r\n', 'Output: \r\n', "Output: Queue_47 has 0 calls (max unlimited) in 'rrmemory' strategy (0s holdtime, 0s talktime), W:0, C:0, A:0, SL:0.0%, SL2:0.0% within 0s\r\n", 'Output:    No Members\r\n', 'Output:    No Callers\r\n', 'Output: \r\n', 'Output: \r\n']
        expected_type = 'queue'
        controller = Controller()
        data_type = controller._get_data_type(received_data)
        self.assertEqual(data_type, expected_type)
    
    def test_type_channel_output(self):
        received_data = ['Response: Success\r\n', 'ActionID: tatianno-ThinkPad-L470-00000001\r\n', 'Message: Command output follows\r\n', 'Output: SIP/IP-7436-QPQGE-00000002!C_1_ENT!997799298!1!Down!AppDial!(Outgoing Line)!997799298!3!3!3!2!!1740760337.2\r\n', 'Output: SIP/IP-101-Q14V2-00000001!macro-externa!s!22!Ring!Dial!SIP/IP-7436-QPQGE/997799298,90,TtM(saida_atendimento)!101!3!!3!2!!1740760337.1\r\n']
        expected_type = 'channel'
        controller = Controller()
        data_type = controller._get_data_type(received_data)
        self.assertEqual(data_type, expected_type)

    def test_channel_update(self):
        controller = Controller()
        controller._get_channels = get_channels_test
        controller._channel_repository._entitie = ChannelTest
        received_data = ['Response: Success\r\n', 'ActionID: tatianno-ThinkPad-L470-0000000c\r\n', 'Message: Command output follows\r\n', 'Output: \r\n']
        expected_data = []
        channels = controller.channel_update(received_data)
        self.assertListEqual(channels, expected_data)
        received_data = ['Response: Success\r\n', 'ActionID: tatianno-ThinkPad-L470-00000001\r\n', 'Message: Command output follows\r\n', 'Output: SIP/IP-7436-QPQGE-00000002!C_1_ENT!997799298!1!Down!AppDial!(Outgoing Line)!997799298!3!3!3!2!!1740760337.2\r\n', 'Output: SIP/IP-101-Q14V2-00000001!macro-externa!s!22!Ring!Dial!SIP/IP-7436-QPQGE/997799298,90,TtM(saida_atendimento)!101!3!!3!2!!1740760337.1\r\n']
        expected_data = [{'channel': 'SIP/IP-7436-QPQGE-00000002', 'context': 'C_1_ENT', 'exten': '997799298', 'priority': '1', 'state': 'Down', 'application': 'AppDial', 'app_data': '(Outgoing Line)', 'callerid_num': '997799298', 'uniqueid': '1740760337.2', 'timestamp': 1736960329.736009, 'type': 'channel', 'event': 'added'}, {'channel': 'SIP/IP-101-Q14V2-00000001', 'context': 'macro-externa', 'exten': 's', 'priority': '22', 'state': 'Ring', 'application': 'Dial', 'app_data': 'SIP/IP-7436-QPQGE/997799298,90,TtM(saida_atendimento)', 'callerid_num': '101', 'uniqueid': '1740760337.1', 'timestamp': 1736960329.736009, 'type': 'channel', 'event': 'added'}]
        channels = controller.channel_update(received_data)
        self.assertListEqual(channels, expected_data)
        received_data = ['Response: Success\r\n', 'ActionID: tatianno-ThinkPad-L470-00000001\r\n', 'Message: Command output follows\r\n', 'Output: SIP/IP-7436-QPQGE-00000002!C_1_ENT!997799298!1!Ring!AppDial!(Outgoing Line)!997799298!3!3!3!2!!1740760337.2\r\n', 'Output: SIP/IP-101-Q14V2-00000001!macro-externa!s!22!Ring!Dial!SIP/IP-7436-QPQGE/997799298,90,TtM(saida_atendimento)!101!3!!3!2!!1740760337.1\r\n']
        expected_data = [{'channel': 'SIP/IP-7436-QPQGE-00000002', 'context': 'C_1_ENT', 'exten': '997799298', 'priority': '1', 'state': 'Ring', 'application': 'AppDial', 'app_data': '(Outgoing Line)', 'callerid_num': '997799298', 'uniqueid': '1740760337.2', 'timestamp': 1736960329.736009, 'type': 'channel', 'event': 'changed'}]
        channels = controller.channel_update(received_data)
        self.assertListEqual(channels, expected_data)
        received_data = ['Response: Success\r\n', 'ActionID: tatianno-ThinkPad-L470-00000001\r\n', 'Message: Command output follows\r\n', 'Output: SIP/IP-7436-QPQGE-00000002!C_1_ENT!997799298!1!Ring!AppDial!(Outgoing Line)!997799298!3!3!3!2!!1740760337.2\r\n']
        expected_data = [{'channel': 'SIP/IP-101-Q14V2-00000001', 'type': 'channel', 'event': 'removed'}]
        channels = controller.channel_update(received_data)
        self.assertListEqual(channels, expected_data)

    def test_peer_update(self):
        received_data = ['Response: Success\r\n', 'ActionID: server-00000003\r\n', 'Message: Command output follows\r\n', 'Output: \r\n', 'Output:     -= Registered Asterisk Dial Plan Hints =-\r\n', 'Output: 104@BLF_1           : SIP/IP-104-IJ8vP      State:Unavailable     Presence:not_set         Watchers  0\r\n', 'Output: 104@BLF_3           : SIP/IP-104-7QmO5      State:Unavailable     Presence:not_set         Watchers  0\r\n', 'Output: ----------------\r\n', 'Output: - 2 hints registered\r\n']
        expected_data = [{'exten': '104', 'peername': 'SIP/IP-104-IJ8vP', 'state': 'Unavailable', 'presence': 'not_set', 'watchers': 0, 'type': 'peer', 'event': 'added', 'timestamp': 1736960329.736009 }, {'exten': '104', 'peername': 'SIP/IP-104-7QmO5', 'state': 'Unavailable', 'presence': 'not_set', 'watchers': 0, 'type': 'peer', 'event': 'added', 'timestamp': 1736960329.736009 }]
        controller = Controller()
        controller._get_peers = get_peers_test
        controller._peer_repository._entitie = PeerTest
        peers = controller.peer_update(received_data)
        self.assertListEqual(peers, expected_data)
        received_data = ['Response: Success\r\n', 'ActionID: server-00000003\r\n', 'Message: Command output follows\r\n', 'Output: \r\n', 'Output:     -= Registered Asterisk Dial Plan Hints =-\r\n', 'Output: 104@BLF_1           : SIP/IP-104-IJ8vP      State:Unavailable     Presence:not_set         Watchers  0\r\n', 'Output: 104@BLF_3           : SIP/IP-104-7QmO5      State:Unavailable     Presence:not_set         Watchers  0\r\n', 'Output: ----------------\r\n', 'Output: - 2 hints registered\r\n']
        expected_data = []
        peers = controller.peer_update(received_data)
        self.assertListEqual(peers, expected_data)
        received_data = ['Response: Success\r\n', 'ActionID: server-00000003\r\n', 'Message: Command output follows\r\n', 'Output: \r\n', 'Output:     -= Registered Asterisk Dial Plan Hints =-\r\n', 'Output: 104@BLF_1           : SIP/IP-104-IJ8vP      State:Idle     Presence:not_set         Watchers  0\r\n', 'Output: 104@BLF_3           : SIP/IP-104-7QmO5      State:Unavailable     Presence:not_set         Watchers  0\r\n', 'Output: ----------------\r\n', 'Output: - 2 hints registered\r\n']
        expected_data = [{'exten': '104', 'peername': 'SIP/IP-104-IJ8vP', 'state': 'Idle', 'presence': 'not_set', 'watchers': 0, 'type': 'peer', 'event': 'changed', 'timestamp': 1736960329.736009}]
        peers = controller.peer_update(received_data)
        self.assertListEqual(peers, expected_data)
        received_data = ['Response: Success\r\n', 'ActionID: server-00000003\r\n', 'Message: Command output follows\r\n', 'Output: \r\n', 'Output:     -= Registered Asterisk Dial Plan Hints =-\r\n', 'Output: 104@BLF_1           : SIP/IP-104-IJ8vP      State:Idle     Presence:not_set         Watchers  0\r\n', 'Output: ----------------\r\n', 'Output: - 1 hints registered\r\n']
        expected_data = [{'peername': 'SIP/IP-104-7QmO5', 'type': 'peer', 'event': 'removed'}]
        peers = controller.peer_update(received_data)
        self.assertEqual(peers, expected_data)
        received_data = ['Response: Success\r\n', 'ActionID: server-00000003\r\n', 'Message: Command output follows\r\n', 'Output: \r\n', 'Output:     -= Registered Asterisk Dial Plan Hints =-\r\n', 'Output: 104@BLF_1           : SIP/IP-104-IJ8vP      State:Inuse     Presence:not_set         Watchers  0\r\n', 'Output: ----------------\r\n', 'Output: - 1 hints registered\r\n']
        expected_data = [{'exten': '104', 'peername': 'SIP/IP-104-IJ8vP', 'state': 'Inuse', 'presence': 'not_set', 'watchers': 0, 'type': 'peer', 'event': 'changed', 'timestamp': 1736960329.736009}]
        peers = controller.peer_update(received_data)
        self.assertEqual(peers, expected_data)

    def test_queue_update(self):
        received_data = ['Response: Success\r\n', 'ActionID: server-00000002\r\n', 'Message: Command output follows\r\n', "Output: Queue_11 has 0 calls (max unlimited) in 'rrmemory' strategy (0s holdtime, 0s talktime), W:0, C:0, A:0, SL:0.0%, SL2:0.0% within 0s\r\n", 'Output:    Members: \r\n', 'Output:       SIP/IP-100-CdFaT (ringinuse disabled) (paused was 2930362 secs ago) (Not in use) has taken no calls yet (login was 2930362 secs ago)\r\n', 'Output:       SIP/IP-101 (ringinuse disabled) (Not in use) has taken no calls yet (login was 2930362 secs ago)\r\n', 'Output:    No Callers\r\n', 'Output: \r\n', "Output: Queue_27 has 0 calls (max unlimited) in 'rrmemory' strategy (0s holdtime, 0s talktime), W:0, C:0, A:0, SL:0.0%, SL2:0.0% within 0s\r\n", 'Output:    No Members\r\n', 'Output:    No Callers\r\n', 'Output: \r\n', "Output: Queue_44 has 0 calls (max unlimited) in 'rrmemory' strategy (0s holdtime, 0s talktime), W:0, C:0, A:0, SL:0.0%, SL2:0.0% within 0s\r\n", 'Output:    Members: \r\n', 'Output:       SIP/IP-100-boazN (ringinuse disabled) (Unavailable) has taken no calls yet (login was 2930362 secs ago)\r\n', 'Output:       SIP/IP-101-Iathq (ringinuse disabled) (Unavailable) has taken no calls yet (login was 2930362 secs ago)\r\n', 'Output:    No Callers\r\n', 'Output: \r\n', "Output: Queue_47 has 0 calls (max unlimited) in 'rrmemory' strategy (0s holdtime, 0s talktime), W:0, C:0, A:0, SL:0.0%, SL2:0.0% within 0s\r\n", 'Output:    No Members\r\n', 'Output:    No Callers\r\n', 'Output: \r\n', 'Output: \r\n']
        expected_data = [{'queuename': 'Queue_11', 'total_calls': 0, 'strategy': 'rrmemory', 'wait_mean': 0, 'duration_mean': 0, 'total_wait_calls': 0, 'total_completed_calls': 0, 'total_abandoned_calls': 0, 'members': [{'name': 'SIP/IP-100-CdFaT', 'has_paused': True, 'reason_paused': None, 'dynamic': None, 'in_call': False, 'paused_time': 2930362, 'logged_time': 2930362, 'total_calls': 0, 'last_call_time': 0, 'type': 'member'}, {'name': 'SIP/IP-101', 'has_paused': False, 'reason_paused': None, 'dynamic': None, 'in_call': False, 'paused_time': 0, 'logged_time': 2930362, 'total_calls': 0, 'last_call_time': 0, 'type': 'member'}], 'waiting_calls': [], 'type': 'queue', 'event': 'added'}, {'queuename': 'Queue_27', 'total_calls': 0, 'strategy': 'rrmemory', 'wait_mean': 0, 'duration_mean': 0, 'total_wait_calls': 0, 'total_completed_calls': 0, 'total_abandoned_calls': 0, 'members': [], 'waiting_calls': [], 'type': 'queue', 'event': 'added'}, {'queuename': 'Queue_44', 'total_calls': 0, 'strategy': 'rrmemory', 'wait_mean': 0, 'duration_mean': 0, 'total_wait_calls': 0, 'total_completed_calls': 0, 'total_abandoned_calls': 0, 'members': [{'name': 'SIP/IP-100-boazN', 'has_paused': False, 'reason_paused': None, 'dynamic': None, 'in_call': False, 'paused_time': 0, 'logged_time': 2930362, 'total_calls': 0, 'last_call_time': 0, 'type': 'member'}, {'name': 'SIP/IP-101-Iathq', 'has_paused': False, 'reason_paused': None, 'dynamic': None, 'in_call': False, 'paused_time': 0, 'logged_time': 2930362, 'total_calls': 0, 'last_call_time': 0, 'type': 'member'}], 'waiting_calls': [], 'type': 'queue', 'event': 'added'}, {'queuename': 'Queue_47', 'total_calls': 0, 'strategy': 'rrmemory', 'wait_mean': 0, 'duration_mean': 0, 'total_wait_calls': 0, 'total_completed_calls': 0, 'total_abandoned_calls': 0, 'members': [], 'waiting_calls': [], 'type': 'queue', 'event': 'added'}]
        controller = Controller()
        queues = controller.queue_update(received_data)
        self.assertListEqual(queues, expected_data)
        received_data = ['Response: Success\r\n', 'ActionID: server-00000002\r\n', 'Message: Command output follows\r\n', "Output: Queue_11 has 0 calls (max unlimited) in 'rrmemory' strategy (0s holdtime, 0s talktime), W:0, C:0, A:0, SL:0.0%, SL2:0.0% within 0s\r\n", 'Output:    Members: \r\n', 'Output:       SIP/IP-101 (ringinuse disabled) (Not in use) has taken no calls yet (login was 2930362 secs ago)\r\n', 'Output:    No Callers\r\n', 'Output: \r\n', "Output: Queue_27 has 0 calls (max unlimited) in 'rrmemory' strategy (0s holdtime, 0s talktime), W:0, C:0, A:0, SL:0.0%, SL2:0.0% within 0s\r\n", 'Output:    No Members\r\n', 'Output:    No Callers\r\n', 'Output: \r\n', "Output: Queue_44 has 0 calls (max unlimited) in 'rrmemory' strategy (0s holdtime, 0s talktime), W:0, C:0, A:0, SL:0.0%, SL2:0.0% within 0s\r\n", 'Output:    Members: \r\n', 'Output:       SIP/IP-100-boazN (ringinuse disabled) (Unavailable) has taken no calls yet (login was 2930362 secs ago)\r\n', 'Output:       SIP/IP-101-Iathq (ringinuse disabled) (Unavailable) has taken no calls yet (login was 2930362 secs ago)\r\n', 'Output:    No Callers\r\n', 'Output: \r\n', "Output: Queue_47 has 0 calls (max unlimited) in 'rrmemory' strategy (0s holdtime, 0s talktime), W:0, C:0, A:0, SL:0.0%, SL2:0.0% within 0s\r\n", 'Output:    No Members\r\n', 'Output:    No Callers\r\n', 'Output: \r\n', 'Output: \r\n']        
        expected_data = [{'queuename': 'Queue_11', 'total_calls': 0, 'strategy': 'rrmemory', 'wait_mean': 0, 'duration_mean': 0, 'total_wait_calls': 0, 'total_completed_calls': 0, 'total_abandoned_calls': 0, 'members': [{'name': 'SIP/IP-101', 'has_paused': False, 'reason_paused': None, 'dynamic': None, 'in_call': False, 'paused_time': 0, 'logged_time': 2930362, 'total_calls': 0, 'last_call_time': 0, 'type': 'member'}], 'waiting_calls': [], 'type': 'queue', 'event': 'changed'}]
        queues = controller.queue_update(received_data)
        self.assertListEqual(queues, expected_data)
        received_data = ['Response: Success\r\n', 'ActionID: server-00000002\r\n', 'Message: Command output follows\r\n', "Output: Queue_27 has 0 calls (max unlimited) in 'rrmemory' strategy (0s holdtime, 0s talktime), W:0, C:0, A:0, SL:0.0%, SL2:0.0% within 0s\r\n", 'Output:    No Members\r\n', 'Output:    No Callers\r\n', 'Output: \r\n', "Output: Queue_44 has 0 calls (max unlimited) in 'rrmemory' strategy (0s holdtime, 0s talktime), W:0, C:0, A:0, SL:0.0%, SL2:0.0% within 0s\r\n", 'Output:    Members: \r\n', 'Output:       SIP/IP-100-boazN (ringinuse disabled) (Unavailable) has taken no calls yet (login was 2930362 secs ago)\r\n', 'Output:       SIP/IP-101-Iathq (ringinuse disabled) (Unavailable) has taken no calls yet (login was 2930362 secs ago)\r\n', 'Output:    No Callers\r\n', 'Output: \r\n', "Output: Queue_47 has 0 calls (max unlimited) in 'rrmemory' strategy (0s holdtime, 0s talktime), W:0, C:0, A:0, SL:0.0%, SL2:0.0% within 0s\r\n", 'Output:    No Members\r\n', 'Output:    No Callers\r\n', 'Output: \r\n', 'Output: \r\n']        
        expected_data = [{'queuename': 'Queue_11', 'type': 'queue', 'event': 'removed'}]
        queues = controller.queue_update(received_data)
        self.assertListEqual(queues, expected_data)

    
    def test_set_members_queues(self):
        received_data = ['Response: Success\r\n', 'ActionID: server-00000002\r\n', 'Message: Command output follows\r\n', "Output: Queue_11 has 0 calls (max unlimited) in 'rrmemory' strategy (0s holdtime, 0s talktime), W:0, C:0, A:0, SL:0.0%, SL2:0.0% within 0s\r\n", 'Output:    Members: \r\n', 'Output:       SIP/IP-100-CdFaT (ringinuse disabled) (paused was 2930362 secs ago) (Not in use) has taken no calls yet (login was 2930362 secs ago)\r\n', 'Output:       SIP/IP-101 (ringinuse disabled) (Not in use) has taken no calls yet (login was 2930362 secs ago)\r\n', 'Output:    No Callers\r\n', 'Output: \r\n', "Output: Queue_27 has 0 calls (max unlimited) in 'rrmemory' strategy (0s holdtime, 0s talktime), W:0, C:0, A:0, SL:0.0%, SL2:0.0% within 0s\r\n", 'Output:    Members: \r\n', 'Output:       SIP/IP-100-CdFaT (ringinuse disabled) (paused was 2930362 secs ago) (Not in use) has taken no calls yet (login was 2930362 secs ago)\r\n', 'Output:    No Callers\r\n', 'Output: \r\n', "Output: Queue_44 has 0 calls (max unlimited) in 'rrmemory' strategy (0s holdtime, 0s talktime), W:0, C:0, A:0, SL:0.0%, SL2:0.0% within 0s\r\n", 'Output:    Members: \r\n', 'Output:       SIP/IP-100-boazN (ringinuse disabled) (Unavailable) has taken no calls yet (login was 2930362 secs ago)\r\n', 'Output:       SIP/IP-101-Iathq (ringinuse disabled) (Unavailable) has taken no calls yet (login was 2930362 secs ago)\r\n', 'Output:    No Callers\r\n', 'Output: \r\n', "Output: Queue_47 has 0 calls (max unlimited) in 'rrmemory' strategy (0s holdtime, 0s talktime), W:0, C:0, A:0, SL:0.0%, SL2:0.0% within 0s\r\n", 'Output:    No Members\r\n', 'Output:    No Callers\r\n', 'Output: \r\n', 'Output: \r\n']
        expected_data = {
            'SIP/IP-100-CdFaT': ['Queue_11', 'Queue_27'],
            'SIP/IP-101': ['Queue_11'],
            'SIP/IP-100-boazN': ['Queue_44'],
            'SIP/IP-101-Iathq': ['Queue_44']
        }
        controller = Controller()
        parser_data = controller._queue_parser.get_data(received_data)
        controller.set_list_queues_from_members(parser_data)
        self.assertDictEqual(controller._queues_members_dict, expected_data)
        received_data = ['Response: Success\r\n', 'ActionID: server-00000002\r\n', 'Message: Command output follows\r\n', "Output: Queue_11 has 0 calls (max unlimited) in 'rrmemory' strategy (0s holdtime, 0s talktime), W:0, C:0, A:0, SL:0.0%, SL2:0.0% within 0s\r\n", 'Output:    Members: \r\n', 'Output:       SIP/IP-100-CdFaT (ringinuse disabled) (paused was 2930362 secs ago) (Not in use) has taken no calls yet (login was 2930362 secs ago)\r\n', 'Output:       SIP/IP-101 (ringinuse disabled) (Not in use) has taken no calls yet (login was 2930362 secs ago)\r\n', 'Output:    No Callers\r\n', 'Output: \r\n', "Output: Queue_27 has 0 calls (max unlimited) in 'rrmemory' strategy (0s holdtime, 0s talktime), W:0, C:0, A:0, SL:0.0%, SL2:0.0% within 0s\r\n", 'Output:    Members: \r\n', 'Output:       SIP/IP-100-CdFaT (ringinuse disabled) (paused was 2930362 secs ago) (Not in use) has taken no calls yet (login was 2930362 secs ago)\r\n', 'Output:    No Callers\r\n', 'Output: \r\n', 'Output: \r\n']
        expected_data = {
            'SIP/IP-100-CdFaT': ['Queue_11', 'Queue_27'],
            'SIP/IP-101': ['Queue_11']
        }
        parser_data = controller._queue_parser.get_data(received_data)
        controller.set_list_queues_from_members(parser_data)
        self.assertDictEqual(controller._queues_members_dict, expected_data)
        
    def test_get_members_queues(self):
        received_data = ['Response: Success\r\n', 'ActionID: server-00000002\r\n', 'Message: Command output follows\r\n', "Output: Queue_11 has 0 calls (max unlimited) in 'rrmemory' strategy (0s holdtime, 0s talktime), W:0, C:0, A:0, SL:0.0%, SL2:0.0% within 0s\r\n", 'Output:    Members: \r\n', 'Output:       SIP/IP-100-CdFaT (ringinuse disabled) (paused was 2930362 secs ago) (Not in use) has taken no calls yet (login was 2930362 secs ago)\r\n', 'Output:       SIP/IP-101 (ringinuse disabled) (Not in use) has taken no calls yet (login was 2930362 secs ago)\r\n', 'Output:    No Callers\r\n', 'Output: \r\n', "Output: Queue_27 has 0 calls (max unlimited) in 'rrmemory' strategy (0s holdtime, 0s talktime), W:0, C:0, A:0, SL:0.0%, SL2:0.0% within 0s\r\n", 'Output:    Members: \r\n', 'Output:       SIP/IP-100-CdFaT (ringinuse disabled) (paused was 2930362 secs ago) (Not in use) has taken no calls yet (login was 2930362 secs ago)\r\n', 'Output:    No Callers\r\n', 'Output: \r\n', "Output: Queue_44 has 0 calls (max unlimited) in 'rrmemory' strategy (0s holdtime, 0s talktime), W:0, C:0, A:0, SL:0.0%, SL2:0.0% within 0s\r\n", 'Output:    Members: \r\n', 'Output:       SIP/IP-100-boazN (ringinuse disabled) (Unavailable) has taken no calls yet (login was 2930362 secs ago)\r\n', 'Output:       SIP/IP-101-Iathq (ringinuse disabled) (Unavailable) has taken no calls yet (login was 2930362 secs ago)\r\n', 'Output:    No Callers\r\n', 'Output: \r\n', "Output: Queue_47 has 0 calls (max unlimited) in 'rrmemory' strategy (0s holdtime, 0s talktime), W:0, C:0, A:0, SL:0.0%, SL2:0.0% within 0s\r\n", 'Output:    No Members\r\n', 'Output:    No Callers\r\n', 'Output: \r\n', 'Output: \r\n']
        expected_data = ['Queue_11', 'Queue_27']
        controller = Controller()
        controller.queue_update(received_data)
        self.assertListEqual(
            controller.get_list_queues_from_a_peer('SIP/IP-100-CdFaT'),
            expected_data
        )

    def test_get_peer(self):
        received_data = ['Response: Success\r\n', 'ActionID: server-00000003\r\n', 'Message: Command output follows\r\n', 'Output: \r\n', 'Output:     -= Registered Asterisk Dial Plan Hints =-\r\n', 'Output: 104@BLF_1           : SIP/IP-104-IJ8vP      State:Unavailable     Presence:not_set         Watchers  0\r\n', 'Output: 104@BLF_3           : SIP/IP-104-7QmO5      State:Unavailable     Presence:not_set         Watchers  0\r\n', 'Output: ----------------\r\n', 'Output: - 2 hints registered\r\n']
        controller = Controller()
        controller.peer_update(received_data)
        peer = controller.get('SIP/IP-104-IJ8vP', 'peer')
        self.assertEqual(peer.peername, 'SIP/IP-104-IJ8vP')
    
    def test_get_queue(self):
        received_data = ['Response: Success\r\n', 'ActionID: server-00000002\r\n', 'Message: Command output follows\r\n', "Output: Queue_11 has 0 calls (max unlimited) in 'rrmemory' strategy (0s holdtime, 0s talktime), W:0, C:0, A:0, SL:0.0%, SL2:0.0% within 0s\r\n", 'Output:    Members: \r\n', 'Output:       SIP/IP-100-CdFaT (ringinuse disabled) (paused was 2930362 secs ago) (Not in use) has taken no calls yet (login was 2930362 secs ago)\r\n', 'Output:       SIP/IP-101 (ringinuse disabled) (Not in use) has taken no calls yet (login was 2930362 secs ago)\r\n', 'Output:    No Callers\r\n', 'Output: \r\n', "Output: Queue_27 has 0 calls (max unlimited) in 'rrmemory' strategy (0s holdtime, 0s talktime), W:0, C:0, A:0, SL:0.0%, SL2:0.0% within 0s\r\n", 'Output:    No Members\r\n', 'Output:    No Callers\r\n', 'Output: \r\n', "Output: Queue_44 has 0 calls (max unlimited) in 'rrmemory' strategy (0s holdtime, 0s talktime), W:0, C:0, A:0, SL:0.0%, SL2:0.0% within 0s\r\n", 'Output:    Members: \r\n', 'Output:       SIP/IP-100-boazN (ringinuse disabled) (Unavailable) has taken no calls yet (login was 2930362 secs ago)\r\n', 'Output:       SIP/IP-101-Iathq (ringinuse disabled) (Unavailable) has taken no calls yet (login was 2930362 secs ago)\r\n', 'Output:    No Callers\r\n', 'Output: \r\n', "Output: Queue_47 has 0 calls (max unlimited) in 'rrmemory' strategy (0s holdtime, 0s talktime), W:0, C:0, A:0, SL:0.0%, SL2:0.0% within 0s\r\n", 'Output:    No Members\r\n', 'Output:    No Callers\r\n', 'Output: \r\n', 'Output: \r\n']
        controller = Controller()
        controller.queue_update(received_data)
        queue = controller.get('Queue_11', 'queue')
        self.assertEqual(queue.queuename, 'Queue_11')
    
    def test_get_channel(self):
        received_data = ['Response: Success\r\n', 'ActionID: tatianno-ThinkPad-L470-00000001\r\n', 'Message: Command output follows\r\n', 'Output: SIP/IP-7436-QPQGE-00000002!C_1_ENT!997799298!1!Down!AppDial!(Outgoing Line)!997799298!3!3!3!2!!1740760337.2\r\n', 'Output: SIP/IP-101-Q14V2-00000001!macro-externa!s!22!Ring!Dial!SIP/IP-7436-QPQGE/997799298,90,TtM(saida_atendimento)!101!3!!3!2!!1740760337.1\r\n']
        controller = Controller()
        controller.channel_update(received_data)
        channel = controller.get('SIP/IP-7436-QPQGE-00000002', 'channel')
        self.assertEqual(channel.channel, 'SIP/IP-7436-QPQGE-00000002')
    
    def test_get_invalid_type(self):
        controller = Controller()
        self.assertRaises(
            TypeError,
            controller.get,
            'Queue_11', 
            'queue1'
        )
    
    def test_get_peer_not_exists_raise_exception(self):
        controller = Controller()
        self.assertRaises(
            Peer.DoesExists,
            controller.get,
            'SIP/IP-104-IJ8vP', 
            'peer',
            raise_exception=True
        )
    
    def test_get_queue_not_exists_raise_exception(self):
        controller = Controller()
        self.assertRaises(
            Queue.DoesExists,
            controller.get,
            'Queue_11', 
            'queue',
            raise_exception=True
        )

    def test_get_peer_not_exists(self):
        controller = Controller()
        queue = controller.get('SIP/IP-104', 'peer')
        self.assertIsNone(queue)
    
    def test_get_queue_not_exists(self):
        controller = Controller()
        queue = controller.get('Queue_11', 'queue')
        self.assertIsNone(queue)
    
    def test_get_channel_not_exists(self):
        controller = Controller()
        channel = controller.get('SIP/IP-100-29038', 'channel')
        self.assertIsNone(channel)