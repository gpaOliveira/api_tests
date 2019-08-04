from framework.apis.api_base import ApiBase
from framework.requests.requests import Requests
from framework.lobster.marketplace_product import MarketplaceProduct
from typing import List
import pdb
import os


class ApiLobster(ApiBase):
    def __init__(self, lobster_base):
        super().__init__()
        self.lobster_base = lobster_base
        self.tenant = "lobsterink"  # Maybe a parameter in the future

    def body_from_file(self, filename, **kwargs):
        file_path = os.path.join(
            os.path.dirname(os.path.abspath(__file__)),
            "data",
            filename
        )
        with open(file_path) as f:
            content = f.read()
        content = content.replace("\n", "")
        for param, value in kwargs.items():
            content = content.replace("{parameter_" + param + "}", str(value))
        return content

    def search_marketplace(self, preview=False, skip=0, take=9, text="") -> List[MarketplaceProduct]:
        body = self.body_from_file(
            filename="searchMarketplaceBase",
            preview=str(preview).lower(),
            skip=skip,
            take=take,
            text=text
        )
        search_raw = self.request(
            name="search_marketplace",
            method=Requests.METHOD_POST,
            request_headers={
                "tenant": self.tenant,
                "Content-Type": "application/json"
            },
            url=self.lobster_base,
            body=body,
            expected_response_code=200
        )
        if not self.verification_status:
            return []
        if not search_raw:
            return []

        return [
            MarketplaceProduct(p)
            for p in search_raw.get("data", {}).get("searchMarketplaceBase", {}).get("filteredProducts", [])
        ]
