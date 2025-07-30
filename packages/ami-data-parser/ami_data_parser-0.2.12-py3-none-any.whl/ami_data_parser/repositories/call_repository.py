from ami_data_parser.entities.call import Call
from ami_data_parser.repositories.core import BaseRepository


class CallRepository(BaseRepository):
    _entitie = Call

    def get(self, name) -> Call:
        return super().get(name)
    
    def get_dict(self) -> dict:
        return [
            vars(self._objects[key])
            for key in self._objects
        ]

    def __eq__(self, value: object) -> bool:
        
        if self.count() != value.count():
            return False
        
        for call in value.all():
            
            if not self.exists(call.get_key()):
                return False
            
            if call != self.get(call.get_key()):
                return False
        
        return True