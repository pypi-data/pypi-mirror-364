# LLM Wrapper

A comprehensive Python wrapper for Azure OpenAI with built-in PostgreSQL integration and usage tracking. Provides detailed analytics for LLM usage with support for both text and JSON response formats, including multimodal capabilities (text + images).

## Features

- 🚀 **Easy Integration**: Simple API for interacting with Azure OpenAI services
- 📊 **Usage Tracking**: Comprehensive logging and analytics for all LLM requests
- 💾 **PostgreSQL Integration**: Built-in PostgreSQL database support with automatic table creation
- ⚡ **High Performance**: Optimized for concurrent requests and high throughput
- 🔒 **Secure**: Built-in security features and API key management
- 📈 **Analytics**: Detailed usage statistics and reporting
- 🎯 **Response Types**: Support for both text and JSON response formats
- 🖼️ **Multimodal Support**: Handle text, images, and mixed content in conversations
- 🗨️ **Conversation Support**: Multi-turn conversation capabilities with role-based messaging
- 🐳 **Production Ready**: Robust error handling and logging

## Installation

### Basic Installation

```bash
pip install hibiz-llm-wrapper
```

## Quick Start

### Basic Usage

```python
from hibiz_llm_wrapper import LLMWrapper

# Initialize the wrapper (database connection is automatic)
wrapper = LLMWrapper(
    service_url="https://your-azure-openai-instance.openai.azure.com",
    api_key="your-azure-openai-api-key",
    deployment_name="your-deployment-name",
    api_version="2023-05-15",
    default_model='gpt-4'
)

# Send a text request using prompt_payload
prompt_payload = [
    {"role": "user", "content": "What are the benefits of renewable energy?"}
]

response = wrapper.send_request(
    prompt_payload=prompt_payload,
    customer_id=1,
    organization_id=1,
    response_type="text",
    temperature=0.7,
    max_tokens=2000
)

print(f"Response: {response['processed_output']}")
print(f"Tokens used: {response['total_tokens']}")
print(f"Response type: {response['response_type']}")

# Send a JSON request
json_prompt = [
    {"role": "user", "content": "Create a JSON object with information about Python programming including name, creator, and year_created."}
]

json_response = wrapper.send_request(
    prompt_payload=json_prompt,
    customer_id=1,
    organization_id=1,
    response_type="json"
)

print(f"JSON Response: {json_response['processed_output']}")
print(f"Creator: {json_response['processed_output'].get('creator', 'N/A')}")

# Get usage statistics
stats = wrapper.get_usage_stats()
print(f"Total requests: {stats['total_requests']}")
print(f"Total tokens: {stats['total_tokens']}")

# Clean up
wrapper.close()
```

### Multimodal Usage (Text + Images)

```python
# Send request with image
multimodal_prompt = [
    {
        "role": "user", 
        "content": [
            {"type": "text", "text": "What do you see in this image? Describe it in detail."},
            {"type": "image_url", "image_url": {"url": "data:image/jpeg;base64,/9j/4AAQSkZJRgABAQAAAQ..."}}
        ]
    }
]

response = wrapper.send_request(
    prompt_payload=multimodal_prompt,
    customer_id=1,
    organization_id=1,
    response_type="text"
)

print(f"Image Analysis: {response['processed_output']}")

# Multiple images with text
multi_image_prompt = [
    {
        "role": "user", 
        "content": [
            {"type": "text", "text": "Compare these two images and tell me the differences:"},
            {"type": "image_url", "image_url": {"url": "https://example.com/image1.jpg"}},
            {"type": "image_url", "image_url": {"url": "https://example.com/image2.jpg"}},
            {"type": "text", "text": "Please provide the comparison in JSON format."}
        ]
    }
]

comparison = wrapper.send_request(
    prompt_payload=multi_image_prompt,
    customer_id=1,
    organization_id=1,
    response_type="json"
)
```

### Multi-turn Conversations

