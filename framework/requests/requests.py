import pdb
import os
import requests
import logging
import copy
from multiprocessing import Process, Queue
import urllib.request
import json
from time import sleep
from datetime import datetime
from framework.log.logger import Logger
from framework.datetime.datetime import now_to_str

class Requests:
    METHOD_GET = "GET"
    METHOD_POST = "POST"
    METHOD_HEAD = "HEAD"
    METHOD_PUT = "PUT"
    TIMEOUT = 30
    VERIFY_STATUS_CODE = "VERIFY_STATUS_CODE"
    VERIFY_HEADERS = "VERIFY_HEADERS"
    VERIFY_BODY_LEN = "VERIFY_BODY_LEN"
    CONTENT_TYPE_XML = "xml"
    CONTENT_TYPE_JSON = "json"
    CONTENT_TYPE_HTML = "html"
    CONTENT_TYPE_JPEG = "jpeg"
    CONTENT_TYPE_JPG = "jpg"
    CONTENT_TYPE_PNG = "png"
    CACHE_MODE_READ = False
    CACHE_MODE_WRITE = False
    CACHE_EXTENSION = ".cached.json"
    BASE_FOLDER = "."
    DEFAULT_VERIFICATIONS = [
        VERIFY_STATUS_CODE,
        VERIFY_HEADERS
    ]

    def __init__(self,
                 url,
                 method=METHOD_GET,
                 request_headers={},
                 authorization=None,
                 proxies=None,
                 plain_body=None,
                 json_body=None,
                 ignore_response_body=False,
                 expected_response_code=200,
                 expected_headers=None,
                 expected_verifications=DEFAULT_VERIFICATIONS,
                 override_base_filename=None,
                 override_base_folder=None
                 ):
        self.method = method
        self.url = url
        self.body = plain_body
        if not self.body and json_body:
            self.body = json.dumps(json_body)
        self.ignore_response_body = ignore_response_body
        self.request_headers = request_headers
        self.authorization = authorization
        self.proxies = proxies
        self.status_code = 0
        self.expected_response_code = expected_response_code
        self.response_headers = {}
        self.expected_headers = expected_headers
        self.expected_verifications = expected_verifications

        # Attributes to control caching (cached_filename) and where the data is stored when saved (filename)
        self.filename = None
        base_name = (
            self.__safe_string(self.url) + now_to_str()
            if not override_base_filename else override_base_filename
        )
        self._base_name = (
            os.path.join(
                override_base_folder if override_base_folder else self.BASE_FOLDER,
                base_name
            )
        )
        self.cached_filename = self._base_name + self.CACHE_EXTENSION

        # Declare response time (time between request and all download) and
        # latency time (time between request and response headers) and
        # full time (time between request and response saved in filesystem)
        self.elapsed_time = 0
        self.latency_time = 0
        self.full_time = 0

        # Declare the response data (in plain, as it came) and the dict representation of it
        # If the response content type is a binary one, nothing is saved in those
        # but a file is created with the proposed filename (and the flag self.is_binary is set to True)
        # Real data content len is also stored, for further checks with Header Content-Length
        self._data = None
        self.is_binary = False
        self._dict = None
        self.content_len = 0

        # Misc stuff
        self.error_messages = []
        self._request_begin_time = None
        self._requested = False
        self._retries = 3
        self._sleep_between_retries = 0.1
        self._logger = Logger(name=self.__class__.__name__)
        logging.getLogger("requests").setLevel(logging.ERROR)
        logging.getLogger("urllib").setLevel(logging.ERROR)
        logging.getLogger("urllib3").setLevel(logging.ERROR)
        requests.packages.urllib3.disable_warnings()

    @property
    def dict_data(self):
        if self._dict:
            return self._dict
        self.__load_payload()
        self._dict = self.__safe_json_load(self._data)
        return self._dict

    @property
    def data(self):
        if self._data:
            return self._data
        self.__load_payload()
        return self._data

    def save(self):
        Requests.CACHE_MODE_WRITE = True
        self.__save_json_data_if_cache_mode_enabled()
        Requests.CACHE_MODE_WRITE = False

    @staticmethod
    def load_from_file(filename):
        r = Requests(url="")
        Requests.CACHE_MODE_READ = True
        r.cached_filename = filename
        r.request()
        Requests.CACHE_MODE_READ = False
        return r

    def to_json(self):
        """
        Return a json representation of the public attributes of this object
        """
        translated_json = {}
        for k, v in self.__dict__.items():
            try:
                if not k.startswith("_"):
                    translated_json[k] = json.dumps(v)
                    translated_json[k] = v
            except TypeError as err:
                pass
        return translated_json

    def content_type(self):
        """
        Clear content_type, acquired from our CONTENT_TYPE_* variables
        """
        possible_extensions = [v for k, v in Requests.__dict__.items() if k.startswith("CONTENT_TYPE")]
        extension = self.__content_type_in(*possible_extensions)
        return extension

    def is_textual_type(self):
        return self.__content_type_in(self.CONTENT_TYPE_XML, self.CONTENT_TYPE_JSON, self.CONTENT_TYPE_HTML) is not None

    def is_binary_type(self):
        return self.__content_type_in(
            self.CONTENT_TYPE_PNG, self.CONTENT_TYPE_JPEG, self.CONTENT_TYPE_JPG
        ) is not None

    def copy(self):
        newone = self.__class__(url=self.url)
        for k, v in self.__dict__.items():
            try:
                newone.__dict__[k] = copy.deepcopy(v)
            except TypeError:
                pass
        return newone

    def request(self):
        """
        Use python-request lib to ask for a REST API_Base content and retrieve anything

        :return: The response data (same as self.response)
        """
        if self.__load_json_data_if_cache_mode_enabled():
            return True

        self.__start_timer()
        self.error_messages = []
        r = None
        try:
            r = requests.request(
                method=self.method,
                url=self.url,
                data=self.body,
                headers=self.request_headers,
                auth=self.authorization,
                proxies=self.proxies,
                verify=False,
                timeout=self.TIMEOUT
            )
            self.status_code = r.status_code
            self.__read_response_body(
                func_read_headers=lambda: {k: v for k, v in r.headers.items()} if r.headers else {},
                func_read_textual_data=lambda: r.text,
                func_read_binary_data=lambda: r.content,
            )
            self.elapsed_time = self.__stop_timer()
            self._requested = True
            self.__save_json_data_if_cache_mode_enabled()
            return True
        except Exception as err:
            self.error_messages.append(str(err))
            return False
        finally:
            if r:
                r.close()

    def urlopen(self):
        """
        Use python-urlib.urlopen to ask for a content. This handles exceptions gracefully and sleeps in bad error situations.

        :param sleep_time_err_case: the amount of time to sleep case a bad thing happens (404s and 500s are not bad things). Defaults to None.
        :return: True if no exception was raised - False otherwise (grab your content from self.response)
        """
        if self.__load_json_data_if_cache_mode_enabled():
            return True
        r = None
        self.__start_timer()
        for _ in range(self._retries):
            try:
                raw_request = urllib.request.Request(self.url, headers=self.request_headers)
                self._requested = True
                r = urllib.request.urlopen(raw_request, timeout=self.TIMEOUT)
                self.status_code = int(r.getcode())
                self.__read_response_body(
                    func_read_headers=lambda: {
                        x[0]: ",".join([h[1].replace(', ', ',')
                                        for h in r.getheaders() if h[0] == x[0]])
                        for x in r.getheaders()
                    },
                    func_read_textual_data=lambda: r.read().decode('utf-8'),
                    func_read_binary_data=lambda: r.read(),
                )
                self.__save_json_data_if_cache_mode_enabled()
                return True
            except urllib.request.HTTPError as err:
                self.status_code = int(err.code)
                self._data = err.read().decode('utf-8')
                return True
            except Exception as err:
                self.error_messages.append(str(err))
                sleep(self._sleep_between_retries)
        return False

    def log_summary(self):
        self._logger.log_debug("{} {} {} {}".format(self.method, self.url, self.status_code, self.elapsed_time))
        if self.body:
            self._logger.log_debug("Input=====> " + str(self.body))

        to_log_request_headers = {
            k: (
                v if "KEY" not in k.upper() and "TOKEN" not in k.upper() and "AUTHORIZATION" not in k.upper()
                else "**HIDDEN**"
            )
            for k, v in self.request_headers.items()
        }
        self._logger.log_debug("Headers =====> " + str(to_log_request_headers))
        if self._data or self.filename:
            self._logger.log_debug("Output =====> " + (str(self._data) if self._data else " Saved on " + self.filename))
        self._logger.log_debug("Output Headers =====> " + str(self.response_headers))
        self._logger.log_debug("")

    def requests_async(self, workers):
        """
        GET many requests for the same URL in asyncronous way - return a list of Request objects from the responses, without data,
        to avoid memory usage to grow.

        For the effect of a larger number of workers, read http://skipperkongen.dk/2016/09/09/easy-parallel-http-requests-with-python-and-asyncio/

        workers: the amount of requests to perform
        """
        # Start as many processes as needed with a small delay
        output = Queue()
        for _ in range(workers):
            Process(target=Requests.__requests_async, args=(self, output,)).start()
            sleep(0.01)
        responses = [output.get() for _ in range(workers)]
        new_requests = []
        for r in responses:
            new_request = self.copy()
            new_request.status_code = r.status_code
            new_request.response_headers = {k: v for k, v in r.headers.items()} if r.headers else {}
            new_requests.append(new_request)
        return new_requests

    def verification(self):
        """
        Verifies the response and populates self.error_messages if needed.

        The following validations are performed:

        * Expected status code returned on response(default 200).
        * Non-empty data body
        * Expected headers values (including that Server headers has the right "VSPP_VERSION")

        :return: if error messages exists (same as len(self.error_messages) > 0)
        """
        if not self._requested:
            return len(self.error_messages) == 0

        if self.error_messages:
            return len(self.error_messages) == 0

        if self.__should_verify(self.VERIFY_STATUS_CODE):
            status = self.verify_status_code()
            # If the request has failed, no point in performing further validation.
            # If we try and validate BODY_LEN after a fail and no data returned an exception will be raised.
            #    TypeError: object of type 'NoneType' has no len()
            if not status:
                return status

        if self.__should_verify(self.VERIFY_BODY_LEN):
            self.verify_body_len()

        if self.__should_verify(self.VERIFY_HEADERS):
            self.verify_response_headers()

        return len(self.error_messages) == 0

    def verify_status_code(self):
        status = self.status_code == self.expected_response_code
        if not status:
            self.error_messages.append(
                "Request {0} returned a {1} response code".format(
                    self.url, self.status_code
                )
            )
        self._logger.log(
            "[{}] Status Code Check".format(
                "OK" if not self.error_messages else "BAD"
            )
        )
        return len(self.error_messages) == 0

    def verify_response_headers(self):
        """
        Verifies the response expected headers values and populates self.error_messages.

        If the expected header value is N/A, only verify the header existence but not its value

        :param expected_headers: A custom dictionary of expected headers and values. Default to None (will use self.default_headers)

        :return: Error messages (same as self.error_messages)
        """

        for header_field_to_verify in self.expected_headers:
            expected = self.expected_headers[header_field_to_verify]
            if expected == "N/A":
                if header_field_to_verify not in self.response_headers:
                    self.error_messages.append(
                        "\n Expected to find header '{}' but it wasn't in {}".format(
                            header_field_to_verify,
                            self.url
                        )
                    )
            else:
                actual = self.response_headers.get(header_field_to_verify, "N/A")
                if actual != expected:
                    self.error_messages.append(
                        "Expected value for '{}' is '{}' but response header had '{}'".format(
                            header_field_to_verify,
                            expected,
                            actual
                        )
                    )
        self._logger.log(
            "[{}] Headers Check".format(
                "OK" if not self.error_messages else "BAD"
            )
        )
        return len(self.error_messages) == 0

    def verify_body_len(self):
        header_content_len = self.response_headers.get('Content-Length', 0)
        status = self.content_len != header_content_len
        if not status:
            self.error_messages.append(
                "Request {} returned {} bytes while Content-Length header had {}".format(
                    self.url,
                    self.content_len,
                    header_content_len
                )
            )
        self._logger.log(
            "[{}] Body Len Check".format(
                "OK" if not self.error_messages else "BAD"
            )
        )
        return len(self.error_messages) == 0

    @staticmethod
    def __requests_async(request, output):
        response = requests.request(
            method=Requests.METHOD_GET,
            url=request.url,
            headers=request.request_headers,
            auth=request.authorization,
            proxies=request.proxies,
            verify=False
        )
        output.put(response)

    @staticmethod
    def __safe_string(unsafe_string):
        return (
            unsafe_string.
                replace(":", ".").
                replace("/", ".").
                replace("$", ".").
                replace("?", ".").
                replace("=", ".").
                replace("(", ".").
                replace(")", ".").
                replace("&", ".").
                replace("...", ".").
                replace("..", ".")
        )

    def __load_json_data_if_cache_mode_enabled(self):
        if self.CACHE_MODE_READ:
            try:
                with open(self.cached_filename) as f:
                    response = json.load(f)
                    for k, v in self.__dict__.items():
                        if k in response:
                            self.__dict__[k] = response[k]
                    self._logger.log("Loaded public data from {}".format(self.cached_filename))
                    self._requested = True
                    return True
            except Exception as e:
                raise e
        return False

    def __save_json_data_if_cache_mode_enabled(self):
        if self.CACHE_MODE_WRITE:
            content_type = self.content_type()
            if (self._data is not None or self._dict is not None) and content_type:
                self.filename = self._base_name + "." + content_type
                if self._dict is not None:
                    with open(self.filename, "w") as f:
                        f.write(json.dumps(self._dict, indent=4))
                elif self._data is not None and type(self._data) == str:
                    with open(self.filename, "w") as f:
                        f.write(self._data)
                elif self._data is not None:
                    with open(self.filename, "wb") as f:
                        f.write(self._data)
            with open(self.cached_filename, "w") as f:
                f.write(json.dumps(self.to_json(), indent=4, ensure_ascii=True, sort_keys=True))
            self._logger.log("Saved public data on {}".format(self.cached_filename))
            return True
        return False

    def __start_timer(self):
        self._request_begin_time = datetime.now().timestamp()

    def __stop_timer(self):
        return round(datetime.now().timestamp() - self._request_begin_time, 6) if self._request_begin_time else 0

    def __read_response_body(self, func_read_headers, func_read_textual_data, func_read_binary_data):
        """
        Read the response, independently on how it was got

        This is achieved thanks to the functional parameters, functions that allow it to read headers and response.

        The textual function will be used if the content type is either XML, JSON, or HTML. In this case, the
        self.is_binary attribute will be False and self.data will be populated.

        The binary function will be used if the content type is either MP4, MP2T, or image. In this case, the
        self.is_binary attribute will be True and self.data will NOT be populated - a file will be saved with
        the content for later manipulations.

        :param func_read_headers: a function defining how to read the headers of the response
        :param func_read_textual_data: a function defining how to read textual data - will be used depending on the content type
        :param func_read_binary_data: a function defining how to read binary data - will be used depending on the content type
        :return:
        """
        self.response_headers = func_read_headers()
        self.latency_time = self.__stop_timer()
        self._data = None
        self.is_binary = False
        if self.ignore_response_body or self.method == self.METHOD_HEAD:
            return
        textual_type = self.is_textual_type()
        binary_type = self.is_binary_type()
        if textual_type:
            self._data = func_read_textual_data()
            self.elapsed_time = self.__stop_timer()
            self.content_len = len(self._data)
            self._dict = self.__safe_json_load(self._data)
            self.full_time = self.__stop_timer()
        elif binary_type:
            self.is_binary = True
            self._data = func_read_binary_data()
            self.elapsed_time = self.__stop_timer()
            self.content_len = len(self._data)
            self.full_time = self.__stop_timer()
        elif not textual_type and not binary_type:
            self._data = func_read_textual_data()
            self.elapsed_time = self.__stop_timer()
            self.content_len = len(self._data)
            self.full_time = self.__stop_timer()
        else:
            # should never happen, as no two CONTENT_TYPE constant should match at the same time
            self.error_messages.append("Something wrong on __read_body")

    def __load_payload(self):
        if self.filename is None:
            return
        if not os.path.exists(self.filename):
            return
        if self._data is not None:
            return

        # Else
        with open(self.filename, 'r', encoding='utf8') as f:
            self._data = f.read()

    def __content_type_in(self, *args):
        content_types = [
            x
            for x in args
            if x in self.response_headers.get("Content-Type", "").lower()
        ]
        return content_types[0] if content_types else None

    def __should_verify(self, verification_constant):
        return verification_constant in self.expected_verifications

    def __safe_json_load(self, json_data):
        """
        Safelly (no exceptions) parses string to dictionary
        :param string_data: json data as string
        :return: parsed dictionary data
        """
        data = None
        try:
            data = json.loads(json_data)
        except Exception as e:
            pass
        return data
