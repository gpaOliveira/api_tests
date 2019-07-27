from tests.test_base import ApiTestBase
from framework.apis.github.api_github import ApiGithub
from framework.github.github_repository import GithubRepository
from framework.comparisons.equal_deep import EqualDeep
from framework.datetime.datetime import now_to_str
from typing import List
import pdb


class TestGithubApi(ApiTestBase):

    def test_make_sure_github_repository_exist(self):
        """
        Given a GITHUB_KEY
        When listing all user repositories
        Then the repository with name "playground" is among one of the returned
        """
        if not self.environment.GITHUB_KEY:
            self.then_everything_should_be_fine(["No GITHUB_KEY"])

        api = ApiGithub(self.environment.GITHUB_BASE, self.environment.GITHUB_KEY)
        repositories: List[GithubRepository] = api.user_repositories()
        self.flush_api_messages(api)

        for r in repositories:
            self.add_output_message(str(r))

        target_repo = [r for r in repositories if r.name == "playground"]
        if not target_repo:
            self.add_fail_message("No 'playground' repository found")

        self.then_everything_should_be_fine()
