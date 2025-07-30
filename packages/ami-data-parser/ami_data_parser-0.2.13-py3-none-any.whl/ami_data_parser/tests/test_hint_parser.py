from unittest import TestCase
from ami_data_parser.parser.hint_parser import HintParser


class HintParserTestCase(TestCase):

    def test_get_data(self):
        received_data = ['Response: Success\r\n', 'ActionID: server-00000003\r\n', 'Message: Command output follows\r\n', 'Output: \r\n', 'Output:     -= Registered Asterisk Dial Plan Hints =-\r\n', 'Output: 104@BLF_1           : SIP/IP-104-IJ8vP      State:Unavailable     Presence:not_set         Watchers  0\r\n', 'Output: 104@BLF_3           : SIP/IP-104-7QmO5      State:Unavailable     Presence:not_set         Watchers  0\r\n', 'Output: 105@BLF_1           : SIP/IP-105-rrPi8      State:Unavailable     Presence:not_set         Watchers  0\r\n', 'Output: 105@BLF_3           : SIP/IP-105-3RhNF      State:Unavailable     Presence:not_set         Watchers  0\r\n', 'Output: 106@BLF_1           : SIP/IP-106-Y6NcH      State:Unavailable     Presence:not_set         Watchers  0\r\n', 'Output: 106@BLF_3           : SIP/IP-106-HhV1H      State:Unavailable     Presence:not_set         Watchers  0\r\n', 'Output: 107@BLF_1           : SIP/IP-107-s7TbL      State:Unavailable     Presence:not_set         Watchers  0\r\n', 'Output: 107@BLF_3           : SIP/IP-107-RLZp1      State:Unavailable     Presence:not_set         Watchers  0\r\n', 'Output: 100@BLF_1           : SIP/IP-100-CdFaT      State:Idle            Presence:not_set         Watchers  0\r\n', 'Output: 100@BLF_3           : SIP/IP-100-boazN      State:Unavailable     Presence:not_set         Watchers  0\r\n', 'Output: 101@BLF_1           : SIP/IP-101            State:Idle            Presence:not_set         Watchers  0\r\n', 'Output: 102@BLF_3           : SIP/IP-102-wlJsG      State:Unavailable     Presence:not_set         Watchers  0\r\n', 'Output: 103@BLF_1           : SIP/IP-103-DFiZ3      State:Unavailable     Presence:not_set         Watchers  0\r\n', 'Output: 103@BLF_3           : SIP/IP-103-Hdqsq      State:Unavailable     Presence:not_set         Watchers  0\r\n', 'Output: 108@BLF_3           : SIP/IP-108-RIIuq      State:Unavailable     Presence:not_set         Watchers  0\r\n', 'Output: 109@BLF_1           : SIP/IP-109            State:Unavailable     Presence:not_set         Watchers  0\r\n', 'Output: 109@BLF_3           : SIP/IP-109-fiMZ4      State:Unavailable     Presence:not_set         Watchers  0\r\n', 'Output: 201@BLF_3           : SIP/IP-101-Iathq      State:Unavailable     Presence:not_set         Watchers  0\r\n', 'Output: 1000@demo           : SIP/1000              State:Unavailable     Presence:not_set         Watchers  0\r\n', 'Output: 1001@demo           : SIP/1001              State:Unavailable     Presence:not_set         Watchers  0\r\n', 'Output: 1234@default        : SIP/1234              State:Unavailable     Presence:not_set         Watchers  0\r\n', 'Output: 7444@BLF_1          : SIP/IPHmfsz           State:Unavailable     Presence:not_set         Watchers  0\r\n', 'Output: ----------------\r\n', 'Output: - 22 hints registered\r\n']
        expected_data = [{'exten': '104', 'peername': 'SIP/IP-104-IJ8vP', 'state': 'Unavailable', 'presence': 'not_set', 'watchers': 0}, {'exten': '104', 'peername': 'SIP/IP-104-7QmO5', 'state': 'Unavailable', 'presence': 'not_set', 'watchers': 0}, {'exten': '105', 'peername': 'SIP/IP-105-rrPi8', 'state': 'Unavailable', 'presence': 'not_set', 'watchers': 0}, {'exten': '105', 'peername': 'SIP/IP-105-3RhNF', 'state': 'Unavailable', 'presence': 'not_set', 'watchers': 0}, {'exten': '106', 'peername': 'SIP/IP-106-Y6NcH', 'state': 'Unavailable', 'presence': 'not_set', 'watchers': 0}, {'exten': '106', 'peername': 'SIP/IP-106-HhV1H', 'state': 'Unavailable', 'presence': 'not_set', 'watchers': 0}, {'exten': '107', 'peername': 'SIP/IP-107-s7TbL', 'state': 'Unavailable', 'presence': 'not_set', 'watchers': 0}, {'exten': '107', 'peername': 'SIP/IP-107-RLZp1', 'state': 'Unavailable', 'presence': 'not_set', 'watchers': 0}, {'exten': '100', 'peername': 'SIP/IP-100-CdFaT', 'state': 'Idle', 'presence': 'not_set', 'watchers': 0}, {'exten': '100', 'peername': 'SIP/IP-100-boazN', 'state': 'Unavailable', 'presence': 'not_set', 'watchers': 0}, {'exten': '101', 'peername': 'SIP/IP-101', 'state': 'Idle', 'presence': 'not_set', 'watchers': 0}, {'exten': '102', 'peername': 'SIP/IP-102-wlJsG', 'state': 'Unavailable', 'presence': 'not_set', 'watchers': 0}, {'exten': '103', 'peername': 'SIP/IP-103-DFiZ3', 'state': 'Unavailable', 'presence': 'not_set', 'watchers': 0}, {'exten': '103', 'peername': 'SIP/IP-103-Hdqsq', 'state': 'Unavailable', 'presence': 'not_set', 'watchers': 0}, {'exten': '108', 'peername': 'SIP/IP-108-RIIuq', 'state': 'Unavailable', 'presence': 'not_set', 'watchers': 0}, {'exten': '109', 'peername': 'SIP/IP-109', 'state': 'Unavailable', 'presence': 'not_set', 'watchers': 0}, {'exten': '109', 'peername': 'SIP/IP-109-fiMZ4', 'state': 'Unavailable', 'presence': 'not_set', 'watchers': 0}, {'exten': '201', 'peername': 'SIP/IP-101-Iathq', 'state': 'Unavailable', 'presence': 'not_set', 'watchers': 0}, {'exten': '1000', 'peername': 'SIP/1000', 'state': 'Unavailable', 'presence': 'not_set', 'watchers': 0}, {'exten': '1001', 'peername': 'SIP/1001', 'state': 'Unavailable', 'presence': 'not_set', 'watchers': 0}, {'exten': '1234', 'peername': 'SIP/1234', 'state': 'Unavailable', 'presence': 'not_set', 'watchers': 0}, {'exten': '7444', 'peername': 'SIP/IPHmfsz', 'state': 'Unavailable', 'presence': 'not_set', 'watchers': 0}]
        hint_parser = HintParser()
        data = hint_parser.get_data(received_data)
        self.assertListEqual(data, expected_data)
    
    def test_get_data_without_output_word(self):
        received_data = ['Response: Follows\r\n', 'Privilege: Command\r\n', 'ActionID: pbx-jhf-00000028\r\n', '\n', '    -= Registered Asterisk Dial Plan Hints =-\n', '237@BLF_2           : SIP/237-IPe9AAl       State:Idle            Presence:not_set         Watchers  0\n', '104@BLF_2           : SIP/104-IPnc3MM       State:Unavailable     Presence:not_set         Watchers  0\n', '105@BLF_2           : SIP/105-IPCZncL       State:Idle            Presence:not_set         Watchers  0\n', '----------------\n', '- 3 hints registered\n', '--END COMMAND--\r\n']
        expected_data = [{'exten': '237', 'peername': 'SIP/237-IPe9AAl', 'state': 'Idle', 'presence': 'not_set', 'watchers': 0}, {'exten': '104', 'peername': 'SIP/104-IPnc3MM', 'state': 'Unavailable', 'presence': 'not_set', 'watchers': 0}, {'exten': '105', 'peername': 'SIP/105-IPCZncL', 'state': 'Idle', 'presence': 'not_set', 'watchers': 0}]
        hint_parser = HintParser()
        data = hint_parser.get_data(received_data)
        self.assertListEqual(data, expected_data)

    def test_get_parser_hint(self):
        received_data = 'Output: 104@BLF_1           : SIP/IP-104-IJ8vP      State:Unavailable     Presence:not_set         Watchers  0\r\n'
        expected_data = {
            'exten': '104',
            'peername': 'SIP/IP-104-IJ8vP',
            'state': 'Unavailable',
            'presence': 'not_set',
            'watchers': 0
        }
        hint_parser = HintParser()
        data = hint_parser._get_parser_hint(received_data)
        self.assertDictEqual(data, expected_data)

    def test_get_parser_hint_without_output_word(self):
        received_data = '237@BLF_2           : SIP/237-IPe9AAl       State:Idle            Presence:not_set         Watchers  0\n'
        expected_data = {
            'exten': '237', 
            'peername': 'SIP/237-IPe9AAl', 
            'state': 'Idle', 
            'presence': 'not_set', 
            'watchers': 0
        }
        hint_parser = HintParser()
        data = hint_parser._get_parser_hint(received_data)
        self.assertDictEqual(data, expected_data)

    def test_get_exten(self):
        received_data = 'Output: 104@BLF_1           : SIP/IP-104-IJ8vP      State:Unavailable     Presence:not_set         Watchers  0\r\n'
        hint_parser = HintParser()
        exten = hint_parser._get_exten(received_data)
        self.assertEqual(exten, '104')
    
    def test_get_peername(self):
        received_data = 'Output: 104@BLF_1           : SIP/IP-104-IJ8vP      State:Unavailable     Presence:not_set         Watchers  0\r\n'
        hint_parser = HintParser()
        peername = hint_parser._get_peername(received_data)
        self.assertEqual(peername, 'SIP/IP-104-IJ8vP')
    
    def test_get_state(self):
        received_data = 'Output: 104@BLF_1           : SIP/IP-104-IJ8vP      State:Unavailable     Presence:not_set         Watchers  0\r\n'
        hint_parser = HintParser()
        state = hint_parser._get_state(received_data)
        self.assertEqual(state, 'Unavailable')
    
    def test_get_state(self):
        received_data = 'Output: 104@BLF_1           : SIP/IP-104-IJ8vP      State:Unavailable     Presence:not_set         Watchers  0\r\n'
        hint_parser = HintParser()
        state = hint_parser._get_state(received_data)
        self.assertEqual(state, 'Unavailable')
    
    def test_get_presence(self):
        received_data = 'Output: 104@BLF_1           : SIP/IP-104-IJ8vP      State:Unavailable     Presence:not_set         Watchers  0\r\n'
        hint_parser = HintParser()
        presence = hint_parser._get_presence(received_data)
        self.assertEqual(presence, 'not_set')
    
    def test_get_watchers(self):
        received_data = 'Output: 104@BLF_1           : SIP/IP-104-IJ8vP      State:Unavailable     Presence:not_set         Watchers  0\r\n'
        hint_parser = HintParser()
        watchers = hint_parser._get_watchers(received_data)
        self.assertEqual(watchers, 0)