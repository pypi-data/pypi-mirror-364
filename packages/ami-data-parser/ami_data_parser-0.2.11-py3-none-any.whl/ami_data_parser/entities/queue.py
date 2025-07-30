from ami_data_parser.entities.core import BaseEntitie
from ami_data_parser.factories.call_factory import get_calls
from ami_data_parser.factories.queue_member_factory import get_queue_members
from ami_data_parser.repositories.call_repository import CallRepository
from ami_data_parser.repositories.member_repository import MemberRepository


class Queue(BaseEntitie):

    def __init__(
        self,
        queuename: str,
        total_calls: int,
        strategy: str,
        wait_mean: int,
        duration_mean: int,
        total_wait_calls: int,
        total_completed_calls: int,
        total_abandoned_calls: int,
        members: list,
        waiting_calls: list
    ):
        self.queuename = queuename
        self.total_calls = total_calls
        self.strategy = strategy
        self.wait_mean = wait_mean
        self.duration_mean = duration_mean
        self.total_wait_calls =  total_wait_calls
        self.total_completed_calls = total_completed_calls
        self.total_abandoned_calls = total_abandoned_calls
        self.members = self._generate_member_repository(members)
        self.waiting_calls = self._generate_call_repository(waiting_calls)
        self.type = 'queue'

    def get_key(self) -> str:
        return self.queuename
    
    def get_dict(self) -> dict:
        data = {
            "queuename": self.queuename,
            "total_calls": self.total_calls,
            "strategy": self.strategy,
            "wait_mean": self.wait_mean,
            "duration_mean": self.duration_mean,
            "total_wait_calls": self.total_wait_calls,
            "total_completed_calls": self.total_completed_calls,
            "total_abandoned_calls": self.total_abandoned_calls,
            "members": self.members.get_dict(),
            "waiting_calls": self.waiting_calls.get_dict(),
            "type": self.type
        }
        return data

    def _generate_member_repository(self, members: list) -> MemberRepository:
        repository = MemberRepository()
        repository.set(get_queue_members(members))        
        return repository
    
    def _generate_call_repository(self, waiting_calls: list) -> CallRepository:
        repository = CallRepository()
        repository.set(get_calls(waiting_calls))
        return repository
    
    def __eq__(self, value: object) -> bool:

        if type(self) != type(value):
            return False
        
        return bool(
            self.members == value.members and
            self.waiting_calls == value.waiting_calls and
            self.total_wait_calls == value.total_wait_calls and
            self.total_completed_calls == value.total_completed_calls and
            self.total_abandoned_calls == value.total_abandoned_calls and
            self.get_key() == value.get_key()    
        )
