import json
import os


def load_txt(file_path):
    if not os.path.exists(file_path):
        with open(file_path, 'w') as file:
            pass

    else:
        with open(file_path, 'r') as file:
            data = [line.split()[0] for line in file.readlines()]
            return data