from datetime import datetime


class BaseEntitie:

    class DoesExists(Exception):
        
        def __init__(self, message: str=None) -> None:
            self.message = message
            

    def get_key(self) -> str:
        raise NotImplemented
    
    def set_status_time(self, obj):
        ...
        
    def _get_timestamp(self) -> float:
        return datetime.now().timestamp()
    