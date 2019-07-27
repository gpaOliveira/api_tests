import json


class GithubRepository:
    def __init__(self, raw_repo):
        self.repo_id = raw_repo.get("id")
        self.node_id = raw_repo.get("node_id")
        self.name = raw_repo.get("name")
        self.full_name = raw_repo.get("full_name")
        self.description = raw_repo.get("description")
        self.owner_login = raw_repo.get("owner", {}).get("login")
        repo_license = raw_repo.get("license", {})
        if repo_license is None:
            repo_license = {}
        self.license_name = repo_license.get("name")

    def __str__(self):
        return "{}:\n{}".format(self.__class__.__name__, json.dumps(self.to_json(), indent=4))

    def to_json(self):
        return {
            "repo_id": self.repo_id,
            "node_id": self.node_id,
            "name": self.name,
            "full_name": self.full_name,
            "description": self.description,
            "owner_login": self.owner_login,
            "license_name": self.license_name
        }