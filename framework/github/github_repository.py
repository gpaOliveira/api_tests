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

    @staticmethod
    def from_json(github_repository_json):
        return GithubRepository({
            "id": github_repository_json.get("repo_id"),
            "node_id": github_repository_json.get("node_id"),
            "name": github_repository_json.get("name"),
            "full_name": github_repository_json.get("full_name"),
            "description": github_repository_json.get("description"),
            "owner": {"login": github_repository_json.get("owner_login")},
            "license": (
                None if github_repository_json.get("license_name") is None
                else {"name": github_repository_json.get("license_name")}
            )
        })

    def csv_headers(self):
        return list(self.to_json().keys())

    def csv_line(self, headers):
        myself = self.to_json()
        return [
            myself.get(h, '') for h in headers
        ]