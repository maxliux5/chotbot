# Chotbot Web 版部署指南

## 功能说明

- 网页版聊天界面，支持流式回答
- 实时显示机器人回复，无需等待完整响应
- 支持上下文对话
- 支持所有原有的聊天机器人功能

## 快速启动

### 方式一：使用启动脚本（推荐）

```bash
chmod +x start.sh
./start.sh
```

脚本会自动启动：
- 后端服务：http://localhost:5001
- 前端服务：http://localhost:3000

### 方式二：手动启动

#### 1. 启动后端服务

```bash
cd /path/to/chotbot
python -m uvicorn backend.main:app --host 0.0.0.0 --port 5001
```

#### 2. 启动前端服务（新开一个终端）

```bash
cd /path/to/chotbot/frontend
npm run dev
```

#### 3. 访问页面

打开浏览器访问：http://localhost:3000

## 项目结构

```
chotbot/
├── backend/
│   └── main.py                # FastAPI 后端服务
├── frontend/
│   ├── public/               # 静态资源
│   ├── src/
│   │   ├── App.js            # 主应用组件
│   │   ├── App.css           # 样式
│   │   ├── index.js          # 入口文件
│   │   └── index.css         # 全局样式
│   ├── package.json          # 前端依赖
│   └── vite.config.js        # Vite 配置
└── start.sh                  # 一键启动脚本
```

## 技术栈

- **前端**：React 18 + Vite + JavaScript
- **后端**：FastAPI + Python
- **通信**：REST API + 流式响应

## 开发说明

### 前端开发

前端代码位于 `frontend/` 目录下，使用 Vite 构建工具。

```bash
# 安装依赖
npm install

# 开发模式
npm run dev

# 构建生产版本
npm run build

# 预览生产版本
npm run preview
```

### 后端开发

后端代码位于 `backend/main.py`，提供以下 API 接口：

- `POST /api/chat` - 普通聊天接口
- `POST /api/chat/stream` - 流式聊天接口

## 注意事项

1. 确保已正确配置 `.env` 文件，包含 OpenAI API 密钥
2. 前端默认会代理 API 请求到 `http://localhost:5001`，如果后端端口不同，需要修改 `vite.config.js`
3. 流式响应需要浏览器支持 Server-Sent Events (SSE)
4. 确保防火墙允许访问 3000 和 5001 端口
