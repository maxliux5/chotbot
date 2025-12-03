#!/bin/bash
set -ex # 遇到错误立即退出,并打印执行的命令

PROJECT_ROOT="/Users/bytedance/agent/aitrade/chotbot"
BACKEND_PORT=5001
FRONTEND_PORT=3000

echo "======================================"
echo "Chotbot 终极启动脚本"
echo "======================================"

# --------------------------
# 1. 清理旧进程
# --------------------------
echo -e "\n1. 清理旧进程..."
for PORT in $BACKEND_PORT $FRONTEND_PORT; do
    PIDS=$(lsof -ti :$PORT 2>/dev/null || echo "")
    [ -n "$PIDS" ] && kill -9 $PIDS
done
echo "✅ 旧进程已清理"

# --------------------------
# 2. 启动后端
# --------------------------
echo -e "\n2. 启动后端服务..."
cd "$PROJECT_ROOT"
if [ ! -d ".venv" ]; then
    uv venv
fi
source ".venv/bin/activate"
# 使用虚拟环境的 Python 直接运行，而不是 uv run
.venv/bin/python -m uvicorn backend.main:app --host 0.0.0.0 --port $BACKEND_PORT --log-level info &
BACKEND_PID=$!

# 验证后端
for i in {1..10}; do
    if curl -s "http://localhost:$BACKEND_PORT"; then
        echo "✅ 后端运行在: http://localhost:$BACKEND_PORT"
        break
    fi
    sleep 1
done

# --------------------------
# 3. 启动前端
# --------------------------
echo -e "\n3. 启动前端服务..."
cd "$PROJECT_ROOT/frontend"
npm run dev -- --port $FRONTEND_PORT --host 0.0.0.0 &
FRONTEND_PID=$!

# 验证前端
for i in {1..15}; do
    if curl -s "http://localhost:$FRONTEND_PORT"; then
        echo "✅ 前端运行在: http://localhost:$FRONTEND_PORT"
        break
    fi
    sleep 1
done

# --------------------------
# 4. 完成提示
# --------------------------
echo -e "\n======================================"
echo "🎉 所有服务已启动！"
echo "--------------------------------------"
echo "请在浏览器中访问："
echo "👉 http://localhost:$FRONTEND_PORT"
echo "--------------------------------------"
echo "停止服务："
echo "kill -9 $BACKEND_PID $FRONTEND_PID"
echo "======================================"

# 保持脚本运行
wait
