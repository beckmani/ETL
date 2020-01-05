import requests
import uuid
import json


def generate_file_names():
    files_dict = {'Files': []}
    for i in range(10):
        file_name = str(uuid.uuid4())
        files_dict['Files'].append(file_name)

    headers = {'content-type': 'application/json'}
    r = requests.post('http://127.0.0.1:8081/insertFiles', data=json.dumps(files_dict), headers=headers)

if __name__ == '__main__':
    generate_file_names()