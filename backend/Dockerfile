FROM nvidia/cuda:12.4.1-cudnn-runtime-ubuntu22.04
ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1 UV_SYSTEM_PYTHON=1
RUN apt-get update && apt-get install -y python3.12 python3.12-venv python3-pip ffmpeg curl git && rm -rf /var/lib/apt/lists/* && pip install uv
WORKDIR /app
COPY pyproject.toml uv.lock ./
RUN uv pip install -e .
COPY . .