```python
# Conversation with context
conversation_prompt = [
    {"role": "user", "content": "Hello, I need help with Python programming."},
    {"role": "assistant", "content": "Hello! I'd be happy to help you with Python programming. What specific topic or problem would you like assistance with?"},
    {"role": "user", "content": "Can you explain list comprehensions with examples?"},
    {"role": "assistant", "content": "Certainly! List comprehensions are a concise way to create lists in Python..."},
    {"role": "user", "content": "Now show me how to use list comprehensions with images in the context."},
    {
        "role": "user", 
        "content": [
            {"type": "text", "text": "Here's a code screenshot I'm working with:"},
            {"type": "image_url", "image_url": {"url": "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAA..."}}
        ]
    }
]

response = wrapper.send_request(
    prompt_payload=conversation_prompt,
    customer_id=1,
    organization_id=1,
    response_type="text"
)
```

## Response Types

### Text Response (Default)

```python
prompt_payload = [{"role": "user", "content": "Explain artificial intelligence"}]

response = wrapper.send_request(
    prompt_payload=prompt_payload,
    customer_id=1,
    organization_id=1,
    response_type="text"
)

# Response structure:
{
    "output_text": "raw response from API",
    "processed_output": "same as output_text for text responses",
    "response_type": "text",
    "input_tokens": 10,
    "output_tokens": 150,
    "total_tokens": 160,
    "response_time_ms": 1200,
    "model": "gpt-4",
    "full_response": {...},
    "original_prompt": [{"role": "user", "content": "Explain artificial intelligence"}]
}
```

### JSON Response

```python
prompt_payload = [{"role": "user", "content": "Create a JSON object with user information including name, age, and skills array"}]

response = wrapper.send_request(
    prompt_payload=prompt_payload,
    customer_id=1,
    organization_id=1,
    response_type="json"
)

# Response structure:
{
    "output_text": '{"name": "John", "age": 30, "skills": ["Python", "AI"]}',
    "processed_output": {"name": "John", "age": 30, "skills": ["Python", "AI"]},
    "response_type": "json",
    "input_tokens": 15,
    "output_tokens": 25,
    "total_tokens": 40,
    "response_time_ms": 1500,
    "model": "gpt-4",
    "full_response": {...},
    "original_prompt": [{"role": "user", "content": "Create a JSON object..."}]
}
```

## Prompt Payload Formats

### Simple Text Message

```python
prompt_payload = [
    {"role": "user", "content": "Your question here"}
]
```

### System Message with User Input

```python
prompt_payload = [
    {"role": "system", "content": "You are a helpful assistant specialized in data analysis."},
    {"role": "user", "content": "Analyze this sales data for trends."}
]
```

### Multimodal Content (Text + Image)

```python
prompt_payload = [
    {
        "role": "user", 
        "content": [
            {"type": "text", "text": "What's in this image?"},
            {"type": "image_url", "image_url": {"url": "data:image/jpeg;base64,..."}}
        ]
    }
]
```

### Multi-turn Conversation

```python
prompt_payload = [
    {"role": "user", "content": "What is machine learning?"},
    {"role": "assistant", "content": "Machine learning is a subset of artificial intelligence..."},
    {"role": "user", "content": "Can you give me a practical example?"}
]
```

### Complex Multimodal Conversation

```python
prompt_payload = [
    {"role": "system", "content": "You are an expert image analyst and coder."},
    {
        "role": "user", 
        "content": [
            {"type": "text", "text": "I have two images showing different UI designs. Please analyze them and suggest improvements:"},
            {"type": "image_url", "image_url": {"url": "https://example.com/ui1.png"}},
            {"type": "image_url", "image_url": {"url": "https://example.com/ui2.png"}},
            {"type": "text", "text": "Focus on usability and accessibility aspects."}
        ]
    },
    {"role": "assistant", "content": "I can see both UI designs. Here are my observations..."},
    {
        "role": "user", 
        "content": [
            {"type": "text", "text": "Great analysis! Now here's the updated design based on your feedback:"},
            {"type": "image_url", "image_url": {"url": "https://example.com/ui3.png"}},
            {"type": "text", "text": "What do you think of the improvements?"}
        ]
    }
]
```

## Database Schema

The wrapper automatically creates the following PostgreSQL table:

