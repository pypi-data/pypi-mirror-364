from ami_data_parser.entities.channel import Channel
from ami_data_parser.repositories.core import BaseRepository


class ChannelRepository(BaseRepository):
    _entitie = Channel

    def get(self, name: str=None, peername: str=None) -> Channel:

        if name:
            return super().get(name)
        
        if peername:
            for channel_name in self._objects:
                if channel_name.startswith(peername):
                    return super().get(channel_name)
            
        return None