import json


class GitlabProject:
    def __init__(self, project_raw):
        self._project_raw = project_raw
        self.project_id = project_raw.get("id")
        self.description = project_raw.get("description")
        self.name = project_raw.get("name")

    def __str__(self):
        return "{}:\n{}".format(self.__class__.__name__, json.dumps(self.to_json(), indent=4))

    def to_json(self):
        return {
            "id": self.project_id,
            "description": self.description,
            "name": self.name
        }