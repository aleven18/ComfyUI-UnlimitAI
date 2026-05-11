#!/bin/bash
# 停止所有服务

echo "================================================"
echo "停止 ComfyUI-UnlimitAI 服务"
echo "================================================"
echo ""

# 停止 ComfyUI
echo "停止 ComfyUI 后端..."
pkill -f "python.*main.py.*8188" && echo "   ✅ ComfyUI 已停止" || echo "   ⚠️  ComfyUI 未运行"

# 停止前端
echo "停止前端服务器..."
pkill -f "vite.*3000" && echo "   ✅ 前端已停止" || echo "   ⚠️  前端未运行"

echo ""
echo "✅ 所有服务已停止"
