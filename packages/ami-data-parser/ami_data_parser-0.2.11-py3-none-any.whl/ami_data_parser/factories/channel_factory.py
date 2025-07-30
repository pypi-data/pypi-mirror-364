from ami_data_parser.entities.channel import Channel


def get_channels(data: list) -> list:
    return [
        Channel(**item)
        for item in data
    ]