from framework.apis.api_base import ApiBase
from framework.gitlab.gitlab_project import GitlabProject
from framework.gitlab.gitlab_issue import GitlabIssue
from framework.requests.requests import Requests
import pdb


class ApiGitlab(ApiBase):
    def __init__(self, gitlab_base, gitlab_api_key):
        super().__init__()
        self.gitlab_base = gitlab_base
        self.gitlab_api_key = gitlab_api_key

    def search_project_without_api_key(self, search):
        self.request(
            name="search_project",
            url=self.gitlab_base + "search?scope=projects&search=" + search,
            expected_response_code=401
        )
        if not self.verification_status:
            return False
        return True

    def search_project(self, search) -> GitlabProject:
        project_raw = self.request(
            name="search_project",
            request_headers={"Private-Token": self.gitlab_api_key},
            url=self.gitlab_base + "search?scope=projects&search=" + search
        )
        if not self.verification_status:
            return None
        if not project_raw:
            return None

        return GitlabProject(project_raw[0])

    def list_issues_project(self, project: GitlabProject, issue_name) -> GitlabProject:
        issue_raw = self.request(
            name="list_issues_project",
            request_headers={"Private-Token": self.gitlab_api_key},
            url="{}projects/{}/issues?search={}".format(self.gitlab_base, project.project_id, issue_name),
        )
        if not self.verification_status:
            return None
        if not issue_raw:
            return None

        return GitlabIssue(issue_raw[0])

    def create_bug(self, project: GitlabProject, issue_name) -> GitlabIssue:
        issue_raw = self.request(
            name="search_project",
            method=Requests.METHOD_POST,
            request_headers={"Private-Token": self.gitlab_api_key, "Content-Type": "application/json"},
            url="{}projects/{}/issues/".format(self.gitlab_base, project.project_id),
            json_body={"title": issue_name, "labels": "bug"},
            expected_response_code=201
        )
        if not self.verification_status:
            return None
        if not issue_raw:
            return None

        return GitlabIssue(issue_raw)