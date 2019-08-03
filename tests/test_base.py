import unittest
import os
import json
from typing import List
from framework.apis.api_base import ApiBase
from framework.pages.page_base import PageBase
from framework.log.logger import Logger
from framework.environment.environment import Environment


class ApiTestBase(unittest.TestCase):
    def setUp(self):
        self.test_name = self.id().split(".")[-1]
        os.environ["PYTEST_CURRENT_TEST"] = self.test_name  # not needed on pytest 3.2

        self.environment = Environment()
        self.logger = Logger(debug=(self.environment.DEBUG == "true"))

        # Populate variables with data to HTML Report and to JUnit XML
        self._pytest_output = ""
        self._fail_message = []

        # Done
        self.log("Starting test " + self.id())
        self.log_step("Scenario description:")
        self.log("\n" + self.__dict__["_testMethodDoc"])

    def tearDown(self):
        self.log("Ending test {} - {}".format(self.id(), "PASSED" if len(self._fail_message) == 0 else "FAILED"))
        self.log("=" * 50)
        self.log("Log file created on {}.txt".format(self.logger.logging_filename))
        self.log("=" * 50)

    def log(self, line):
        self.logger.log(line)

    def log_multiple(self, logs: List[str]):
        self.logger.log_multiple(logs)

    def log_step(self, line):
        self.logger.log_step(line)

    def reset_fail_message(self):
        self._fail_message = []

    def add_fail_message(self, message: str):
        self._fail_message.append(message)

    def add_fail_messages(self, messages: List[str]):
        self._fail_message += messages

    def add_output_message(self, message: str):
        self._pytest_output += message + "\n"
        self.log(message)

    def add_output_messages(self, messages: List[str]):
        if messages:
            message = "\n\t *" + "\n\t *".join(messages) + "\n"
            self._pytest_output += message
            self.log(message)

    def fail_if_message(self):
        fail_log_message = "Fail Message(s) for test [" + self.id() + "]:\n" + "\n".join(self._fail_message)
        if len(self._fail_message) != 0:
            self.log(fail_log_message)
        assert len(self._fail_message) == 0, "\n" + fail_log_message

    def then_everything_should_be_fine(self, fail_messages=None):
        if fail_messages:
            self.log("Failure messages:")
            self.add_fail_messages(fail_messages)

        self.log_step('Then everything is successfully returned on all requests')
        self.fail_if_message()

    def flush_api_messages(self, api: ApiBase):
        self.add_fail_messages(api.error_messages)
        self.add_output_messages(api.output_messages)

    def flush_page_messages(self, page: PageBase):
        self.add_fail_messages(page.error_messages)
        self.add_output_messages(page.output_messages)

    def data_test_file_path(self, filename):
        return os.path.join(
            os.path.dirname(os.path.abspath(__file__)),
            "data",
            filename
        )
