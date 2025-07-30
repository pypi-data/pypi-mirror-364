from ami_data_parser.parser.utils import set_output_format


class ChannelParser:

    def get_data(self, lines: list) -> list:
        channels_data = []

        for line in lines:
            line = set_output_format(line)
            channel_data = self._get_parser_channel(line)

            if channel_data:
                channels_data.append(channel_data)
        
        return channels_data

    def _get_parser_channel(self, line: str) -> dict:

        if 'Output:' not in line or 'Output: \r\n'  in line:
            return None 
        
        data = self._get_data_list(line)
        return {
            'channel': self._get_channel(data),
            'context': self._get_context(data),
            'exten': self._get_exten(data),
            'priority': self._get_priority(data),
            'state': self._get_state(data),
            'application': self._get_application(data),
            'app_data': self._get_app_data(data),
            'callerid_num': self._get_callerid_num(data),
            'uniqueid': self._get_uniqueid(data)
        }
    
    def _get_channel(self, data: list) -> str:
        return self._get_value_in_list(data, 0)
    
    def _get_context(self, data: list) -> str:
        return self._get_value_in_list(data, 1)
    
    def _get_exten(self, data: list) -> str:
        return self._get_value_in_list(data, 2)
    
    def _get_priority(self, data: list) -> str:
        return self._get_value_in_list(data, 3)
    
    def _get_state(self, data: list) -> str:
        return self._get_value_in_list(data, 4)
    
    def _get_application(self, data: list) -> str:
        return self._get_value_in_list(data, 5)
    
    def _get_app_data(self, data: list) -> str:
        return self._get_value_in_list(data, 6)
    
    def _get_callerid_num(self, data: list) -> str:
        return self._get_value_in_list(data, 7)
    
    def _get_uniqueid(self, data: list) -> str:
        return self._get_value_in_list(data, 13)

    def _get_data_list(self, line: str) -> list:
        line = self._clean_data(line)
        return line.split('!')
    
    def _clean_data(self, line: str) -> str:
        remove_itens = ['Output:', '\r', '\n']

        for item in remove_itens:
            line = line.replace(item, '')

        return line.strip()
    
    def _get_value_in_list(self, data: list, index: int) -> str:

        try:
            return data[index]

        except IndexError:
            return None