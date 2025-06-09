import json
import os
import yaml


def load_txt(file_path):
    if not os.path.exists(file_path):
        with open(file_path, 'w') as file:
            pass

    else:
        with open(file_path, 'r') as file:
            data = [line.split()[0] for line in file.readlines()]
            return data
        

def load_json(file_path):
    if not os.path.exists(file_path):
        with open(file_path, 'w') as file:
            pass
    else:
        with open(file_path) as file:
            data = json.load()
            return data
        

def load_yaml(file_path):
    with open(file_path, 'r') as file:
        data = yaml.safe_load(file)
        return data