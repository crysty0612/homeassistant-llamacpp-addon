ARG BUILD_FROM
FROM ubuntu:24.04

ENV DEBIAN_FRONTEND=noninteractive

# Minimal dependencies, no build tools required as we use release binaries
RUN apt-get update && apt-get install -y \
    curl \
    jq \
    python3 \
    python3-pip \
    vulkan-tools \
    libvulkan1 \
    && rm -rf /var/lib/apt/lists/*

# Install huggingface_hub for python-based model pulling
RUN pip3 install --no-cache-dir huggingface_hub --break-system-packages

WORKDIR /opt/llama.cpp

COPY llama_version.txt /opt/llama.cpp/llama_version.txt

# Add the runtime script, python utility, and public web UI
COPY pull_models.py /pull_models.py
COPY run.sh /run.sh
COPY public /opt/llama.cpp/public
COPY logo.png /opt/llama.cpp/public/logo.png
RUN chmod +x /run.sh

ENTRYPOINT [ "/run.sh" ]
