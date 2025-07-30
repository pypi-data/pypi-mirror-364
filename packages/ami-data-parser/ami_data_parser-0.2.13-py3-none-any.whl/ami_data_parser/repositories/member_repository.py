from ami_data_parser.entities.queue_member import QueueMember
from ami_data_parser.repositories.core import BaseRepository


class MemberRepository(BaseRepository):
    _entitie = QueueMember  

    def get(self, name) -> QueueMember:
        return super().get(name)

    def get_dict(self) -> dict:
        return [
            vars(self._objects[key])
            for key in self._objects
        ]

    def __eq__(self, value: object) -> bool:
       
        if self.count() != value.count():
            return False
        
        for member in value.all():
            if not self.exists(member.get_key()):
                return False
            
            if member != self.get(member.get_key()):
                return False
        
        return True