```sql
CREATE TABLE token_usage_log (
    id SERIAL PRIMARY KEY,
    customer_id INTEGER NOT NULL,
    organization_id INTEGER NOT NULL,
    model_name VARCHAR(255) NOT NULL,
    request_params JSON,
    response_params JSON,
    input_tokens INTEGER NOT NULL,
    output_tokens INTEGER NOT NULL,
    total_tokens INTEGER NOT NULL,
    request_timestamp TIMESTAMP DEFAULT NOW(),
    response_time_ms INTEGER NOT NULL,
    status VARCHAR(50) DEFAULT 'success'
);
```

## Usage Analytics

```python
# Get overall statistics
stats = wrapper.get_usage_stats()

# Get customer-specific statistics
customer_stats = wrapper.get_usage_stats(customer_id=1)

# Get organization-specific statistics
org_stats = wrapper.get_usage_stats(organization_id=1)

# Get statistics for a specific time period
period_stats = wrapper.get_usage_stats(
    start_date="2024-01-01T00:00:00",
    end_date="2024-01-31T23:59:59"
)

# Example stats output:
{
    "total_requests": 150,
    "total_tokens": 45000,
    "models": [
        {
            "model_name": "gpt-4",
            "requests": 100,
            "input_tokens": 15000,
            "output_tokens": 20000,
            "total_tokens": 35000,
            "avg_response_time_ms": 1200
        },
        {
            "model_name": "gpt-3.5-turbo",
            "requests": 50,
            "input_tokens": 5000,
            "output_tokens": 5000,
            "total_tokens": 10000,
            "avg_response_time_ms": 800
        }
    ]
}
```

## Configuration Options

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `service_url` | str | Required | Azure OpenAI service endpoint URL |
| `api_key` | str | Required | Azure OpenAI API key |
| `deployment_name` | str | Required | Azure OpenAI deployment name |
| `api_version` | str | Required | Azure OpenAI API version |
| `default_model` | str | 'gpt-4' | Default model identifier |
| `timeout` | int | 30 | Request timeout in seconds |

## API Reference

### Core Methods

#### `send_request(prompt_payload, customer_id, organization_id, response_type="text", **kwargs)`

Send a request to the Azure OpenAI service using the new prompt payload format.

**Parameters:**
- `prompt_payload` (List[Dict[str, Any]]): Array of message objects with role and content
- `customer_id` (int): Customer identifier
- `organization_id` (int): Organization identifier
- `response_type` (str): Response format - "text" or "json"
- `model` (str, optional): Model to use for this request
- `temperature` (float, optional): Sampling temperature (0.0-1.0)
- `max_tokens` (int, optional): Maximum tokens in response

**Message Format:**
```python
# Text message
{"role": "user|assistant|system", "content": "text content"}

# Multimodal message
{
    "role": "user|assistant|system", 
    "content": [
        {"type": "text", "text": "text content"},
        {"type": "image_url", "image_url": {"url": "image_url_or_base64"}}
    ]
}
```

**Returns:**
- `dict`: Response containing output text, processed output, token counts, metadata, and original prompt

#### `get_usage_stats(**filters)`

Get usage statistics with optional filtering.

**Parameters:**
- `customer_id` (int, optional): Filter by customer
- `organization_id` (int, optional): Filter by organization
- `start_date` (str, optional): Start date in ISO format
- `end_date` (str, optional): End date in ISO format

**Returns:**
- `dict`: Usage statistics including request counts, token usage, and performance metrics

#### `close()`

Close database connections and clean up resources.

## Token Calculation

The wrapper intelligently handles token calculation for different content types:

- **Text content**: Direct token counting using the specified model's tokenizer
- **Image content**: Uses placeholder tokens for estimation (actual tokens may vary based on image size and complexity)
- **Mixed content**: Combines text and image token estimates

## Error Handling

The wrapper provides comprehensive error handling:

```python
from hibiz_llm_wrapper.exceptions import APIError, DatabaseError

try:
    response = wrapper.send_request(
        prompt_payload=[{"role": "user", "content": "Hello"}],
        customer_id=1,
        organization_id=1
    )
except APIError as e:
    print(f"API request failed: {e}")
except DatabaseError as e:
    print(f"Database operation failed: {e}")
```

## Requirements

- Python 3.8+
- Pillow (for image processing)
- tiktoken (for token counting)

## License

This project is licensed under the MIT License.

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## Acknowledgments

- Thanks to all contributors who have helped shape this project
- Built with love for the AI/ML community