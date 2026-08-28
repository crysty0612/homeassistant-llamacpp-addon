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
    wget \
    gpg \
    && rm -rf /var/lib/apt/lists/*

# Install Intel graphics drivers (Level Zero) and oneAPI SYCL runtime
# llama.cpp SYCL prebuilts are compiled against oneAPI 2025.3 (libsycl.so.8)
# We install compiler-dpcpp-cpp-runtime (provides libsycl.so) + dnnl + mkl runtimes
RUN wget -qO - https://repositories.intel.com/gpu/intel-graphics.key | gpg --yes --dearmor --output /usr/share/keyrings/intel-graphics.gpg && \
    echo "deb [arch=amd64 signed-by=/usr/share/keyrings/intel-graphics.gpg] https://repositories.intel.com/gpu/ubuntu noble client" | tee /etc/apt/sources.list.d/intel-gpu-noble.list && \
    wget -O- https://apt.repos.intel.com/intel-gpg-keys/GPG-PUB-KEY-INTEL-SW-PRODUCTS.PUB | gpg --yes --dearmor | tee /usr/share/keyrings/oneapi-archive-keyring.gpg && \
    echo "deb [signed-by=/usr/share/keyrings/oneapi-archive-keyring.gpg] https://apt.repos.intel.com/oneapi all main" | tee /etc/apt/sources.list.d/oneAPI.list && \
    apt-get update && apt-get install -y \
    intel-opencl-icd intel-level-zero-gpu level-zero \
    intel-oneapi-compiler-dpcpp-cpp-runtime-2025.3 intel-oneapi-runtime-dnnl=2025.3.0-409 intel-oneapi-runtime-mkl=2025.3.0-461 \
    && rm -rf /var/lib/apt/lists/* \
    && echo "Configuring dynamic linker for Intel oneAPI libraries..." \
    && find /opt/intel -name "*.so*" -exec dirname {} \; | sort -u > /etc/ld.so.conf.d/intel.conf \
    && ldconfig

# Install huggingface_hub for python-based model pulling
RUN pip3 install --no-cache-dir huggingface_hub flask requests --break-system-packages

WORKDIR /opt/llama.cpp

COPY llama_version.txt /opt/llama.cpp/llama_version.txt

# Add the runtime script, python utility, and public web UI
COPY pull_models.py /pull_models.py
COPY ui_server.py /ui_server.py
COPY run.sh /run.sh
COPY public /opt/llama.cpp/public
COPY logo.png /opt/llama.cpp/public/logo.png
RUN chmod +x /run.sh

ENTRYPOINT [ "/run.sh" ]
