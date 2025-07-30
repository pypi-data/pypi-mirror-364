from ami_data_parser.entities.queue import Queue
from ami_data_parser.factories.channel_factory import get_channels
from ami_data_parser.factories.peer_factory import get_peers
from ami_data_parser.factories.queue_factory import get_queues
from ami_data_parser.parser.channel_parser import ChannelParser
from ami_data_parser.parser.hint_parser import HintParser
from ami_data_parser.parser.queue_parser import QueueParser
from ami_data_parser.repositories.channel_repository import ChannelRepository
from ami_data_parser.repositories.peer_repository import PeerRepository
from ami_data_parser.repositories.queue_repository import QueueRepository


class Controller:

    def __init__(self):
        self._channel_parser = ChannelParser()
        self._hint_parser = HintParser()
        self._queue_parser = QueueParser()
        self._channel_repository = ChannelRepository()
        self._peer_repository = PeerRepository()
        self._queue_repository = QueueRepository()
        self._queues_members_dict = {}
        self._diff_queues_list = []
        self._get_channels = get_channels
        self._get_peers = get_peers
        self._get_queues = get_queues

    def get(self, entity_key: str, entity_type: str, raise_exception=False):

        if entity_type == 'peer':

            if not self._peer_repository.exists(entity_key) and not raise_exception:
                return None
            
            return self._peer_repository.get(entity_key)
        
        elif entity_type == 'queue':

            if not self._queue_repository.exists(entity_key) and not raise_exception:
                return None
            
            return self._queue_repository.get(entity_key)
        
        elif entity_type == 'channel':
            return self._channel_repository.get(peername=entity_key)
        
        raise TypeError(f'Invalid type: {entity_type}')
    
    def update(self, data: list) -> dict:
        data_type = self._get_data_type(data)
        data_diff = []

        if data_type == 'peer':
            data_diff.extend(self.peer_update(data))
            data_diff.extend(self.queue_update())
        
        elif data_type == 'queue':
            data_diff.extend(self.queue_update(data))
        
        elif data_type == 'channel':
            data_diff.extend(self.channel_update(data))
        
        return data_diff

    def get_list_queues_from_a_peer(self, key: str) -> list:
        return self._queues_members_dict.get(key, [])

    def peer_update(self, received_data: list) -> list:
        data = []
        self.update_peers_repository(received_data)
        peers_diff = self._peer_repository.diff()

        for peername, event in peers_diff:
            
            if event == 'removed':
                peer_dict = {'peername': peername, 'type': 'peer'}
            
            else:
                peer = self._peer_repository.get(peername)
                peer_dict = vars(peer)
                self.update_diff_queues(peername)
            
            peer_dict['event'] = event
            data.append(peer_dict)
            
        return data

    def queue_update(self, received_data: list=[]) -> list:
        data = []
        self.update_queues_repository(received_data)        
        queues_diff = self.get_queues_diff()

        for queue, event in queues_diff:

            if event == 'removed':
                queue_dict = {'queuename': queue, 'type': 'queue'}
            
            else:
                queue_data: Queue = self._queue_repository.get(queue)
                queue_dict = queue_data.get_dict()

            queue_dict['event'] = event
            data.append(queue_dict)
        
        return data
    
    def channel_update(self, received_data: list=[]) -> list:
        data = []
        self.update_channels_repository(received_data)
        channels_diff = self._channel_repository.diff()

        for channel, event in channels_diff:
            
            if event == 'removed':
                channel_dict = {'channel': channel, 'type': 'channel'}
            
            else:
                channel = self._channel_repository.get(channel)
                channel_dict = vars(channel)
            
            channel_dict['event'] = event
            data.append(channel_dict)
            
        return data
    
    def update_peers_repository(self, data: list) -> None:
        parser_data = self._hint_parser.get_data(data)
        peers_data = self._get_peers(parser_data)
        self._peer_repository.set(
            peers_data
        )

    def update_queues_repository(self, data: list) -> None:

        if len(data) > 0:
            parser_data = self._queue_parser.get_data(data)
            self.set_list_queues_from_members(parser_data)
            queues_data = self._get_queues(parser_data)
            self._queue_repository.set(
                queues_data
            )
    
    def update_channels_repository(self, data: list) -> None:
        parser_data = self._channel_parser.get_data(data)
        channels_data = self._get_channels(parser_data)
        self._channel_repository.set(
            channels_data
        )
    
    def get_queues_diff(self) -> list:
        self._queue_repository.add_diff(self._diff_queues_list)
        queues_diff = self._queue_repository.diff()
        self._diff_queues_list = []
        return queues_diff

    def set_list_queues_from_members(self, parser_data: list):
        self._clear_queues_members_dict()

        for queue_data in parser_data:
            queuename = queue_data.get('queuename')

            for member_data in queue_data.get('members', []):
                membername = member_data.get('name')

                if membername not in self._queues_members_dict:
                    self._queues_members_dict[membername] = []
                
                if queuename not in self._queues_members_dict[membername]:
                    self._queues_members_dict[membername].append(queuename)              
    
    def update_diff_queues(self, peername: str) -> None:
        peer_queues = self.get_list_queues_from_a_peer(peername)
        self._diff_queues_list.extend(
            [
                (queue, 'changed') 
                for queue in peer_queues 
                if queue not in self._diff_queues_list
            ]
        )

    def _clear_queues_members_dict(self):
        self._queues_members_dict = {}

    def _get_data_type(self, data: list) -> str:
        
        for line in data:
            if 'Hints' in line:
                return 'peer'
            
            elif 'strategy' in line:
                return 'queue'
            
            elif '!' in line:
                return 'channel'