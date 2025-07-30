from ami_data_parser.entities.core import BaseEntitie


class Member(BaseEntitie):

    def __init__(
        self,
        name: str,
        has_paused: bool,
        paused_time: int,
        logged_time: int,
        total_calls: int,
        last_call_time: int,
    ):
        self.name = name
        self.has_paused = has_paused
        self.paused_time = paused_time
        self.logged_time = logged_time
        self.total_calls = total_calls
        self.last_call_time = last_call_time
        self.type = 'member'

    class DoesExists(Exception):
        ...

    def get_key(self) -> str:
        return self.name
    
    def __eq__(self, value: object) -> bool:

        if type(self) != type(value):
            return False
        
        return bool(self.has_paused == value.has_paused and
            self.get_key() == value.get_key() 
        )