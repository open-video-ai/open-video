# OpenVideo — container image for the open-video CLI.
# The generation engine (ComfyUI + weights) is mounted/reached separately.
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

# `open-video serve` is not shipped yet (see pyproject optional-dependencies).
# Default: report install health + engine reachability, then exit.
# Generate with e.g.:
#   docker run --rm <image> open-video "sunset waves" --dry-run
CMD ["open-video", "status"]
