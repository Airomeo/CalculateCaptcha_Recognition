# container/Dockerfile

FROM python:3.12-slim

# 设置工作目录
WORKDIR /app

# 从构建上下文的 container 目录复制 requirements.txt
COPY container/requirements.txt ./

# 安装依赖
RUN pip install --no-cache-dir -r requirements.txt

# 从构建上下文的根目录复制 ONNX 模型
COPY mathcode.onnx ./

# 复制 container 目录中的所有文件到 /app
COPY container/ .

# 强制Python进入无缓冲模式，确保print和logging能立即显示
ENV PYTHONUNBUFFERED=1

# 定义容器启动时执行的命令
CMD ["python", "serve.py"]