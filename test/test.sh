#!/usr/bin/env bash
set -e

echo "Building Docker image for testing..."
# Build the image using the same BUILD_FROM as Home Assistant
docker build --build-arg BUILD_FROM=ubuntu:24.04 -t llamacpp-addon-test ../llamacpp

echo "Starting container..."
# Run the container with the mocked options.json mounted
docker run -d --name llamacpp-test-instance \
  -p 8080:8080 \
  -v $(pwd)/options.json:/data/options.json \
  -v $(pwd)/share:/share \
  llamacpp-addon-test

echo "Waiting for models to download and server to start (this may take a minute)..."

# Tail logs in the background so we can see what's happening
docker logs -f llamacpp-test-instance &
LOG_PID=$!

# Wait until the server is listening
for i in {1..60}; do
  if curl -s http://localhost:8080/health > /dev/null; then
    echo -e "\nServer is up and running!"
    break
  fi
  sleep 2
done

# Cleanup
echo "Stopping and removing test container..."
kill $LOG_PID || true
docker stop llamacpp-test-instance
docker rm llamacpp-test-instance

echo "Test complete!"
