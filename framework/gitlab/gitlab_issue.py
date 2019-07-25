import json


class GitlabIssue:
    def __init__(self, issue_raw):
        self._issue_raw = issue_raw
        self.issue_id = issue_raw.get("id")
        self.issue_iid = issue_raw.get("iid")
        self.project_id = issue_raw.get("project_id")
        self.description = issue_raw.get("description")
        self.name = issue_raw.get("title")
        self.state = issue_raw.get("state")

    def __str__(self):
        return "{}:\n{}".format(self.__class__.__name__, json.dumps(self.to_json(), indent=4))

    def to_json(self):
        return {
            "issue_id": self.issue_id,
            "issue_iid": self.issue_id,
            "project_id": self.project_id,
            "description": self.description,
            "name": self.name,
            "state": self.state,
        }