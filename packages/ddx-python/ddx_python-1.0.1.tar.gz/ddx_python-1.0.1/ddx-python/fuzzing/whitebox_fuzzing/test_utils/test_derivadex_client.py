"""
TestDerivaDEX Client
"""
from typing import Optional

from ddx.derivadex_client import DerivaDEXClient
from whitebox_fuzzing.test_utils.test_kyc_client import TestKYCClient
from whitebox_fuzzing.test_utils.test_on_chain_client import TestOnChainClient


class TestDerivaDEXClient(DerivaDEXClient):
    """
    Test-enabled DerivaDEX client with additional testing functionality.
    Extends the standard client with test-only operations.
    """

    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self._test_kyc: Optional[TestKYCClient] = None
        self._on_chain: Optional[TestOnChainClient] = None

    @property
    def kyc(self) -> TestKYCClient:
        """Access test KYC operations."""

        if self._test_kyc is None:
            self._test_kyc = TestKYCClient(self._http, self._base_url)

        return self._test_kyc

    @property
    def on_chain(self) -> TestOnChainClient:
        """
        Access on-chain operations.
        Overrides base on chain client to provide test functionality.
        """

        if self._on_chain is None:
            self._on_chain = TestOnChainClient(
                self._http,
                self._base_url,
                self.web3_account,
                self.w3,
                self._verifying_contract,
            )

        return self._on_chain
