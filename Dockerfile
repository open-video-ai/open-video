# OpenVideo — containerized deployment (for SaaS/API hosting)
# Multi-stage: build env → runtime
FROM python:3.12-slim AS base

WORKDIR /app

# Install system deps (ffmpeg for video processing, git for plugins)
RUN apt-get update && apt-get install -y --no-install-recommends \
    ffmpeg git curl aria2 && \
    rm -rf /var/lib/apt/lists/*

# Copy open-video
COPY . /app/open-video
WORKDIR /app/open-video

# Install open-video (core only — ComfyUI installed separately)
RUN pip install --no-cache-dir -e .

# ComfyUI + H3 weights are expected at /app/ComfyUI (mounted or downloaded)
# ENV COMFYUI_PATH=/app/ComfyUI
# ENV OPEN_VIDEO_COMFYUI=http://host.docker.internal:8188

# Default: start the API server
EXPOSE 8000
CMD ["python", "cli/open_video.py", "serve", "--host", "0.0.0.0", "--port", "8000"]
