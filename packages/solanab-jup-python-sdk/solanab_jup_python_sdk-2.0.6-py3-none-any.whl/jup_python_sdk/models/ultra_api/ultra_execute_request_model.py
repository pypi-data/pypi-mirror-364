from typing import Any

from pydantic import BaseModel
from pydantic.alias_generators import to_camel


class UltraExecuteRequest(BaseModel):
    """
    Pydantic model for executing a previously created order.

    Attributes:
        signed_transaction: Base64-encoded signed transaction string.
        request_id: The request ID returned from the order endpoint.
    """

    signed_transaction: str
    request_id: str

    def to_dict(self) -> dict[str, Any]:
        """
        Convert the model to a dictionary with camelCase keys.

        Returns:
            Dict with camelCase keys suitable for API requests.
        """
        params = self.model_dump(exclude_none=True)

        camel_case_params = {to_camel(key): value for key, value in params.items()}

        return camel_case_params
