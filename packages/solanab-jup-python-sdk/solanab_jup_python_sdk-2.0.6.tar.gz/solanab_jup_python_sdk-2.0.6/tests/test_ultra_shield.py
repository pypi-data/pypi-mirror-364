import pytest
from dotenv import load_dotenv

from jup_python_sdk.clients.ultra_api_client import AsyncUltraApiClient, UltraApiClient


def test_ultra_shield() -> None:
    """
    Test the sync UltraApiClient shield method.
    """
    load_dotenv()
    client = UltraApiClient()

    # WSOL and USDC mints
    wsol_mint = "So11111111111111111111111111111111111111112"
    usdc_mint = "EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v"

    try:
        shield_response = client.shield(mints=[wsol_mint, usdc_mint])
        assert "warnings" in shield_response, (
            "Response does not contain 'warnings' key."
        )

        print()
        print("Shield API Response:")
        if shield_response.get("warnings"):
            for mint, warnings in shield_response["warnings"].items():
                print(f"Mint: {mint}")
                for warning in warnings:
                    print(f"  - Type: {warning.get('type')}")
                    print(f"    Message: {warning.get('message')}")
        else:
            print("No warnings returned for provided mints")

    except Exception as e:
        print("Error occurred while fetching shield information:", str(e))
    finally:
        client.close()


@pytest.mark.asyncio
async def test_async_ultra_shield() -> None:
    """
    Test the async UltraApiClient shield method.
    """
    load_dotenv()
    client = AsyncUltraApiClient()

    # WSOL and USDC mints
    wsol_mint = "So11111111111111111111111111111111111111112"
    usdc_mint = "EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v"

    try:
        shield_response = await client.shield(mints=[wsol_mint, usdc_mint])
        assert "warnings" in shield_response, (
            "Response does not contain 'warnings' key."
        )

        print()
        print("Async Shield API Response:")
        if shield_response.get("warnings"):
            for mint, warnings in shield_response["warnings"].items():
                print(f"Mint: {mint}")
                for warning in warnings:
                    print(f"  - Type: {warning.get('type')}")
                    print(f"    Message: {warning.get('message')}")
    except Exception as e:
        print("Error occurred while fetching async shield information:", str(e))
    finally:
        await client.close()
