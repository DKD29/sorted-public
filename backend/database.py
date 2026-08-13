import json
import os


BASE_DIR = os.path.dirname(
    os.path.dirname(
        os.path.abspath(__file__)
    )
)

DATA_FOLDER = os.path.join(
    BASE_DIR,
    "data"
)


def load_data(filename):
    path = os.path.join(DATA_FOLDER, filename)

    if not os.path.exists(path):
        return {}

    with open(path, "r") as file:
        return json.load(file)



def save_data(filename, data):
    path = os.path.join(DATA_FOLDER, filename)

    with open(path, "w") as file:
        json.dump(data, file, indent=4)