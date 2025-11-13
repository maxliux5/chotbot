# Chotbot

A Python-based chatbot with RAG (Retrieval-Augmented Generation) and MCP (Model Context Protocol) support.

## Features

- **LLM Integration**: Supports OpenAI API (API key from environment variables)
- **RAG**: Retrieval-Augmented Generation for knowledge-enhanced responses
- **MCP**: Model Context Protocol for context-aware conversations
- **Console Interface**: Interactive console-based usage
- **自动文档加载**: 自动加载 `doc/` 目录的文档并跟踪更新

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
python run_chatbot.py
```

### 自动文档加载功能

Chatbot 会**自动加载项目根目录下的 `doc/` 目录**中的所有文档（支持 `.md`, `.txt`, `.rst` 等格式）。

#### 文档跟踪机制
- 系统会生成 `.rag_loaded.json` 文件来跟踪已加载的文档
- 使用文件的 MD5 哈希值检测文档是否更新
- 每次启动时自动加载新文档或更新过的文档

#### 添加自定义文档
1. 将文档文件（支持 `.md`, `.txt`, `.rst`）放入 `doc/` 目录
2. 重新启动 Chatbot，系统会自动加载新文档
3. 可以嵌套目录组织文档，系统会自动遍历所有子目录

#### 手动管理
```bash
# 查看已加载的文档记录
cat .rag_loaded.json

# 清除所有记录（下次启动会重新加载所有文档）
rm .rag_loaded.json
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
├── doc/                   # Documentation directory (auto-loaded)
├── .env.example           # Example configuration file
├── run_chatbot.py         # Startup script
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
