from unittest import TestCase
from ami_data_parser.parser.utils import set_output_format


class ParserUtilsTestCase(TestCase):

    def test_set_output_format(self):
        received_line = 'Response: Follows\r\n'
        expected_data = 'Response: Follows\r\n'
        data = set_output_format(received_line)
        self.assertEqual(data, expected_data)
        received_line = 'Privilege: Command\r\n'
        expected_data = 'Privilege: Command\r\n'
        data = set_output_format(received_line)
        self.assertEqual(data, expected_data)
        received_line = 'ActionID: pbx-jhf-00000029\r\n'
        expected_data = 'ActionID: pbx-jhf-00000029\r\n'
        data = set_output_format(received_line)
        self.assertEqual(data, expected_data)
        received_line = "Queue_110 has 6 calls (max unlimited) in 'rrmemory' strategy (45s holdtime, 310s talktime), W:0, C:124, A:242, SL:0.0% within 0s\n"
        expected_data = "Output:    Queue_110 has 6 calls (max unlimited) in 'rrmemory' strategy (45s holdtime, 310s talktime), W:0, C:124, A:242, SL:0.0% within 0s\n"
        data = set_output_format(received_line)
        self.assertEqual(data, expected_data)
        received_line = '--END COMMAND--\r\n'
        expected_data = '--END COMMAND--\r\n'
        data = set_output_format(received_line)
        self.assertEqual(data, expected_data)
        received_line = 'Message: Command output follows\r\n'
        expected_data = 'Message: Command output follows\r\n'
        data = set_output_format(received_line)
        self.assertEqual(data, expected_data)