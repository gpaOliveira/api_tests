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
        self.log_step("Given a GITHUB_KEY")
        if not self.environment.GITHUB_KEY:
            self.then_everything_should_be_fine(["No GITHUB_KEY"])

        self.log_step("When listing all user repositories")
        api = ApiGithub(self.environment.GITHUB_BASE, self.environment.GITHUB_KEY)
        repositories: List[GithubRepository] = api.user_repositories_v3()
        self.flush_api_messages(api)
        for r in repositories:
            self.add_output_message(str(r))

        self.log_step("Then the repository with name 'playground' is among one of the returned")
        target_repo = [r for r in repositories if r.name == "playground"]
        if not target_repo:
            self.add_fail_message("No 'playground' repository found")

        self.then_everything_should_be_fine()

    def test_make_sure_github_repository_is_the_same_on_v2_and_v3(self):
        """
        Given a GITHUB_KEY
        And a list of all user repositories using v3
        And a list of all user repositories using v2
        When the repository with name "playground" is among one returned in both lists
        Then they have the same information
        """
        self.log_step("Given a GITHUB_KEY")
        if not self.environment.GITHUB_KEY:
            self.then_everything_should_be_fine(["No GITHUB_KEY"])

        self.log_step("Given all user repositories using v3")
        api = ApiGithub(self.environment.GITHUB_BASE, self.environment.GITHUB_KEY)
        repositories_v3: List[GithubRepository] = api.user_repositories_v3()
        self.flush_api_messages(api)
        self.add_output_message("User repositories using v3:")
        for r in repositories_v3:
            self.add_output_message(str(r))

        self.log_step("Given all user repositories using v2")
        repositories_v2: List[GithubRepository] = api.user_repositories_v2()
        self.flush_api_messages(api)
        self.add_output_message("User repositories using v2:")
        for r in repositories_v2:
            self.add_output_message(str(r))

        self.log_step("When the repository with name 'playground' is among one returned in both lists")
        target_repo_v3: List[GithubRepository] = [r for r in repositories_v3 if r.name == "playground"]
        if not target_repo_v3:
            self.add_fail_message("No 'playground' repository found in v3")
        else:
            self.add_output_message("Target repository using v3:\n" + str(target_repo_v3[0]))

        target_repo_v2: List[GithubRepository] = [r for r in repositories_v2 if r.name == "playground"]
        if not target_repo_v2:
            self.add_fail_message("No 'playground' repository found in v2")
        else:
            self.add_output_message("Target repository using v2:\n" + str(target_repo_v2[0]))

        self.log_step("Then they have the same information")
        if target_repo_v3 and target_repo_v2 and target_repo_v3[0].to_json() != target_repo_v2[0].to_json():
            self.then_everything_should_be_fine(
                ["target_repo_v3 {} != retrieved {}".format(target_repo_v3[0].to_json(), target_repo_v2[0].to_json())]
            )

        self.then_everything_should_be_fine()
