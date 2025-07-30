from ami_data_parser.entities.queue_member import QueueMember


def get_members(data: list) -> list:
    return [
        QueueMember(**item)
        for item in data
    ]