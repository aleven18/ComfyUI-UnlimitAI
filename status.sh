#!/bin/bash
# 查看服务状态

echo "================================================"
echo "ComfyUI-UnlimitAI 服务状态"
echo "================================================"
echo ""

# 检查 ComfyUI
echo "【ComfyUI 后端】"
if pgrep -f "python.*main.py.*8188" > /dev/null; then
    PID=$(pgrep -f "python.*main.py.*8188")
    echo "   状态: ✅ 运行中"
    echo "   PID: $PID"
    echo "   地址: http://127.0.0.1:8188"
else
    echo "   状态: ❌ 未运行"
fi

echo ""

# 检查前端
echo "【前端服务器】"
if pgrep -f "vite.*3000" > /dev/null; then
    PID=$(pgrep -f "vite.*3000")
    echo "   状态: ✅ 运行中"
    echo "   PID: $PID"
    echo "   地址: http://localhost:3000"
else
    echo "   状态: ❌ 未运行"
fi

echo ""
echo "================================================"
