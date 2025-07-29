from typing import Any

from jup_python_sdk.clients.jupiter_client import AsyncJupiterClient, JupiterClient
from jup_python_sdk.models.ultra_api.ultra_execute_request_model import (
    UltraExecuteRequest,
)
from jup_python_sdk.models.ultra_api.ultra_order_request_model import (
    UltraOrderRequest,
)


class UltraApiClient(JupiterClient):
    """
    A synchronous client for interacting with the Jupiter Ultra API.
    """

    def order(self, request: UltraOrderRequest) -> dict[str, Any]:
        """
        Get an order from the Jupiter Ultra API (synchronous).

        Args:
            request (UltraOrderRequest): The request parameters for the order.

        Returns:
            dict: The dict api response.
        """
        params = request.to_dict()

        url = f"{self.base_url}/ultra/v1/order"
        response = self.client.get(url, params=params, headers=self._get_headers())
        response.raise_for_status()

        return response.json()  # type: ignore[no-any-return]  # type: ignore

    def execute(self, request: UltraExecuteRequest) -> dict[str, Any]:
        """
        Execute the order with the Jupiter Ultra API (synchronous).

        Args:
            request (UltraExecuteRequest): The execute request parameters.

        Returns:
            dict: The dict api response.
        """
        payload = request.to_dict()

        url = f"{self.base_url}/ultra/v1/execute"
        response = self.client.post(url, json=payload, headers=self._get_headers())
        response.raise_for_status()

        return response.json()  # type: ignore[no-any-return]  # type: ignore

    def order_and_execute(self, request: UltraOrderRequest) -> dict[str, Any]:
        """
        Get and execute an order in a single call (synchronous).

        Args:
            request (UltraOrderRequest): The request parameters for the order.

        Returns:
            dict: The dict api response.
        """
        order_response = self.order(request)

        request_id = order_response["requestId"]
        signed_transaction = self._sign_base64_transaction(
            order_response["transaction"]
        )

        execute_request = UltraExecuteRequest(
            request_id=request_id,
            signed_transaction=self._serialize_versioned_transaction(
                signed_transaction
            ),
        )

        return self.execute(execute_request)

    def balances(self, address: str) -> dict[str, Any]:
        """
        Get token balances of an account (synchronous).

        Args:
            address (str): The public key of the account to get balances for.

        Returns:
            dict: The dict api response.
        """
        url = f"{self.base_url}/ultra/v1/balances/{address}"
        response = self.client.get(url, headers=self._get_headers())
        response.raise_for_status()

        return response.json()  # type: ignore[no-any-return]  # type: ignore

    def shield(self, mints: list[str]) -> dict[str, Any]:
        """
        Get token info and warnings for specific mints (synchronous).

        Args:
            mints (list[str]): List of token mint addresses
            to get information for.

        Returns:
            dict: The dict api response with warnings information.
        """
        params = {"mints": ",".join(mints)}

        url = f"{self.base_url}/ultra/v1/shield"
        response = self.client.get(url, params=params, headers=self._get_headers())
        response.raise_for_status()

        return response.json()  # type: ignore[no-any-return]  # type: ignore


class AsyncUltraApiClient(AsyncJupiterClient):
    """
    An asynchronous client for interacting with the Jupiter Ultra API.
    """

    async def order(self, request: UltraOrderRequest) -> dict[str, Any]:
        """
        Get an order from the Jupiter Ultra API (asynchronous).

        Args:
            request (UltraOrderRequest): The request parameters for the order.

        Returns:
            dict: The dict api response.
        """
        params = request.to_dict()

        url = f"{self.base_url}/ultra/v1/order"
        response = await self.client.get(
            url, params=params, headers=self._get_headers()
        )
        response.raise_for_status()

        return response.json()  # type: ignore[no-any-return]

    async def execute(self, request: UltraExecuteRequest) -> dict[str, Any]:
        """
        Execute the order with the Jupiter Ultra API (asynchronous).

        Args:
            request (UltraExecuteRequest): The execute request parameters.

        Returns:
            dict: The dict api response.
        """
        payload = request.to_dict()

        url = f"{self.base_url}/ultra/v1/execute"
        response = await self.client.post(
            url, json=payload, headers=self._get_headers()
        )
        response.raise_for_status()

        return response.json()  # type: ignore[no-any-return]

    async def order_and_execute(self, request: UltraOrderRequest) -> dict[str, Any]:
        """
        Get and execute an order in a single call (asynchronous).

        Args:
            request (UltraOrderRequest): The request parameters for the order.

        Returns:
            dict: The dict api response.
        """
        order_response = await self.order(request)

        request_id = order_response["requestId"]
        signed_transaction = self._sign_base64_transaction(
            order_response["transaction"]
        )

        execute_request = UltraExecuteRequest(
            request_id=request_id,
            signed_transaction=self._serialize_versioned_transaction(
                signed_transaction
            ),
        )

        return await self.execute(execute_request)

    async def balances(self, address: str) -> dict[str, Any]:
        """
        Get token balances of an account (asynchronous).

        Args:
            address (str): The public key of the account to get balances for.

        Returns:
            dict: The dict api response.
        """
        url = f"{self.base_url}/ultra/v1/balances/{address}"
        response = await self.client.get(url, headers=self._get_headers())
        response.raise_for_status()

        return response.json()  # type: ignore[no-any-return]

    async def shield(self, mints: list[str]) -> dict[str, Any]:
        """
        Get token info and warnings for specific mints (asynchronous).
        """
        params = {"mints": ",".join(mints)}
        url = f"{self.base_url}/ultra/v1/shield"
        response = await self.client.get(
            url, params=params, headers=self._get_headers()
        )
        response.raise_for_status()

        return response.json()  # type: ignore[no-any-return]
