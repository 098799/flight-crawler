import json
import os


def open_json_fixture(file_name):
    file_path = os.path.join(os.getcwd(), f"tests/fixtures/{file_name}")

    with open(file_path, "r") as infile:
        return json.load(infile)
