import json


class GithubIssue:
    """
    "state": "open",
    "title": "Found a bug",
    "body": "I'm having a problem with this.",
    """
    def __init__(self, raw_issue):
        self.issue_id = raw_issue.get("id")
        self.node_id = raw_issue.get("node_id")
        self.url = raw_issue.get("url")
        self.name = raw_issue.get("title")
        self.state = raw_issue.get("state")
        self.description = raw_issue.get("body")
        self.owner_login = raw_issue.get("user", {}).get("login")
        assignee = raw_issue.get("assignee")
        if assignee is None:
            assignee = {}
        self.assignee_login = assignee.get("login")
        pull_request = raw_issue.get("pull_request", {})
        if pull_request is None:
            pull_request = {}
        self.pull_request_url = pull_request.get("url")
        labels = raw_issue.get("labels", [])
        if labels is None:
            labels = []
        self.label_names = [l.get("name") for l in labels]

    def __str__(self):
        return "{}:\n{}".format(self.__class__.__name__, json.dumps(self.to_json(), indent=4))

    def to_json(self):
        return {
            "issue_id": self.issue_id,
            "node_id": self.node_id,
            "url": self.url,
            "name": self.name,
            "state": self.state,
            "description": self.description,
            "owner_login": self.owner_login,
            "assignee_login": self.assignee_login,
            "pull_request_url": self.pull_request_url,
            "label_names": self.label_names,
        }