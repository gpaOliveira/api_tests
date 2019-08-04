import json


class MarketplaceProduct:
    def __init__(self, raw_product):
        self.description = raw_product.get("description")
        self.product_id = raw_product.get("id")
        self.name = raw_product.get("name")

    def __str__(self):
        return "{}:\n{}".format(self.__class__.__name__, json.dumps(self.to_json(), indent=4))

    def to_json(self):
        return {
            "description": self.description,
            "product_id ": self.product_id ,
            "name": self.name
        }