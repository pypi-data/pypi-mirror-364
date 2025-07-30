class ParserException(Exception):

    def __init__(self, message: str=None) -> None:
        self.message = message


class BaseParser:

    def _get_data(self, line: str, initial_pattern: str, final_pattern: str) -> str:
        line = self._clean_line(line)
        initial_position = self._get_initial_position(line, initial_pattern)
        final_position = self._get_final_position(line, final_pattern, initial_position)
        data = line[initial_position: final_position].strip()       
        return data
    
    def _clean_line(self, line: str) -> str:
        exclude_list_pattern = ["'", 'Output:', '\r\n']

        for pattern in exclude_list_pattern:
            line = line.replace(pattern, '')
        
        return line.strip()
    
    def _get_initial_position(self, line: str, pattern: str) -> int:

        if not pattern:
            return 0
        
        position = self._validate_position(line.find(pattern))
        return position + len(pattern)
    
    def _get_final_position(self, line: str, pattern: str, initial_position: int) -> int:
        
        if not pattern:
            return len(line)

        position = self._validate_position(line[initial_position:].find(pattern))
        return position + initial_position
    
    def _validate_position(self, position: int) -> int:

        if position == -1:
            raise ParserException()
        
        return position