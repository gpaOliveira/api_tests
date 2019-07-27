from typing import List
import logging
import os
import sys
from framework.datetime.datetime import now_to_str


class Logger:
    def __init__(self, name=None, debug=False):
        self.name = name
        self.test_name = os.environ.get("PYTEST_CURRENT_TEST", name)
        self._format = "%(asctime)-15s %(name)s %(message)s"
        self._logging_level = logging.DEBUG if debug else logging.INFO
        self.logging_filename = self.__initialize_filename()
        self._logger = self.__initialize_log()

    def __initialize_filename(self):
        base_directory = os.sep.join(os.path.dirname(__file__).split(os.sep)[:-2])
        test_logs_directory = os.path.join(base_directory, "logs")
        if not os.path.exists(test_logs_directory):
            os.makedirs(test_logs_directory)
        return os.path.join(test_logs_directory, "{}_{}.txt".format(self.test_name, now_to_str()))

    def __initialize_log(self):
        log = logging.getLogger(self.test_name)
        log.setLevel(self._logging_level)

        if not len(log.handlers):
            format = logging.Formatter(self._format)
            ch = logging.StreamHandler(sys.stdout)
            ch.setFormatter(format)
            log.addHandler(ch)

            fh = logging.FileHandler(self.logging_filename)
            fh.setFormatter(format)
            log.addHandler(fh)
        return log

    def log(self, line: str):
        self._logger.info("[{}] {}".format(self.name, line) if self.name else line)

    def log_debug(self, line: str):
        self._logger.debug("[{}] {}".format(self.name, line) if self.name else line)

    def log_multiple(self, logs: List[str]):
        for l in logs:
            self.log(l)

    def log_step(self, line):
        self.log("="*100 + " " + line)
