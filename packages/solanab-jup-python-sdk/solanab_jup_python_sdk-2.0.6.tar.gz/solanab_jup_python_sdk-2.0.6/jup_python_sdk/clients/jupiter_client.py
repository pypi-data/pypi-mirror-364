import base64
import json
import os
from typing import Any, Optional

import base58
from curl_cffi import AsyncSession, requests
from solders.solders import Keypair, VersionedTransaction


class _CoreJupiterClient:
    """
    Core non-network-dependent logic for Jupiter clients.
    Handles private key loading and transaction signing.
    """

    def __init__(self, api_key: Optional[str], private_key_env_var: str):
        """
        Initialize the core Jupiter client.

        Args:
            api_key: Optional API key for enhanced access to Jupiter API.
                If provided, uses https://api.jup.ag endpoint.
            private_key_env_var: Name of environment variable containing the
                private key. Defaults to 'PRIVATE_KEY'.
        """
        self.api_key = api_key
        self.base_url = "https://api.jup.ag" if api_key else "https://lite-api.jup.ag"
        self.private_key_env_var = private_key_env_var

    def _get_headers(self) -> dict[str, str]:
        """
        Get headers for GET requests.

        Returns:
            Dict containing headers with Accept and optional API key.
        """
        headers = {
            "Accept": "application/json",
        }
        if self.api_key:
            headers["x-api-key"] = self.api_key
        return headers

    def _post_headers(self) -> dict[str, str]:
        """
        Get headers for POST requests.

        Returns:
            Dict containing headers with Accept, Content-Type, and optional API key.
        """
        headers = {
            "Accept": "application/json",
            "Content-Type": "application/json",
        }
        if self.api_key:
            headers["x-api-key"] = self.api_key
        return headers

    def _load_private_key_bytes(self) -> bytes:
        """Loads the private key from the environment
        variable as base58 or uint8 array."""
        pk_raw = os.getenv(self.private_key_env_var, "")
        pk_raw = pk_raw.strip()
        if pk_raw.startswith("[") and pk_raw.endswith("]"):
            try:
                arr = json.loads(pk_raw)
                if isinstance(arr, list) and all(
                    isinstance(x, int) and 0 <= x <= 255 for x in arr
                ):
                    return bytes(arr)
                else:
                    raise ValueError
            except Exception as e:
                raise ValueError(f"Invalid uint8-array private key format: {e}") from e
        try:
            return base58.b58decode(pk_raw)
        except Exception as e:
            raise ValueError(f"Invalid base58 private key format: {e}") from e

    def get_public_key(self) -> str:
        """
        Get the public key from the loaded private key.

        Returns:
            Public key as a base58-encoded string.
        """
        wallet = Keypair.from_bytes(self._load_private_key_bytes())
        return str(wallet.pubkey())

    async def get_public_key_async(self) -> str:
        """
        Async wrapper for get_public_key().

        Returns:
            Public key as a base58-encoded string.
        """
        return self.get_public_key()

    def _sign_base64_transaction(self, transaction_base64: str) -> VersionedTransaction:
        """
        Sign a base64-encoded transaction.

        Args:
            transaction_base64: Base64-encoded transaction string.

        Returns:
            Signed VersionedTransaction object.
        """
        transaction_bytes = base64.b64decode(transaction_base64)
        versioned_transaction = VersionedTransaction.from_bytes(transaction_bytes)
        return self._sign_versioned_transaction(versioned_transaction)

    def _sign_versioned_transaction(
        self, versioned_transaction: VersionedTransaction
    ) -> VersionedTransaction:
        """
        Sign a VersionedTransaction with the loaded private key.

        Args:
            versioned_transaction: VersionedTransaction to sign.

        Returns:
            Signed VersionedTransaction with signature applied.
        """
        wallet = Keypair.from_bytes(self._load_private_key_bytes())
        account_keys = versioned_transaction.message.account_keys
        wallet_index = account_keys.index(wallet.pubkey())

        signers = list(versioned_transaction.signatures)
        signers[wallet_index] = wallet  # type: ignore

        return VersionedTransaction(
            versioned_transaction.message,
            signers,  # type: ignore
        )

    def _serialize_versioned_transaction(
        self, versioned_transaction: VersionedTransaction
    ) -> str:
        """
        Serialize a VersionedTransaction to base64 string.

        Args:
            versioned_transaction: VersionedTransaction to serialize.

        Returns:
            Base64-encoded string representation of the transaction.
        """
        return base64.b64encode(bytes(versioned_transaction)).decode("utf-8")


class JupiterClient(_CoreJupiterClient):
    """
    The synchronous client for interacting with the Jupiter API.
    Powered by curl_cffi.
    """

    def __init__(
        self,
        api_key: Optional[str] = None,
        private_key_env_var: str = "PRIVATE_KEY",
        client_kwargs: Optional[dict[str, Any]] = None,
    ):
        """
        Initialize the synchronous Jupiter client.

        Args:
            api_key: Optional API key for enhanced access to Jupiter API.
            private_key_env_var: Name of environment variable containing the
                private key.
            client_kwargs: Optional kwargs to pass to curl_cffi Session.
                Common options include 'proxies', 'timeout', 'impersonate'.
        """
        super().__init__(api_key, private_key_env_var)
        kwargs = client_kwargs or {}
        # Use realworld random browser impersonation based on market share
        # if not specified
        kwargs.setdefault("impersonate", "realworld")
        self.client = requests.Session(**kwargs)

    def close(self) -> None:
        """
        Close the underlying HTTP session.

        Always call this method when done to properly cleanup resources.
        """
        self.client.close()


class AsyncJupiterClient(_CoreJupiterClient):
    """
    The asynchronous client for interacting with the Jupiter API.
    Powered by curl_cffi.
    """

    def __init__(
        self,
        api_key: Optional[str] = None,
        private_key_env_var: str = "PRIVATE_KEY",
        client_kwargs: Optional[dict[str, Any]] = None,
    ):
        """
        Initialize the asynchronous Jupiter client.

        Args:
            api_key: Optional API key for enhanced access to Jupiter API.
            private_key_env_var: Name of environment variable containing the
                private key.
            client_kwargs: Optional kwargs to pass to curl_cffi AsyncSession.
                Common options include 'proxies', 'timeout', 'impersonate'.
        """
        super().__init__(api_key, private_key_env_var)
        kwargs = client_kwargs or {}
        # Use realworld random browser impersonation based on market share
        # if not specified
        kwargs.setdefault("impersonate", "realworld")
        self.client = AsyncSession(**kwargs)

    async def close(self) -> None:
        """
        Close the underlying HTTP session.

        Always call this method when done to properly cleanup resources.
        """
        await self.client.close()

    # Override get_public_key for async context consistency
    async def get_public_key(self) -> str:  # type: ignore[override]
        """
        Get the public key from the loaded private key.

        Returns:
            Public key as a base58-encoded string.
        """
        return super().get_public_key()
