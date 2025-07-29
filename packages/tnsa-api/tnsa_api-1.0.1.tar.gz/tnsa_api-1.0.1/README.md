# TNSA API Python Client

A powerful, OpenAI-compatible Python SDK for TNSA NGen3 Pro and Lite Models.

## Features

- 🚀 **OpenAI-Compatible API** - Familiar interface for easy migration
- ⚡ **Async & Sync Support** - Both synchronous and asynchronous clients
- 🌊 **Streaming Responses** - Real-time token streaming for interactive applications
- 🔧 **Comprehensive Error Handling** - Robust error handling with retry logic
- 📊 **Usage Tracking** - Built-in token counting and cost estimation
- 💬 **Conversation Management** - Automatic chat history and context management
- 🔒 **Secure Authentication** - API key management with environment variable support
- 📝 **Type Safety** - Full type hints for better IDE support
- 🎯 **Framework Integration** - Works seamlessly with FastAPI, Django, and more

## Installation

```bash
pip install tnsa-api
```

## Quick Start

```python
from tnsa_api_v2 import TNSA

# Initialize the client
client = TNSA(api_key="your-api-key")

# List available models
models = client.models.list()
print("Available models:", [model.id for model in models])

# Create a chat completion
response = client.chat.completions.create(
    model="NGen3.9-Pro",
    messages=[
        {"role": "user", "content": "Hello, how are you?"}
    ]
)

print(response.choices[0].message.content)
```

## Streaming Example

```python
# Streaming responses
stream = client.chat.completions.create(
    model="NGen3.9-Lite",
    messages=[{"role": "user", "content": "Tell me a story"}],
    stream=True
)

for chunk in stream:
    if chunk.choices[0].delta.content:
        print(chunk.choices[0].delta.content, end="")
```

## Async Usage

```python
import asyncio
from tnsa_api_v2 import AsyncTNSA

async def main():
    client = AsyncTNSA(api_key="your-api-key")
    
    response = await client.chat.completions.acreate(
        model="NGen3.9-Pro",
        messages=[{"role": "user", "content": "Hello!"}]
    )
    
    print(response.choices[0].message.content)

asyncio.run(main())
```

## Configuration

The client can be configured using environment variables, configuration files, or direct parameters:

### Environment Variables

```bash
export TNSA_API_KEY="your-api-key"
export TNSA_BASE_URL="https://api.tnsaai.com"
export TNSA_TIMEOUT=30.0
```

### Configuration File (config.yaml)

```yaml
api_key: "your-api-key"
base_url: "https://api.tnsaai.com"
timeout: 30.0
max_retries: 3
default_model: "NGen3.9-Pro"
```

### Direct Parameters

```python
client = TNSA(
    api_key="your-api-key",
    base_url="https://api.tnsaai.com",
    timeout=30.0,
    max_retries=3
)
```

## Available Models

- **NGen3.9-Pro** - High-performance model for complex tasks
- **NGen3.9-Lite** - Fast, efficient model for general use
- **NGen3-7B-0625** - Specialized model variant
- **Farmvaidya-Bot** - Agricultural domain-specific model

## Error Handling

```python
from tnsa_api_v2 import TNSAError, RateLimitError, AuthenticationError

try:
    response = client.chat.completions.create(
        model="NGen3.9-Pro",
        messages=[{"role": "user", "content": "Hello!"}]
    )
except AuthenticationError:
    print("Invalid API key")
except RateLimitError:
    print("Rate limit exceeded")
except TNSAError as e:
    print(f"API error: {e}")
```

## Documentation

For detailed documentation, examples, and API reference, visit: [https://docs.tnsaai.com](https://docs.tnsaai.com)

## Support

- 📧 Email: info@tnsaai.com
- 🐛 Issues: [GitHub Issues](https://github.com/tnsaai/tnsa-api-python/issues)
- 📖 Documentation: [https://docs.tnsaai.com](https://docs.tnsaai.com)

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.