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

# Download and extract the latest stable releases of llama.cpp from ggml-org
RUN set -e; \
    ARCH=$(dpkg --print-architecture); \
    if [ "$ARCH" = "amd64" ]; then LLAMA_ARCH="x64"; \
    elif [ "$ARCH" = "arm64" ]; then LLAMA_ARCH="arm64"; \
    else echo "Unsupported architecture: $ARCH"; exit 1; fi; \
    \
    LATEST_RELEASE=$(curl -s https://api.github.com/repos/ggml-org/llama.cpp/releases/latest); \
    \
    # Find and download the CPU tarball URL
    CPU_URL=$(echo "$LATEST_RELEASE" | grep -o "https://github.com/ggml-org/llama.cpp/releases/download/[^\"]*ubuntu-${LLAMA_ARCH}\.tar\.gz" | head -n 1); \
    echo "Downloading CPU: $CPU_URL"; \
    curl -L -o cpu.tar.gz "$CPU_URL"; \
    mkdir -p build-cpu; \
    tar -xzf cpu.tar.gz -C build-cpu --strip-components=1; \
    rm cpu.tar.gz; \
    \
    # Find and download the Vulkan tarball URL
    VULKAN_URL=$(echo "$LATEST_RELEASE" | grep -o "https://github.com/ggml-org/llama.cpp/releases/download/[^\"]*ubuntu-vulkan-${LLAMA_ARCH}\.tar\.gz" | head -n 1); \
    echo "Downloading Vulkan: $VULKAN_URL"; \
    curl -L -o vulkan.tar.gz "$VULKAN_URL"; \
    mkdir -p build-vulkan; \
    tar -xzf vulkan.tar.gz -C build-vulkan --strip-components=1; \
    rm vulkan.tar.gz

# Add the runtime script, python utility, and public web UI
COPY pull_models.py /pull_models.py
COPY run.sh /run.sh
COPY public /opt/llama.cpp/public
RUN chmod +x /run.sh

ENTRYPOINT [ "/run.sh" ]
