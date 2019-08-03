import os
from framework.log.logger import Logger
import json
from functools import reduce
import pdb


class Environment:
    """
    @DynamicAttrs loaded as part of load_environment_json
    """

    def __init__(self):
        self._data = {}
        self._logger = Logger(name=self.__class__.__name__, debug=True)
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

        variables_to_check = [
            'GITLAB_KEY',
            'GITHUB_KEY',
            'LOBSTER_EMAIL',
            'LOBSTER_PASSWORD'
        ]
        status_variables = {}

        for v in variables_to_check:
            a = getattr(self, v)
            status_variables[v] = True
            if a is None or len(a) <= 0:
                self._logger.log("No {} found - export one".format(v))
                status_variables[v] = False

        self._logger.log("Export variables check")
        self._logger.log(json.dumps(status_variables, indent=4))
        return reduce(lambda x, y: x and y, list(status_variables.values()))

    def load_environment_json(self):
        self._data = {}
        data = {}
        try:
            with open(self._default_values_file) as f:
                data = json.loads(f.read())
        except:
            pass

        if not data:
            self._logger.log("Failed to load {}".format(self._default_values_file))
            return

        for d in data:
            if d in os.environ:
                self._logger.log("Loaded {} from OS".format(d))
                self.__dict__[d] = os.environ[d]
            else:
                self._logger.log("Loaded {} from JSON".format(d))
                self.__dict__[d] = data[d]
