import os
from framework.log.logger import Logger
import json


class Environment:
    """
    @DynamicAttrs loaded as part of load_environment_json
    """

    def __init__(self):
        self._data = {}
        self._logger = Logger(self.__class__.__name__)
        self._default_values_file = os.path.join(
            os.path.dirname(os.path.abspath(__file__)),
            "environment.json"
        )
        self.load_environment_json()
        self.check_variables()

    def __getattr__(self, name):
        """
        Python magic to avoid AttributeError exception

        https://stackoverflow.com/questions/45234632/how-to-prevent-attributeerror-for-undeclared-variables-and-methods-and-fix-get
        :param name:
        :return:
        """
        if name not in self.__dict__:
            return ""

        return self.__dict__[name]

    def check_variables(self):
        if self.gitlab_key is None or len(self.gitlab_key) <= 0:
            self._logger.log("No GITLAB_KEY found - export one")
            return False
        return True

    def load_environment_json(self):
        self._data = {}
        data = {}
        try:
            with open(self._default_values_file) as f:
                data = json.load(f.read())
        except:
            pass

        for d in data:
            if d in os.environ:
                self._logger.log("Loaded {} from OS".format(d))
                self.__dict__[d] = os.environ[d]
            else:
                self._logger.log("Loaded {} from JSON".format(d))
                self.__dict__[d] = data[d]
