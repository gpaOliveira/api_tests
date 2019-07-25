import pdb
from typing import List
from framework.log.logger import Logger
from framework.requests.requests import Requests


class ApiBase:

    def __init__(self):
        # error messages that will make tests fails
        self.error_messages = []

        # log messages to be used for logging in pytest results
        self.output_messages = []

        # requests data
        self.expected_status_code = 200
        self.response_code = -1
        self.headers = {}
        self.data = ""
        self.filename = ""
        self.verification_status = False

        # Other useful declarations for the children to use
        self.logger = Logger(self.__class__.__name__)

    def log(self, line):
        self.logger.log(line)

    def log_multiple(self, logs: List[str]):
        self.logger.log_multiple(logs)

    def request(self,
                name,
                url,
                method=Requests.METHOD_GET,
                headers={},
                request_headers={},
                body=None,
                json_body=None,
                expected_verification=Requests.DEFAULT_VERIFICATIONS,
                expected_response_code=200,
                override_base_filename=None,
                override_base_folder=None
                ):
        request = Requests(
            url=url,
            method=method,
            expected_headers=headers,
            request_headers=request_headers,
            plain_body=body,
            json_body=json_body,
            expected_verifications=expected_verification,
            expected_response_code=expected_response_code,
            override_base_filename=override_base_filename,
            override_base_folder=override_base_folder
        )
        request.request()
        self.verification_status = request.verification()
        printable_attr = "[" + name + " Request] "
        self.error_messages += [
            printable_attr + error
            for error in request.error_messages
        ]
        self.response_code = int(request.status_code)
        self.headers = request.response_headers
        self.filename = request.filename
        last_raw_data = request.data
        last_dict_data = request.dict_data
        self.data = last_dict_data if last_dict_data else last_raw_data
        request.save()
        request.log_summary()
        return self.data
