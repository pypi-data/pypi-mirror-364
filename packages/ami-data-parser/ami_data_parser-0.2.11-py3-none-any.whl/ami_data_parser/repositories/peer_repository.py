from ami_data_parser.entities.peer import Peer
from ami_data_parser.repositories.core import BaseRepository


class PeerRepository(BaseRepository):
    _entitie = Peer

    def get(self, name) -> Peer:
        return super().get(name)