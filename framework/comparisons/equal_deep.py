
class EqualDeep:
    def __init__(self):
        self.error_messages = []

    def run(self, target, **kwargs):
        if target is None:
            self.error_messages.append("No target - None")
            return None

        error_messages = []
        for d in kwargs:
            if d in target.__dict__ and not d.startswith("_"):
                if target.__dict__[d] != kwargs[d]:
                    error_messages.append("different {}: {} != {}".format(d, target.__dict__[d], kwargs[d]))
        self.error_messages += error_messages
        equal_flag = len(error_messages) == 0
        return equal_flag

    def two_objects(self, obj_1, obj_2):
        if obj_1 is None:
            self.error_messages.append("No target - obj_1")
            return None
        if obj_2 is None:
            self.error_messages.append("No target - obj_2")
            return None

        return self.run(obj_1, **obj_2.__dict__)
