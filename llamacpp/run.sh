#!/usr/bin/env bash
set -e

CONFIG_PATH=/data/options.json

echo "Starting llama.cpp Home Assistant Add-on..."

# 1. Pull models and configure
python3 /pull_models.py

# Check if exec_config exists
if [ ! -f /tmp/exec_config.json ]; then
    echo "No models were configured or successfully pulled. Exiting."
    exit 1
fi

# 2. Extract configuration
VULKAN=$(jq --raw-output '.LLAMACPP_VULKAN' $CONFIG_PATH)
GPU_PATH=$(jq --raw-output '.LLAMACPP_GPU_PATH // empty' $CONFIG_PATH)
CTX_SIZE=$(jq --raw-output '.LLAMACPP_CTX_SIZE' $CONFIG_PATH)
THREADS=$(jq --raw-output '.LLAMACPP_THREADS' $CONFIG_PATH)
BATCH_SIZE=$(jq --raw-output '.LLAMACPP_BATCH_SIZE' $CONFIG_PATH)
PARALLEL=$(jq --raw-output '.LLAMACPP_PARALLEL' $CONFIG_PATH)
FLASH_ATTN=$(jq --raw-output '.LLAMACPP_FLASH_ATTN' $CONFIG_PATH)

MODEL=$(jq --raw-output '.model // empty' /tmp/exec_config.json)
MMPROJ=$(jq --raw-output '.mmproj // empty' /tmp/exec_config.json)
DRAFTER=$(jq --raw-output '.drafter // empty' /tmp/exec_config.json)
DRAFTER_TYPE=$(jq --raw-output '.drafter_type // empty' /tmp/exec_config.json)

if [ -z "$MODEL" ]; then
    echo "Error: No main model path found in execution config."
    exit 1
fi

# 3. Handle Vulkan and GPU
SERVER_DIR="/opt/llama.cpp/build-cpu"
SERVER_BIN="$SERVER_DIR/llama-server"

if [ "$VULKAN" = "true" ]; then
    echo "Vulkan enabled. Verifying GPU..."
    if [ -z "$GPU_PATH" ]; then
        echo "Error: LLAMACPP_VULKAN is true but LLAMACPP_GPU_PATH is empty."
        exit 1
    fi
    if [ ! -e "$GPU_PATH" ]; then
        echo "Error: GPU path $GPU_PATH does not exist. Ensure GPU is passed to the addon."
        exit 1
    fi
    echo "GPU found at $GPU_PATH. Using Vulkan binary."
    SERVER_DIR="/opt/llama.cpp/build-vulkan"
    SERVER_BIN="$SERVER_DIR/llama-server"
else
    echo "Using CPU binary."
fi

# Set library path so the server can find its .so files
export LD_LIBRARY_PATH="$SERVER_DIR:$LD_LIBRARY_PATH"

# 4. Construct Server Command
CMD=("$SERVER_BIN")
CMD+=("--host" "0.0.0.0")
CMD+=("--port" "8080")
CMD+=("-m" "$MODEL")
CMD+=("-c" "$CTX_SIZE")
CMD+=("-t" "$THREADS")
CMD+=("-b" "$BATCH_SIZE")
CMD+=("--parallel" "$PARALLEL")

if [ "$FLASH_ATTN" = "true" ]; then
    CMD+=("-fa")
fi

if [ -n "$MMPROJ" ]; then
    echo "Adding mmproj: $MMPROJ"
    CMD+=("--mmproj" "$MMPROJ")
fi

if [ -n "$DRAFTER" ]; then
    echo "Adding Drafter Model: $DRAFTER"
    CMD+=("-md" "$DRAFTER")
fi

if [ -n "$DRAFTER_TYPE" ]; then
    echo "Adding Speculative Decoding Type: $DRAFTER_TYPE"
    if [ "$DRAFTER_TYPE" = "dflash" ]; then
        CMD+=("--spec-type" "draft-dflash")
    else
        CMD+=("--spec-type" "$DRAFTER_TYPE")
    fi
fi

# 5. Start Server
echo "Starting server with command: ${CMD[*]}"
exec "${CMD[@]}"
