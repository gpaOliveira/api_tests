from tests.test_base import ApiTestBase
from framework.apis.github.api_github import ApiGithub
from framework.github.github_repository import GithubRepository
from framework.json.json_file import JsonFile
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
        And all the other repositories are the same as from file "github_repositories.json"
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

        self.log_step("Then all the other repositories are the same as from file 'github_repositories.json'")
        # Whenever "github_repositories.json needs to be updated, uncomment below
        # JsonFile.list_to_json_file(repositories, self.data_test_file_path("github_repositories.json"))
        loaded_repositories: List[GithubRepository] = JsonFile.parse_from_json_file(
            GithubRepository,
            self.data_test_file_path("github_repositories.json")
        )
        for r in repositories:
            equals = EqualDeep()
            loaded_repository = [l for l in loaded_repositories if l.name == r.name]
            if not loaded_repository:
                self.add_fail_message("No loaded repository with name '{}'".format(r.name))
                self.add_output_message("[BAD] No loaded repository with name '{}'".format(r.name))
            elif not equals.two_objects(loaded_repository[0], r):
                self.add_fail_message("loaded repository != repository with name '{}'".format(r.name))
                self.add_output_message(
                    "[BAD] loaded repository != repository with name '{}' - {}".format(
                        r.name,
                        ",".join(equals.error_messages)
                    )
                )
            else:
                self.add_output_message("[OK] loaded repository == repository with name '{}'".format(r.name))

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
        equals = EqualDeep()
        if not equals.two_objects(target_repo_v3[0], target_repo_v2[0]):
            self.then_everything_should_be_fine(
                ["target_repo_v3 != target_repo_v2 - {}".format(",".join(equals.error_messages))]
            )

        self.then_everything_should_be_fine()

    def test_create_issue_in_github_project(self):
        """
        Given a GITHUB_KEY
        And 'playground' repository is found using v3
        When an issue is created with today's date
        And the list of issues in the project is retrieved
        And that same issue is retrieved
        Then they all have the same issue information
        """
        equals = EqualDeep()
        self.log_step("Given a GITHUB_KEY")
        if not self.environment.GITHUB_KEY:
            self.then_everything_should_be_fine(["No GITHUB_KEY"])

        self.log_step("Given 'playground' repository is found using v3")
        api = ApiGithub(self.environment.GITHUB_BASE, self.environment.GITHUB_KEY)
        repositories_v3: List[GithubRepository] = api.user_repositories_v3()
        self.flush_api_messages(api)
        target_repos_v3: List[GithubRepository] = [r for r in repositories_v3 if r.name == "playground"]
        target_repo_v3 = None
        if not target_repos_v3:
            self.then_everything_should_be_fine(["No 'playground' repository found in v3"])
        else:
            target_repo_v3 = target_repos_v3[0]
            self.add_output_message("Target repository using v3:\n" + str(target_repo_v3))

        self.log_step("When an issue is created with today's date")
        now = now_to_str()
        issue_name = "Issue {}".format(now)
        self.add_output_message("Creating '{}'".format(issue_name))
        issue = api.create_issue_in_repo(target_repo_v3, name=issue_name, labels=["bug"], description=issue_name)
        self.add_output_message(str(issue))
        if not equals.run(target=issue, name=issue_name):
            self.then_everything_should_be_fine(equals.error_messages)

        self.log_step("When the list of issues in the project is retrieved")
        issues = api.list_issues_in_repo(target_repo_v3)
        issues_with_same_title = [i for i in issues if i.name == issue_name]
        listed_issue = None
        if not issues_with_same_title:
            self.add_fail_message("No issue with title '{}' found in repo".format(issue_name))
        else:
            self.add_output_message("Listed '{}'".format(issue_name))
            listed_issue = issues_with_same_title[0]
            self.add_output_message(str(listed_issue))

        self.log_step("When that same issue is retrieved")
        self.add_output_message("Retrieving '{}'".format(issue_name))
        retrieved_issue = api.retrieve_single_issue(issue)
        self.add_output_message(str(retrieved_issue))

        self.log_step("Then they all have the same issue information")
        equals = EqualDeep()
        if not equals.two_objects(issue, retrieved_issue):
            self.then_everything_should_be_fine(
                ["issue created != retrieved - {}".format(",".join(equals.error_messages))]
            )
        else:
            self.add_output_message("issue created == retrieved")
        if not equals.two_objects(issue, listed_issue):
            self.then_everything_should_be_fine(
                ["issue created != listed - {}".format(",".join(equals.error_messages))]
            )
        else:
            self.add_output_message("issue created == listed")

        self.then_everything_should_be_fine()