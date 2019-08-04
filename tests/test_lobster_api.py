from tests.test_base import ApiTestBase
from framework.apis.lobster.api_lobster import ApiLobster
from framework.lobster.marketplace_product import MarketplaceProduct
from typing import List


class TestLobsterApi(ApiTestBase):

    def test_lobster_search_products(self):
        """
        Given LOBSTER_API_BASE is provided
        When an API search for 'hotels' products is done
        Then some products are retrieved
        """
        self.log_step("When an API search for 'hotels' products is done")
        api = ApiLobster(self.environment.LOBSTER_API_BASE)
        products: List[MarketplaceProduct] = api.search_marketplace(text="hotels")
        self.flush_api_messages(api)

        self.log_step("Then some products are retrieved")
        for p in products:
            self.add_output_message(str(p))
        if not products:
            self.add_fail_message("No products retrieved")

        self.then_everything_should_be_fine()