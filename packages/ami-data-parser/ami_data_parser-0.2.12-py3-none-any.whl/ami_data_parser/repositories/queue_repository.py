from ami_data_parser.entities.queue import Queue
from ami_data_parser.repositories.core import BaseRepository


class QueueRepository(BaseRepository):
    _entitie = Queue

    def get(self, name) -> Queue:
        return super().get(name)