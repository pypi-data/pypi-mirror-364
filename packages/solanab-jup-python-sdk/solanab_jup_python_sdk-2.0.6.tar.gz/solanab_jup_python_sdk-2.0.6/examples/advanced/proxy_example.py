#!/usr/bin/env python3
"""
Advanced example: Using proxy with Jupiter SDK
"""

import asyncio

from jup_python_sdk.clients.ultra_api_client import AsyncUltraApiClient


async def example_with_proxy():
    """Example using SOCKS5 proxy"""

    # Configure SOCKS5 proxy (e.g., for Tor)
    # Note: You need to have a SOCKS5 proxy running
    proxies = {
        "https": "socks5://127.0.0.1:9050"  # Default Tor proxy
    }

    print("Creating client with SOCKS5 proxy...")
    client = AsyncUltraApiClient(
        client_kwargs={
            "proxies": proxies,
            "impersonate": "chrome110",  # Simulate Chrome browser
            "timeout": 30,  # 30 seconds timeout
        }
    )

    try:
        # Test the connection
        print("\nFetching shield information through proxy...")

        wsol_mint = "So11111111111111111111111111111111111111112"
        shield_response = await client.shield(mints=[wsol_mint])

        print("✓ Successfully connected through proxy!")
        print(f"Response: {shield_response}")

    except Exception as e:
        print(f"✗ Error occurred: {e}")
        print("Make sure your proxy is running and accessible")

    finally:
        await client.close()


async def example_with_custom_dns():
    """Example using custom DNS resolution"""

    print("Creating client with custom DNS resolution...")

    # Force specific DNS resolution
    # This is useful for:
    # - Testing against specific servers
    # - Bypassing DNS cache
    # - Using internal/private endpoints
    client = AsyncUltraApiClient(
        client_kwargs={
            "resolve": [
                # Format: "domain:port:ip"
                # "api.jup.ag:443:1.2.3.4",  # Example - replace with actual IP
            ],
            "dns_servers": ["1.1.1.1", "1.0.0.1"],  # Use Cloudflare DNS
        }
    )

    try:
        print("\nTesting connection with custom DNS...")

        # Get public key to test basic functionality
        public_key = await client.get_public_key()
        print(f"✓ Public key retrieved: {public_key}")

    except Exception as e:
        print(f"✗ Error occurred: {e}")

    finally:
        await client.close()


async def example_with_http_proxy():
    """Example using HTTP/HTTPS proxy"""

    # Configure HTTP proxy with authentication
    proxies = {
        "http": "http://username:password@proxy.example.com:8080",
        "https": "http://username:password@proxy.example.com:8080",
    }

    print("Creating client with HTTP proxy...")
    client = AsyncUltraApiClient(
        client_kwargs={
            "proxies": proxies,
            "verify": True,  # Verify SSL certificates
        }
    )

    try:
        print("\nTesting connection through HTTP proxy...")

        # Test with a simple request
        usdc_mint = "EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v"
        await client.shield(mints=[usdc_mint])

        print("✓ Successfully connected through HTTP proxy!")

    except Exception as e:
        print(f"✗ Error occurred: {e}")
        print("Check your proxy settings and credentials")

    finally:
        await client.close()


async def main():
    """Run examples"""

    print("=== Jupiter SDK Advanced Features Demo ===\n")

    # Example 1: Custom DNS
    await example_with_custom_dns()

    print("\n" + "=" * 50 + "\n")

    # Example 2: Proxy support
    # Uncomment to test with a real proxy
    # await example_with_proxy()
    # await example_with_http_proxy()

    print("\nNote: Proxy examples are commented out.")
    print("To test them, ensure you have a proxy running and uncomment the code.")


if __name__ == "__main__":
    asyncio.run(main())
