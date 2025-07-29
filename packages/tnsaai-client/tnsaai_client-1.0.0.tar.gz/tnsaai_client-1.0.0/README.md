# TNSAAI Python Client

A powerful, OpenAI-compatible Python SDK for TNSA NGen3 Pro and Lite Models.

## Installation

```bash
pip install tnsaai
```

## Quick Start

```python
from tnsaai import TNSA

# Initialize the client
client = TNSA(api_key="your-api-key", base_url="https://api.tnsaai.com")

# Create a chat completion
response = client.chat.create(
    model="NGen3.9-Pro",
    messages=[{"role": "user", "content": "Hello!"}]
)

print(response.choices[0].message.content)
```

## Streaming

```python
stream = client.chat.create(
    model="NGen3.9-Lite",
    messages=[{"role": "user", "content": "Tell me a story"}],
    stream=True
)

for chunk in stream:
    if chunk.content:
        print(chunk.content, end="")
```

## Async Usage

```python
import asyncio
from tnsaai import AsyncTNSA

async def main():
    async with AsyncTNSA(api_key="your-api-key") as client:
        response = await client.chat.create(
            model="NGen3.9-Pro",
            messages=[{"role": "user", "content": "Hello!"}]
        )
        print(response.choices[0].message.content)

asyncio.run(main())
```

## Available Models

- **NGen3.9-Pro** - High-performance model for complex tasks
- **NGen3.9-Lite** - Fast, efficient model for general use
- **Farmvaidya-Bot** - Agricultural domain-specific model

## Configuration

Set your API key as an environment variable:

```bash
export TNSA_API_KEY="your-api-key"
export TNSA_BASE_URL="https://api.tnsaai.com"
```

Or pass it directly:

```python
client = TNSA(
    api_key="your-api-key",
    base_url="https://api.tnsaai.com"
)
```
