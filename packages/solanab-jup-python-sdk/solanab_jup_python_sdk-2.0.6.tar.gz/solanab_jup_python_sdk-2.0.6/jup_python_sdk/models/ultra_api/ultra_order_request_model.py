from typing import Any, Optional

from pydantic import BaseModel
from pydantic.alias_generators import to_camel


class UltraOrderRequest(BaseModel):
    """
    Pydantic model for creating swap orders on Jupiter Ultra API.

    Attributes:
        input_mint: Mint address of the input token.
        output_mint: Mint address of the output token.
        amount: Amount to swap in the smallest unit (e.g., lamports for SOL).
        taker: Optional public key of the taker (usually your wallet address).
        referral_account: Optional referral account address for fee sharing.
        referral_fee: Optional referral fee in basis points (1 bp = 0.01%).
    """

    input_mint: str
    output_mint: str
    amount: int
    taker: Optional[str] = None
    referral_account: Optional[str] = None
    referral_fee: Optional[int] = None

    def to_dict(self) -> dict[str, Any]:
        """
        Convert the model to a dictionary with camelCase keys.

        Returns:
            Dict with camelCase keys suitable for API requests.
        """
        params = self.model_dump(exclude_none=True)

        camel_case_params = {to_camel(key): value for key, value in params.items()}

        return camel_case_params
