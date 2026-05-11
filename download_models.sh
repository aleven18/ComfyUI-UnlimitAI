#!/bin/bash
# 模型下载脚本
# 下载常用的 Stable Diffusion 模型

set -e

MODELS_DIR="/Volumes/工作/comfyui/models/checkpoints"

echo "================================================"
echo "Stable Diffusion 模型下载工具"
echo "================================================"
echo ""

# 创建模型目录
mkdir -p "$MODELS_DIR"

echo "可用的模型："
echo ""
echo "【1】SDXL Base 1.0 (推荐)"
echo "    大小: ~6.5 GB"
echo "    质量: ⭐⭐⭐⭐⭐"
echo "    速度: ⚡⚡⚡"
echo ""
echo "【2】SD 1.5 (快速)"
echo "    大小: ~2.1 GB"
echo "    质量: ⭐⭐⭐⭐"
echo "    速度: ⚡⚡⚡⚡⚡"
echo ""
echo "【3】SD 2.1 (平衡)"
echo "    大小: ~2.1 GB"
echo "    质量: ⭐⭐⭐⭐"
echo "    速度: ⚡⚡⚡⚡"
echo ""
echo "【4】全部下载"
echo "    大小: ~11 GB"
echo ""
echo "【0】跳过"
echo ""

read -p "请选择 [0-4]: " choice

case $choice in
    1)
        echo ""
        echo "开始下载 SDXL Base 1.0..."
        echo "这可能需要 10-30 分钟，取决于网络速度"
        echo ""
        cd "$MODELS_DIR"
        wget -c https://huggingface.co/stabilityai/stable-diffusion-xl-base-1.0/resolve/main/sd_xl_base_1.0.safetensors \
            || curl -L -C - -o sd_xl_base_1.0.safetensors https://huggingface.co/stabilityai/stable-diffusion-xl-base-1.0/resolve/main/sd_xl_base_1.0.safetensors
        echo ""
        echo "✅ SDXL Base 1.0 下载完成"
        ;;
    2)
        echo ""
        echo "开始下载 SD 1.5..."
        echo "这可能需要 5-15 分钟"
        echo ""
        cd "$MODELS_DIR"
        wget -c https://huggingface.co/runwayml/stable-diffusion-v1-5/resolve/main/v1-5-pruned-emaonly.safetensors \
            || curl -L -C - -o v1-5-pruned-emaonly.safetensors https://huggingface.co/runwayml/stable-diffusion-v1-5/resolve/main/v1-5-pruned-emaonly.safetensors
        echo ""
        echo "✅ SD 1.5 下载完成"
        ;;
    3)
        echo ""
        echo "开始下载 SD 2.1..."
        echo "这可能需要 5-15 分钟"
        echo ""
        cd "$MODELS_DIR"
        wget -c https://huggingface.co/stabilityai/stable-diffusion-2-1-base/resolve/main/v2-1_512-ema-pruned.safetensors \
            || curl -L -C - -o v2-1_512-ema-pruned.safetensors https://huggingface.co/stabilityai/stable-diffusion-2-1-base/resolve/main/v2-1_512-ema-pruned.safetensors
        echo ""
        echo "✅ SD 2.1 下载完成"
        ;;
    4)
        echo ""
        echo "开始下载所有模型..."
        echo "这可能需要 30-60 分钟"
        echo ""
        cd "$MODELS_DIR"
        
        echo "[1/3] 下载 SDXL Base 1.0..."
        wget -c https://huggingface.co/stabilityai/stable-diffusion-xl-base-1.0/resolve/main/sd_xl_base_1.0.safetensors \
            || curl -L -C - -o sd_xl_base_1.0.safetensors https://huggingface.co/stabilityai/stable-diffusion-xl-base-1.0/resolve/main/sd_xl_base_1.0.safetensors
        
        echo ""
        echo "[2/3] 下载 SD 1.5..."
        wget -c https://huggingface.co/runwayml/stable-diffusion-v1-5/resolve/main/v1-5-pruned-emaonly.safetensors \
            || curl -L -C - -o v1-5-pruned-emaonly.safetensors https://huggingface.co/runwayml/stable-diffusion-v1-5/resolve/main/v1-5-pruned-emaonly.safetensors
        
        echo ""
        echo "[3/3] 下载 SD 2.1..."
        wget -c https://huggingface.co/stabilityai/stable-diffusion-2-1-base/resolve/main/v2-1_512-ema-pruned.safetensors \
            || curl -L -C - -o v2-1_512-ema-pruned.safetensors https://huggingface.co/stabilityai/stable-diffusion-2-1-base/resolve/main/v2-1_512-ema-pruned.safetensors
        
        echo ""
        echo "✅ 所有模型下载完成"
        ;;
    0)
        echo ""
        echo "跳过模型下载"
        echo "你可以稍后手动下载模型到: $MODELS_DIR"
        ;;
    *)
        echo ""
        echo "❌ 无效选择"
        exit 1
        ;;
esac

echo ""
echo "================================================"
echo "模型目录: $MODELS_DIR"
echo "================================================"
ls -lh "$MODELS_DIR"/*.safetensors 2>/dev/null || echo "暂无模型文件"
echo "================================================"
