# Chotbot 架构概览

## 项目概述

Chotbot 是一个基于 Python 的智能聊天机器人，集成了 RAG（检索增强生成）和 MCP（模型上下文协议）技术。项目采用模块化架构设计，支持控制台和 Web 界面两种交互方式。

### 核心特性
- **LLM 集成**: 支持 OpenAI API，通过环境变量配置 API 密钥
- **RAG 系统**: 自动文档加载和向量检索，支持 `doc/` 目录文档自动索引
- **MCP 协议**: 上下文感知的对话管理
- **意图识别**: 基于配置文件的意图识别和槽位提取
- **工具集成**: 天气查询、基金信息、深度搜索等工具
- **双界面支持**: 控制台交互和 Web 界面（React + FastAPI）

## 架构设计

### 核心模块

```
src/chotbot/
├── core/           # 核心聊天逻辑
│   ├── chatbot.py  # 主聊天机器人类，集成所有模块
│   ├── llm_client.py # LLM 客户端封装
│   └── react_agent.py # ReAct 代理实现
├── rag/            # RAG 检索增强生成
│   ├── rag_manager.py # RAG 管理器
│   ├── vector_store.py # 向量存储
│   ├── retriever.py  # 文档检索器
│   └── generator.py  # 响应生成器
├── mcp/            # 模型上下文协议
│   ├── processor.py # MCP 处理器
│   ├── context_manager.py # 上下文管理
│   └── tools/      # 工具集合
│       ├── tool_manager.py # 工具管理器
│       ├── weather.py    # 天气查询
│       ├── fund.py      # 基金信息
│       └── search.py    # 搜索工具
├── intent/         # 意图识别
│   └── intent_recognizer.py # 意图识别器
└── utils/          # 工具函数
    ├── config.py   # 配置管理
    └── rag_loader.py # 文档加载器
```

### 前端架构

```
frontend/
├── src/
│   ├── App.jsx     # 主应用组件
│   ├── index.jsx   # 入口文件
│   └── assets/     # 静态资源
├── public/         # 公共资源
└── package.json    # 前端依赖配置
```

### 后端服务

```
backend/
└── main.py         # FastAPI 服务，提供 REST API
```

## 开发命令

### 环境设置
```bash
# 安装依赖
uv install

# 创建环境配置
cp .env.example .env
# 编辑 .env 文件，添加 API 密钥
```

### 运行方式

#### 控制台版本
```bash
# 方式一：使用 uv
uv run chotbot

# 方式二：直接运行
python run_chatbot.py
```

#### Web 版本
```bash
# 一键启动（推荐）
chmod +x start.sh
./start.sh

# 手动启动后端
python -m uvicorn backend.main:app --host 0.0.0.0 --port 5001

# 手动启动前端
cd frontend
npm install
npm run dev
```

### 测试命令
```bash
# 运行测试文件
python test_chatbot.py
python test_intent.py
python test_pdf_load.py
```

## 代码规范

### Python 代码风格
- 遵循 PEP 8 规范
- 使用 4 个空格缩进
- 类名使用 PascalCase
- 函数和变量使用 snake_case
- 常量使用 UPPER_CASE

### 命名约定
- 模块名：`lowercase_with_underscores`
- 类名：`PascalCase`
- 函数名：`snake_case`
- 变量名：`snake_case`
- 常量：`UPPER_CASE`

### 代码组织
- 每个模块职责单一
- 函数长度控制在合理范围
- 添加必要的文档字符串
- 错误处理使用 try-except
- 日志记录使用标准 logging 模块

## 测试策略

### 测试框架
- 使用 Python 标准 unittest 或 pytest
- 测试文件以 `test_` 前缀命名
- 每个核心模块都有对应的测试文件

### 测试覆盖
- 单元测试：核心函数和类方法
- 集成测试：模块间交互
- 端到端测试：完整对话流程

### 测试执行
```bash
# 运行所有测试
python -m pytest test_*.py

# 运行特定测试
python test_chatbot.py
```

## 安全考虑

### API 密钥管理
- 所有 API 密钥通过环境变量配置
- `.env` 文件添加到 `.gitignore`
- 不在代码中硬编码敏感信息

### 输入验证
- 用户输入进行必要的验证和清理
- API 接口使用 Pydantic 模型验证
- 防止注入攻击

### 日志安全
- 日志中不记录敏感信息
- 错误信息不暴露内部实现细节
- 使用适当的日志级别

## 配置管理

### 环境变量
- `OPENAI_API_KEY`: OpenAI API 密钥
- `OPENAI_BASE_URL`: API 基础地址
- `MODEL_NAME`: 使用的模型名称
- `TEMPERATURE`: 生成温度参数

### RAG 配置
- `RAG_TOP_K`: 检索文档数量（默认 3）
- `RAG_CHUNK_SIZE`: 文档分块大小（默认 1000）
- `RAG_CHUNK_OVERLAP`: 分块重叠大小（默认 100）

### MCP 配置
- `MCP_MAX_CONTEXT_SIZE`: 最大上下文大小（默认 4096）
- `MCP_HISTORY_LIMIT`: 历史记录限制（默认 10）

## 部署指南

### 开发环境
- Python 3.11+
- Node.js 16+
- 推荐使用 uv 进行依赖管理

### 生产部署
1. 设置环境变量
2. 安装依赖：`uv install`
3. 构建前端：`cd frontend && npm run build`
4. 启动后端：`uvicorn backend.main:app --host 0.0.0.0 --port 5001`

### 容器化
- 使用 Docker 多阶段构建
- 前端和后端可以分别容器化
- 使用 docker-compose 管理多服务

## 故障排查

### 常见问题
1. **API 密钥错误**: 检查 `.env` 文件配置
2. **依赖缺失**: 运行 `uv install` 安装依赖
3. **端口冲突**: 检查 5001 和 3000 端口是否被占用
4. **文档加载失败**: 检查 `doc/` 目录权限

### 日志查看
```bash
# 后端日志
tail -f backend.log

# 前端日志
tail -f frontend/frontend.log
```

### 调试模式
- 设置环境变量 `DEBUG=true`
- 查看详细日志输出
- 使用调试工具进行代码调试

## 扩展开发

### 添加新工具
1. 在 `src/chotbot/mcp/tools/` 创建新工具类
2. 继承基础工具接口
3. 在 `tool_manager.py` 中注册工具
4. 更新意图配置文件

### 添加新意图
1. 编辑 `intent_config.json`
2. 添加意图名称、示例和槽位定义
3. 在 `chatbot.py` 中实现处理逻辑

### 自定义 RAG 文档
1. 将文档放入 `doc/` 目录
2. 支持 `.md`、`.txt`、`.rst` 格式
3. 系统自动检测并加载更新

## 性能优化

### RAG 优化
- 使用高效的向量数据库
- 优化文档分块策略
- 实现缓存机制

### 前端优化
- 使用生产构建
- 启用压缩和缓存
- 优化资源加载

### 后端优化
- 使用异步处理
- 实现连接池
- 添加限流保护