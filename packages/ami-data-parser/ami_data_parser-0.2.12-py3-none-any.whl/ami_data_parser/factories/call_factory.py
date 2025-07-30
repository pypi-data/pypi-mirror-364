from ami_data_parser.entities.call import Call


def get_calls(data: list) -> list:
    return [
        Call(**item)
        for item in data
    ]