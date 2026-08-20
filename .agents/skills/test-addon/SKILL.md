---
name: test-addon
description: "Instructions on how to test the Home Assistant llama.cpp add-on using Docker."
---

# Testing the Home Assistant llama.cpp Add-on

To test the `llama.cpp` Add-on, we simulate the Home Assistant Supervisor environment by building the Docker image locally and mounting a mocked `/data/options.json` file, which is how Home Assistant passes configuration to the add-on.

## Prerequisites
- Docker daemon must be running.

## Procedure

1. **Navigate to the test directory**
   ```bash
   cd /Users/cc-plenty/ha/homeassistant-llamacpp-addon/test
   ```

2. **Execute the test script**
   ```bash
   ./test.sh
   ```

### What the test script does:
- Builds the `llamacpp` directory into a Docker image tagged `llamacpp-addon-test`.
- Runs a container named `llamacpp-test-instance` mapping port `8080` to the host.
- Maps `test/options.json` to `/data/options.json` inside the container.
- Maps a local `test/share` directory to `/share` inside the container so downloaded models are cached locally.
- Tails the container logs to monitor the model downloading process.
- Polls `http://localhost:8080/health` to verify the server eventually boots and responds.
- Cleans up the container automatically.

### Customizing the Test
If you want to test different models, Vulkan behavior, or Speculative Decoding, edit the `test/options.json` file before running `./test.sh`.
