#!/bin/bash
# set -e 可以确保一旦某个步骤失败，整个部署流程会立刻中断，减少风险。
set -e

# 脚本功能：自动化 Docker 镜像构建过程

cd ..

# 定义镜像名称和标签
IMAGE_NAME="captcha"

echo "🛠 构建新镜像..."
docker build -t $IMAGE_NAME -f container/Dockerfile .

echo "🚀 启动容器..."
docker run -d \
  -e TZ=Asia/Shanghai \
  -p 32769:8000 \
  --restart unless-stopped \
  $IMAGE_NAME

echo "✅ 部署完成！"