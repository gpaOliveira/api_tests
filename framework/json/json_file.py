import json
import os


class JsonFile:

    @staticmethod
    def list_to_json_file(any_list, json_filename):
        json_list = [
            a.to_json()
            for a in any_list
            if "to_json" in dir(a)
        ]
        with open(json_filename, "w") as f:
            f.write(json.dumps(json_list, indent=4))

    @staticmethod
    def parse_from_json_file(class_to_parse, json_filename):

        if "from_json" not in dir(class_to_parse):
            return []
        if not os.path.exists(json_filename):
            return []

        with open(json_filename, "r") as f:
            json_list = json.loads(f.read())

        parsed_list = [
            class_to_parse.from_json(j)
            for j in json_list
        ]
        return parsed_list