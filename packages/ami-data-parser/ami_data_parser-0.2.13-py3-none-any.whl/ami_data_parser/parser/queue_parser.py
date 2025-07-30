from ami_data_parser.parser.core import BaseParser, ParserException
from ami_data_parser.parser.utils import set_output_format


class QueueParser(BaseParser):

    def __init__(self) -> None:
        self._item = None
    
    def get_data(self, lines: list) -> list:
        list_queue_lines = self._get_list_queue_lines(lines)
        data =[]

        for queue_lines in list_queue_lines:
            self._reset_next_item()
            data_queue = self._get_parser_queue(queue_lines)
            data.append(data_queue)
        
        return data
    
    def _get_list_queue_lines(self, lines: list) -> list:
        data = []
        actual_list = None

        for line in lines:           
            line = set_output_format(line)

            if 'Output:' in line:
                if 'strategy' in line:
                    if actual_list:
                        data.append(actual_list)

                    actual_list = []
                
                try:
                    actual_list.append(line)
                
                except AttributeError:
                    return []
        
        if actual_list:
            data.append(actual_list)

        return data

    def _get_parser_queue(self, lines: list) -> dict:
        data = {
            'members': [],
            'waiting_calls': []
        }

        for line in lines:

            try:
                if self._next_item(line) == 'queue':
                    data.update(self._get_data_queue(line))
                
                elif self._next_item(line) == 'members':
                    members_data = self._get_data_member(line)
                    data['members'].append(members_data)
                
                elif self._next_item(line) == 'callers':
                    callers_data = self._get_data_channel(line)
                    data['waiting_calls'].append(callers_data)
            
            except ParserException:
                ...
        
        return data
    
    def _next_item(self, line: str) -> str:
        line = self._clean_line(line)

        if not self._item:
            self._item = 'queue'
        
        elif line == 'Members:':
            self._item = 'members'

        elif line == 'Callers:':
            self._item = 'callers'

        return self._item
    
    def _reset_next_item(self) -> None:
        self._item = 'queue'
    
    def _get_data_queue(self, line: str) -> dict:
        return {
            'queuename': self._get_queuename(line),
            'total_calls': self._get_total_calls(line),
            'strategy': self._get_strategy(line),
            'wait_mean': self._get_wait_mean(line),
            'duration_mean': self._get_duration_mean(line),
            'total_wait_calls': self._get_total_wait_calls(line),
            'total_completed_calls': self._get_total_completed_calls(line),
            'total_abandoned_calls': self._get_total_abandoned_calls(line)
        }
    
    def _get_data_member(self, line: str) -> dict:
        return {
            'name': self._get_member_name(line),
            'dynamic': self._get_dynamic_name(line),
            'in_call': self._get_in_call_atribute(line),
            'has_paused': self._get_member_has_paused(line),
            'paused_time': self._get_member_paused(line),
            'reason_paused': self._get_reason_paused(line),
            'logged_time': self._get_member_logged(line),
            'total_calls': self._get_member_calls(line),
            'last_call_time': self._get_member_last_call(line),
            'penalty': self._get_penalty(line)
        }
    
    def _get_data_channel(self, line: str) -> dict:
        return {
            'channel': self._get_call_channel(line),
            'position': self._get_call_position(line),
            'wait_time': self._get_call_wait(line),
            'priority': self._get_call_priority(line)
        }

    def _get_queuename(self, line: str) -> str:
        queuename = self._get_data(line, None, 'has')
        return queuename
    
    def _get_total_calls(self, line: str) -> int:
        total_calls = self._get_data(line, 'has', 'calls')
        return int(total_calls)
    
    def _get_strategy(self, line: str) -> str:
        strategy = self._get_data(line, 'in', 'strategy')
        return strategy
    
    def _get_wait_mean(self, line: str) -> int:
        wait_mean = self._get_data(line, 'strategy (', 's holdtime')
        return int(wait_mean)
    
    def _get_duration_mean(self, line: str) -> int:
        duration_mean = self._get_data(line, 'holdtime,', 's talktime')
        return int(duration_mean)
    
    def _get_total_wait_calls(self, line: str) -> int:
        total_wait_calls = self._get_data(line, 'W:', ', C:')
        return int(total_wait_calls)
    
    def _get_total_completed_calls(self, line: str) -> int:
        total_completed_calls = self._get_data(line, 'C:', ', A:')
        return int(total_completed_calls)
    
    def _get_total_abandoned_calls(self, line: str) -> int:
        total_abandoned_calls = self._get_data(line, 'A:', ', SL:')
        return int(total_abandoned_calls)
    
    def _get_member_name(self, line: str) -> str:

        if '(dynamic)' in line:
            queue_member = self._get_data(line, '(', ')')
            return queue_member
        
        if 'with penalty' in line:
            queue_member = self._get_data(line, None, 'with penalty')
            return queue_member
        
        queue_member = self._get_data(line, None, '(')
        return queue_member

    def _get_dynamic_name(self, line) -> str:

        if '(dynamic)' in line:
            return self._get_data(line, None, '(')
        
        return None
    
    def _get_in_call_atribute(self, line) -> bool:
        return bool('(in call)' in line)
    
    def _get_member_paused(self, line: str) -> int:
        
        try:
            member_paused = self._get_data(line, '(paused was', 'secs ago)')
            return int(member_paused)
        
        except (ParserException, ValueError):
            return 0
    
    def _get_member_has_paused(self, line: str) -> bool:
        return bool('paused' in line)
    
    def _get_reason_paused(self, line: str) -> str:
        pattern = 'paused:'

        if pattern in line:
            pos_ini = line.find(pattern) + len(pattern)
            line = line[pos_ini:]
            pos_end = line.find('was')
            line = line[:pos_end]
            return line.strip()
            
        return None
    
    def _get_member_logged(self, line: str) -> int:
        
        try:
            member_logged = self._get_data(line, '(login was', 'secs ago)')
            return int(member_logged)
        
        except (ParserException, ValueError):
            return 0
    
    def _get_member_calls(self, line: str) -> int:
        
        try:
            member_calls = self._get_data(line, 'has taken', 'calls')
            return int(member_calls)
        
        except (ParserException, ValueError):
            return 0
    
    def _get_member_last_call(self, line: str) -> int:
        
        try:
            last_call = self._get_data(line, 'calls (last was', 'secs ago')
            return int(last_call)
        
        except (ParserException, ValueError):
            return 0
    
    def _get_penalty(self, line: str) -> int:
        
        try:
            penalty = self._get_data(line, 'penalty ', ' (ringinuse')
            return int(penalty)
        
        except (ParserException, ValueError):
            return 0
    
    def _get_call_position(self, line: str) -> int:
        
        try:
            call_position = self._get_data(line, None, '.')
            return int(call_position)
        
        except (ParserException, ValueError):
            return 0
    
    def _get_call_channel(self, line: str) -> str:
        call_channel = self._get_data(line, '.', '(wait:')
        return call_channel
    
    def _get_call_wait(self, line: str) -> int:
        
        try:
            call_wait = self._get_data(line, '(wait: ', ', prio:')
            minutes, seconds = map(int, call_wait.split(':'))
            return int((minutes * 60) + seconds)
        
        except (ParserException, ValueError):
            return 0
    
    def _get_call_priority(self, line: str) -> int:
        
        try:
            call_wait = self._get_data(line, 'prio:', ')')
            return int(call_wait)
        
        except (ParserException, ValueError):
            return 0