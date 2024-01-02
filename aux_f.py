import json


def read_keys_d(file_name='api_keys.json'):
    with open(file_name, 'r') as f:
        l = f.read()
    return json.loads(l)
