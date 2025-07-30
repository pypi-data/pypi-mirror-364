from ami_data_parser.parser.core import BaseParser, ParserException
from ami_data_parser.parser.utils import set_output_format


class HintParser(BaseParser):

    def get_data(self, lines: list) -> list:
        data = []
        
        for line in lines:
            line = set_output_format(line)

            if 'Output:' in line:
                try:
                    data.append(self._get_parser_hint(line))
                
                except ParserException:
                    ...
        
        return data

    def _get_parser_hint(self, line: str) -> str:
        return {
            'exten': self._get_exten(line),
            'peername': self._get_peername(line),
            'state': self._get_state(line),
            'presence': self._get_presence(line),
            'watchers': self._get_watchers(line)
        }
    
    def _get_exten(self, line: str) -> str:
        exten = self._get_data(line, None, '@')
        return exten
    
    def _get_peername(self, line: str) -> str:
        peername = self._get_data(line, ':', 'State:')
        return peername

    def _get_state(self, line: str) -> str:
        state = self._get_data(line, 'State:', 'Presence:')
        return state
    
    def _get_presence(self, line: str) -> str:
        state = self._get_data(line, 'Presence:', 'Watchers')
        return state
    
    def _get_watchers(self, line: str) -> int:

        try:
            state = self._get_data(line, 'Watchers', None)
            return int(state)
        
        except ValueError:
            return 0