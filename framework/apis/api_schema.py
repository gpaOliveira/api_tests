import fastjsonschema
import json

class ApiSchemaCheckerException(Exception):
    pass


class ApiSchemaChecker:
    LOADED_VALIDATE = {}

    def __init__(self):
        pass

    @staticmethod
    def validate(data, schema):
        if schema in ApiSchemaChecker.LOADED_VALIDATE:
            validate = ApiSchemaChecker.LOADED_VALIDATE[schema]
        else:
            with open(schema) as f:
                schema_json = json.loads(f.read())

            validate = fastjsonschema.compile(schema_json)
        try:
            return validate(data)
        except fastjsonschema.exceptions.JsonSchemaException as e:
            raise ApiSchemaCheckerException(str(e))