from framework.apis.api_base import ApiBase
from framework.github.github_repository import GithubRepository
from framework.github.github_issue import GithubIssue
from framework.requests.requests import Requests
from typing import List
import pdb
import os


class ApiGithub(ApiBase):
    VERSION_3 = "application/vnd.github.v3+json"
    VERSION_2 = "application/vnd.github.v2+json"

    def __init__(self, github_base, github_api_key):
        super().__init__()
        self.github_base = github_base
        self.github_api_key = github_api_key
        self._base_folder = os.path.dirname(os.path.abspath(__file__))

    def user_repositories_v3(self) -> List[GithubRepository]:
        return self._user_repositories(version=self.VERSION_3)

    def user_repositories_v2(self) -> List[GithubRepository]:
        return self._user_repositories(version=self.VERSION_2)

    def _user_repositories(self, version:str) -> List[GithubRepository]:
        name = "user_repositories"
        schema_file = os.path.join(self._base_folder, "user_repositories.schema.json")
        repos_raw = self.request(
            name=name,
            request_headers={
                "Authorization": "token " + self.github_api_key,
                "Accept": version
            },
            url=self.github_base + "user/repos"
        )
        if not self.verification_status:
            return []
        if not repos_raw:
            return []
        if not self.validate_json_schema(name, repos_raw, schema_file):
            return []

        return [GithubRepository(r) for r in repos_raw]

    def list_issues_in_repo(self, repo: GithubRepository):
        url = "{}repos/{}/{}/issues".format(self.github_base, repo.owner_login, repo.name)
        issues_raw = self.request(
            name="user_issues_in_repo",
            url=url,
            request_headers={
                "Authorization": "token " + self.github_api_key
            }
        )
        if not self.verification_status:
            return []
        if not issues_raw:
            return []

        return [GithubIssue(r) for r in issues_raw]

    def create_issue_in_repo(self, repo: GithubRepository, name:str, labels:List[str], description:str):
        url = "{}repos/{}/{}/issues".format(self.github_base, repo.owner_login, repo.name)
        issue_raw = self.request(
            method=Requests.METHOD_POST,
            name="create_issue_in_repo",
            url=url,
            request_headers={
                "Authorization": "token " + self.github_api_key
            },
            json_body={
                "title": name,
                "body": description,
                "labels": labels
            },
            expected_response_code=201
        )
        if not self.verification_status:
            return None
        if not issue_raw:
            return None

        return GithubIssue(issue_raw)

    def retrieve_single_issue(self, issue: GithubIssue):
        issue_raw = self.request(
            name="create_issue_in_repo",
            url=issue.url,
            request_headers={
                "Authorization": "token " + self.github_api_key
            }
        )
        if not self.verification_status:
            return None
        if not issue_raw:
            return None

        return GithubIssue(issue_raw)
