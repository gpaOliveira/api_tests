from framework.apis.api_base import ApiBase
from framework.github.github_repository import GithubRepository
from framework.requests.requests import Requests
from typing import List
import pdb


class ApiGithub(ApiBase):
    def __init__(self, github_base, github_api_key):
        super().__init__()
        self.github_base = github_base
        self.github_api_key = github_api_key

    def user_repositories(self) -> List[GithubRepository]:
        repos_raw = self.request(
            name="user_repositories",
            request_headers={"Authorization": "token " + self.github_api_key},
            url=self.github_base + "user/repos"
        )
        if not self.verification_status:
            return []
        if not repos_raw:
            return []

        return [GithubRepository(r) for r in repos_raw]