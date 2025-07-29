# generativellm

`generativellm` is a simple wrapper around the Gemini REST API using pure HTTP requests. It lets you create chat sessions and generate responses.

## Installation

```bash
pip install generativellm
```

## Usage

```python
from generativellm import AIChat

chatbot = AIChat(token="your-gemini-api-key", model="gemini-pro")

conversation = [
    "Hello!",
    "Hi there! How can I help?",
    "Can you summarize general relativity?",
]

response = chatbot.get_response(conversation)
print(response)
```
