from ddx.rest_client.clients.base_client import BaseClient

GET_KYC_TEST_ACCOUNT = "/kyc/v1/test-account"


class TestKYCClient(BaseClient):
    """Test-only KYC operations."""

    async def add_test_account(self, trader_address: str):
        """
        Add a test account to KYC whitelist (testnet only).

        Parameters
        ----------
        trader_address : str
            Address to whitelist for testing
        """

        params = {"trader": trader_address}

        # Make the request
        return await self._http.get(
            self._build_url(GET_KYC_TEST_ACCOUNT), params=params
        )
