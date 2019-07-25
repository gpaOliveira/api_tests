from tests.test_base import ApiTestBase
from framework.apis.gitlab.api_gitlab import ApiGitlab
from framework.gitlab.gitlab_project import GitlabProject
from framework.comparisons.equal_deep import EqualDeep
from framework.datetime.datetime import now_to_str


class TestGitlabApi(ApiTestBase):

    def test_make_sure_project_search_requires_api_key(self):
        """
        Given no GITLAB_KEY
        When a search for gpaoliveira_playground is made
        Then no project is returned
        """
        api = ApiGitlab(self.environment.GITLAB_BASE, self.environment.GITLAB_KEY)
        api.search_project_without_api_key("gpaoliveira_playground")
        self.flush_api_messages(api)
        self.then_everything_should_be_fine()

    def test_make_sure_project_exist(self):
        """
        Given a GITLAB_KEY
        When a search for gpaoliveira_playground is made
        Then the project is returned
        """
        if not self.environment.GITLAB_KEY:
            self.then_everything_should_be_fine(["No GITLAB_KEY"])

        api = ApiGitlab(self.environment.GITLAB_BASE, self.environment.GITLAB_KEY)
        project: GitlabProject = api.search_project("gpaoliveira_playground")
        self.flush_api_messages(api)

        self.add_output_message(str(project))

        equals = EqualDeep()
        if not equals.run(target=project, name="gpaoliveira_playground"):
            self.add_fail_messages(equals.error_messages)

        self.then_everything_should_be_fine()

    def test_create_issue_in_project(self):
        """
        Given a GITLAB_KEY
        And a search for gpaoliveira_playground was made
        When an issue is created with today's date
        And project issues are searched for using created issue name
        Then the same issue is returned
        """

        if not self.environment.GITLAB_KEY:
            self.then_everything_should_be_fine(["No GITLAB_KEY"])

        self.log_step("Given a search for gpaoliveira_playground was made")
        equals = EqualDeep()
        api = ApiGitlab(self.environment.GITLAB_BASE, self.environment.GITLAB_KEY)
        project: GitlabProject = api.search_project("gpaoliveira_playground")
        self.add_output_message(str(project))
        if not equals.run(target=project, name="gpaoliveira_playground"):
            self.then_everything_should_be_fine(equals.error_messages)

        self.log_step("When an issue is created with today's date")
        now = now_to_str()
        issue_name = "Issue {}".format(now)
        self.add_output_message("Creating {}".format(issue_name))
        issue = api.create_bug(project, issue_name)
        self.add_output_message(str(issue))
        if not equals.run(target=issue, name=issue_name):
            self.then_everything_should_be_fine(equals.error_messages)

        self.log_step("When project issues are searched for using created issue name")
        self.add_output_message("Retrieving {}".format(issue_name))
        listed_issue = api.list_issues_project(project, issue_name)
        self.add_output_message(str(listed_issue))
        if not equals.run(target=listed_issue, name=issue_name):
            self.then_everything_should_be_fine(equals.error_messages)

        self.log_step("Then the same issue is returned")
        if issue.to_json() != listed_issue.to_json():
            self.then_everything_should_be_fine(
                ["issue {} != retrieved {}".format(issue.to_json(), listed_issue.to_json())]
            )

        self.then_everything_should_be_fine()
