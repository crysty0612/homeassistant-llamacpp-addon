# Changelog

## [1.4.1](https://github.com/crysty0612/homeassistant-llamacpp-addon/compare/v1.4.0...v1.4.1) (2026-08-28)

### Bug Fixes
* **llamacpp:** resolve iGPU SYCL memory limits and restore PID 1 logging ([db1a09a](https://github.com/crysty0612/homeassistant-llamacpp-addon/commit/db1a09a8290d515d179a8c357693bd8e781b83c4))

### v1.4.0
- **Model Manager UI:** Introduced a new Web UI for real-time model download management and monitoring (available on port 8081).
- **SYCL Stability:** Major fixes for Intel iGPU compatibility, including upgrading oneAPI to 2025 (libsycl.so.8), resolving Memory Allocation limits (VMM), and restoring proper PID 1 HA Addon UI logging.
- **CI/CD:** Replaced semantic-release HTTPS overrides with native SSH deploy keys for GitHub Actions pipeline stability.

### v1.3.0 - v1.3.6
- **Intel SYCL Backend:** Introduced full support for Intel integrated graphics (iGPUs) using the highly optimized oneAPI SYCL backend.
- **Dynamic Linking:** Added automated resolution for oneAPI runtime libraries (libdnnl, libsvml, libsycl) directly inside the Docker container.
- **CPU Fallbacks:** Added dynamic fallback to CPU binaries if the configured GPU device path is not found.

### v1.2.2
- **DSpark Speculative Decoding:** Added official support for the `dspark` drafting model for accelerated inference.
- **Model Config Engine:** Added support for passing custom `spec-draft-n-min`, `spec-draft-n-max`, and arbitrary extra CLI flags directly from the Home Assistant add-on configuration.

### v1.2.1
- **Live Downloads:** Implemented live UI download progress tracking for model fetching.

### v1.1.6 - v1.1.11
- **Automated Binary Syncing:** Deployed automated workflows to dynamically resolve and pull the latest stable `ggml-org/llama.cpp` releases (up to `v0.3.0`).

### v1.1.5
- **Semantic Versioning CI:** Automated release tags, branches, and changelog generation using GitHub Actions.

### v1.1.0
- **Multi-Model Router:** Completed multi-model router support, allowing multiple models to be served concurrently with dynamic `presets.ini` generation.
- **Vision Models:** Added the ability to toggle reasoning off specifically for Vision (Llava/Qwen) models.

### v1.0.5
- **MTP Drafting:** Fixed internal Speculative Decoding arguments for MTP models.

### v1.0.1 - v1.0.4
- **Auto-Updates:** Added configuration toggle to automatically update llama.cpp binaries on boot.
- **Initial Setup:** Configured dynamic use cases, dashboard mapping logic, and stable releases.
