#!/usr/bin/env python3
"""
Advanced example: Concurrent requests with async Jupiter SDK
"""

import asyncio
import time
from typing import Any

from jup_python_sdk.clients.ultra_api_client import AsyncUltraApiClient


async def check_token_safety(client: AsyncUltraApiClient, mint: str) -> dict[str, Any]:
    """Check a single token for safety warnings"""
    try:
        response = await client.shield(mints=[mint])
        return {
            "mint": mint,
            "warnings": response.get("warnings", {}).get(mint, []),
            "success": True,
        }
    except Exception as e:
        return {"mint": mint, "error": str(e), "success": False}


async def concurrent_token_check():
    """Check multiple tokens concurrently"""

    # Popular Solana tokens
    tokens = {
        "So11111111111111111111111111111111111111112": "WSOL",
        "EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v": "USDC",
        "Es9vMFrzaCERmJfrF4H2FYD4KCoNkY11McCe8BenwNYB": "USDT",
        "7vfCXTUXx5WJV5JADk17DUJ4ksgau7utNKj4b963voxs": "ETH",
        "DezXAZ8z7PnrnRJjz3wXBoRgixCa6xjnB7YaB1pPB263": "BONK",
        "HZ1JovNiVvGrGNiiYvEozEVgZ58xaU3RKwX8eACQBCt3": "PYTH",
        "jtojtomepa8beP8AuQc6eXt5FriJwfFMwQx2v2f9mCL": "JTO",
    }

    print(f"Checking {len(tokens)} tokens concurrently...\n")

    client = AsyncUltraApiClient()
    start_time = time.time()

    try:
        # Create tasks for all tokens
        tasks = [check_token_safety(client, mint) for mint in tokens.keys()]

        # Execute all requests concurrently
        results = await asyncio.gather(*tasks)

        # Process results
        print("=== Token Safety Check Results ===\n")

        safe_tokens = []
        warning_tokens = []

        for result in results:
            if result["success"]:
                token_name = tokens.get(result["mint"], "Unknown")

                if result["warnings"]:
                    warning_tokens.append((token_name, result))
                    print(f"⚠️  {token_name} ({result['mint'][:8]}...)")
                    for warning in result["warnings"]:
                        print(f"   - {warning.get('type')}: {warning.get('message')}")
                else:
                    safe_tokens.append(token_name)
                    print(f"✅ {token_name} ({result['mint'][:8]}...) - No warnings")
            else:
                print(f"❌ Failed to check {result['mint']}: {result.get('error')}")

        # Summary
        elapsed = time.time() - start_time
        print("\n=== Summary ===")
        print(f"Total tokens checked: {len(tokens)}")
        print(f"Safe tokens: {len(safe_tokens)}")
        print(f"Tokens with warnings: {len(warning_tokens)}")
        print(f"Time elapsed: {elapsed:.2f} seconds")
        print(f"Average time per request: {elapsed / len(tokens):.3f} seconds")

    finally:
        await client.close()


async def batch_balance_check():
    """Check balances for multiple addresses concurrently"""

    # Example addresses (you can replace with real ones)
    addresses = [
        "11111111111111111111111111111111",  # System program
        "TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA",  # Token program
        "EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v",  # USDC mint
    ]

    print(f"\nChecking balances for {len(addresses)} addresses...\n")

    client = AsyncUltraApiClient()

    async def get_balance(address: str):
        try:
            balance = await client.balances(address)
            return {"address": address, "balance": balance, "success": True}
        except Exception as e:
            return {"address": address, "error": str(e), "success": False}

    try:
        # Check all balances concurrently
        tasks = [get_balance(addr) for addr in addresses]
        results = await asyncio.gather(*tasks)

        # Display results
        for result in results:
            if result["success"]:
                print(f"Address: {result['address'][:16]}...")
                if result["balance"]:
                    for token, details in result["balance"].items():
                        print(f"  {token}: {details.get('uiAmount', 0)}")
                else:
                    print("  No balances found")
            else:
                print(f"Failed to check {result['address']}: {result['error']}")

    finally:
        await client.close()


async def rate_limited_requests():
    """Example of rate-limited concurrent requests"""

    print("\n=== Rate-Limited Concurrent Requests ===\n")

    # Semaphore to limit concurrent requests
    max_concurrent = 3
    semaphore = asyncio.Semaphore(max_concurrent)

    async def rate_limited_request(
        client: AsyncUltraApiClient, mint: str, delay: float
    ):
        async with semaphore:  # Acquire semaphore
            print(f"🔄 Checking {mint[:8]}...")
            await asyncio.sleep(delay)  # Simulate some processing
            result = await client.shield(mints=[mint])
            print(f"✓ Completed {mint[:8]}...")
            return result

    client = AsyncUltraApiClient()

    mints = [
        "So11111111111111111111111111111111111111112",
        "EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v",
        "Es9vMFrzaCERmJfrF4H2FYD4KCoNkY11McCe8BenwNYB",
        "7vfCXTUXx5WJV5JADk17DUJ4ksgau7utNKj4b963voxs",
        "DezXAZ8z7PnrnRJjz3wXBoRgixCa6xjnB7YaB1pPB263",
    ]

    try:
        msg = (
            f"Processing {len(mints)} requests with max {max_concurrent} concurrent..."
        )
        print(f"{msg}\n")

        tasks = [rate_limited_request(client, mint, 0.5) for mint in mints]

        start = time.time()
        await asyncio.gather(*tasks)
        elapsed = time.time() - start

        print(f"\nCompleted in {elapsed:.2f} seconds")
        print(f"(Would take {len(mints) * 0.5:.2f} seconds sequentially)")

    finally:
        await client.close()


async def main():
    """Run all examples"""

    print("=== Jupiter SDK Concurrent Operations Demo ===\n")

    # Example 1: Concurrent token safety checks
    await concurrent_token_check()

    # Example 2: Batch balance checks
    # await batch_balance_check()

    # Example 3: Rate-limited requests
    await rate_limited_requests()


if __name__ == "__main__":
    asyncio.run(main())
