# Devion Python SDK

Python SDK for the Devion blockchain RPC proxy platform.

## Installation

```bash
pip install devion-sdk
```

## Quick Start

```python
from devion_sdk import DevionSDK

# Initialize the SDK
devion = DevionSDK(api_key="your-api-key-here", network="ethereum")

# Get account balance
balance = devion.get_balance("0x742d35Cc6635C0532925a3b8D007EbA3fFC2C5DD", formatted=True)
print(f"Balance: {balance} ETH")

# Get current block number
block_number = devion.get_block_number()
print(f"Current block: {block_number}")
```

## Features

- Multi-chain support (Ethereum, Polygon, BSC, Arbitrum, etc.)
- Type safety with full type hints
- Comprehensive error handling
- Rate limiting and retry logic
- Context manager support

## Documentation

For full documentation, visit [docs.devion.dev](https://docs.devion.dev)
