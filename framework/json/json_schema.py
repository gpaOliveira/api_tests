import fastjsonschema
import json


class JsonSchemaCheckerException(Exception):
    pass


class JsonSchemaChecker:
    LOADED_VALIDATE = {}

    @staticmethod
    def validate(data, schema):
        if schema in JsonSchemaChecker.LOADED_VALIDATE:
            validate = JsonSchemaChecker.LOADED_VALIDATE[schema]
        else:
            with open(schema) as f:
                schema_json = json.loads(f.read())

            validate = fastjsonschema.compile(schema_json)
        try:
            return validate(data)
        except fastjsonschema.exceptions.JsonSchemaException as e:
            raise JsonSchemaCheckerException(str(e))