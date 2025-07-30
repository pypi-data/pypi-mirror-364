from ami_data_parser.entities.core import BaseEntitie


class Call(BaseEntitie): 

    def __init__(
        self,
        channel: str,
        position: int,
        wait_time: int,
        priority: int
    ):
        self.channel = channel
        self.position = position
        self.wait_time = wait_time
        self.priority = priority
        self.type = 'call'
    
    def get_key(self) -> str:
        return self.channel
    
    def __eq__(self, value: object) -> bool:

        if type(self) != type(value):
            return False
        
        return bool(
            self.position == value.position and
            self.get_key() == value.get_key()    
        )