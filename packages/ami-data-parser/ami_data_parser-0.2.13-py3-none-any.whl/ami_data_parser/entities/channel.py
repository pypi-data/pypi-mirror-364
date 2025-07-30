from ami_data_parser.entities.core import BaseEntitie


class Channel(BaseEntitie):

    def __init__(
        self,
        channel: str,
        context: str,
        exten: str,
        priority: str,
        state: str,
        application: str,
        app_data: str,
        callerid_num: str,
        uniqueid: str
    ):
        self.channel = channel
        self.context = context
        self.exten = exten
        self.priority = priority
        self.state = state
        self.application = application
        self.app_data = app_data
        self.callerid_num = callerid_num
        self.uniqueid = uniqueid
        self.timestamp = self._get_timestamp()
        self.type = 'channel'

    def get_key(self) -> str:
        return self.channel
    
    def set_status_time(self, obj) -> None:
        self.timestamp = obj.timestamp
    
    def __eq__(self, value: object) -> bool:

        if type(self) != type(value):
            return False
        
        return bool(self.state == value.state and
            self.get_key() == value.get_key()    
        )