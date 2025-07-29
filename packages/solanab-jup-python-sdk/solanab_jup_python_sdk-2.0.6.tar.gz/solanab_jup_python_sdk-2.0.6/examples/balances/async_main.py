import asyncio

from dotenv import load_dotenv

from jup_python_sdk.clients.ultra_api_client import AsyncUltraApiClient


async def main():
    load_dotenv()
    client = AsyncUltraApiClient()

    address = await client.get_public_key()

    try:
        balances_response = await client.balances(str(address))

        print("Balances API Response (Async):")
        for token, details in balances_response.items():
            print(f"Token: {token}")
            print(f"  - Amount: {details['amount']}")
            print(f"    UI Amount: {details['uiAmount']}")
            print(f"    Slot: {details['slot']}")
            print(f"    Is Frozen: {details['isFrozen']}")

    except Exception as e:
        print("Error occurred while fetching balances:", str(e))
    finally:
        await client.close()


if __name__ == "__main__":
    asyncio.run(main())
