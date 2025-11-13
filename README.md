# Chotbot

A Python-based chatbot with RAG (Retrieval-Augmented Generation) and MCP (Model Context Protocol) support.

## Features

- **LLM Integration**: Supports OpenAI API (API key from environment variables)
- **RAG**: Retrieval-Augmented Generation for knowledge-enhanced responses
- **MCP**: Model Context Protocol for context-aware conversations
- **Console Interface**: Interactive console-based usage

## Installation

```bash
# Clone the repository
git clone <repository-url>
cd chotbot

# Install dependencies using uv
uv install
```

## Configuration

1. Create a `.env` file in the project root:

```bash
cp .env.example .env
```

2. Edit the `.env` file to add your OpenAI API key:

```env
OPENAI_API_KEY=your-openai-api-key
```

## Usage

```bash
# Run the chatbot
uv run chotbot
```

Or:

```bash
python -m src
```

### Commands

- **exit**: Quit the chatbot
- **clear**: Clear the current context
- **rag on/off**: Toggle RAG (Retrieval-Augmented Generation)
- **Type any question**: Chat with the bot

## Project Structure

```
chotbot/
├── src/
│   └── chotbot/
│       ├── core/          # Core chatbot logic
│       ├── rag/           # RAG (Retrieval-Augmented Generation)
│       ├── mcp/           # MCP (Model Context Protocol)
│       └── utils/         # Utility functions and configuration
├── .env.example           # Example configuration file
├── pyproject.toml         # Project configuration
└── README.md              # This file
```

## Development

### Adding Documents to RAG

You can add custom documents to the RAG system by modifying the `sample_docs` list in `src/chotbot/cli.py`, or by using the `add_documents()` method:

```python
from chotbot.core.chatbot import Chatbot

chatbot = Chatbot()
chatbot.add_documents([
    "Your document text here...",
    "Another document...",
])
```

### Customizing Configuration

Edit the configuration in `src/chotbot/utils/config.py` or override environment variables in `.env`.

## License

MIT
