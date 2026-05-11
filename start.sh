#!/bin/bash
# ComfyUI-UnlimitAI 一键启动脚本
# 同时启动 ComfyUI 后端和前端

set -e

# 配置
COMFYUI_DIR="/Volumes/工作/comfyui"
FRONTEND_DIR="/Users/aleven/.config/opencode/ComfyUI-UnlimitAI/web"
LOG_DIR="/tmp/comfyui-unlimitai-logs"

# 创建日志目录
mkdir -p "$LOG_DIR"

echo "================================================"
echo "ComfyUI-UnlimitAI 启动脚本"
echo "================================================"
echo ""

# 检查 ComfyUI 是否已安装
if [ ! -f "$COMFYUI_DIR/main.py" ]; then
    echo "❌ 错误: ComfyUI 未找到"
    echo "请先运行安装脚本"
    exit 1
fi

# 检查前端是否已构建
if [ ! -d "$FRONTEND_DIR/dist" ]; then
    echo "⚠️  前端未构建，正在构建..."
    cd "$FRONTEND_DIR"
    npm run build
fi

echo "✅ 检查通过"
echo ""

# 启动 ComfyUI 后端
echo "【1/2】启动 ComfyUI 后端..."
cd "$COMFYUI_DIR"
source venv/bin/activate
nohup python main.py --listen 127.0.0.1 --port 8188 > "$LOG_DIR/comfyui.log" 2>&1 &
COMFYUI_PID=$!
echo "   PID: $COMFYUI_PID"
echo "   日志: $LOG_DIR/comfyui.log"

# 等待 ComfyUI 启动
sleep 3

# 检查 ComfyUI 是否成功启动
if ps -p $COMFYUI_PID > /dev/null; then
    echo "   ✅ ComfyUI 后端启动成功"
else
    echo "   ❌ ComfyUI 后端启动失败"
    cat "$LOG_DIR/comfyui.log"
    exit 1
fi

echo ""

# 启动前端开发服务器
echo "【2/2】启动前端开发服务器..."
cd "$FRONTEND_DIR"
nohup npm run dev > "$LOG_DIR/frontend.log" 2>&1 &
FRONTEND_PID=$!
echo "   PID: $FRONTEND_PID"
echo "   日志: $LOG_DIR/frontend.log"

# 等待前端启动
sleep 3

# 检查前端是否成功启动
if ps -p $FRONTEND_PID > /dev/null; then
    echo "   ✅ 前端服务器启动成功"
else
    echo "   ❌ 前端服务器启动失败"
    cat "$LOG_DIR/frontend.log"
    exit 1
fi

echo ""
echo "================================================"
echo "✅ 启动完成！"
echo "================================================"
echo ""
echo "🌐 访问地址："
echo "   前端界面: http://localhost:3000"
echo "   ComfyUI: http://127.0.0.1:8188"
echo ""
echo "📋 管理命令："
echo "   查看日志: tail -f $LOG_DIR/*.log"
echo "   停止服务: ./stop.sh"
echo "   查看状态: ./status.sh"
echo ""
echo "💡 提示:"
echo "   - 首次使用需要配置 UnlimitAI API Key"
echo "   - 前端会自动代理到 ComfyUI 后端"
echo ""
