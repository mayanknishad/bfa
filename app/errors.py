"""
Error checking
"""


def check_request(data, keys):
    """
    check's request data to make sure it contains all keys in keys
    """
    missing_keys = [key for key in keys if key not in data]

    if len(missing_keys):
        return [{'message': 'Missing/incorrect request keys - {}'.format(missing_keys)}]
    return []

