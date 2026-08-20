<div align="center">
  <img src="llamacpp/icon.png" width="150" alt="llama.cpp Add-on Logo">
  <h1>Home Assistant llama.cpp Add-on</h1>
</div>
[![GitHub Actions Workflow Status](https://img.shields.io/github/actions/workflow/status/crysty0612/homeassistant-llamacpp-addon/test.yaml?label=Build%20Tests&style=for-the-badge)](https://github.com/crysty0612/homeassistant-llamacpp-addon/actions)
[![HACS Custom Repository](https://img.shields.io/badge/HA_Addon-Ready-blue.svg?style=for-the-badge)](https://my.home-assistant.io/redirect/supervisor_add_addon_repository/?repository_url=https%3A%2F%2Fgithub.com%2Fcrysty0612%2Fhomeassistant-llamacpp-addon)

Run large language models (LLMs) directly on your Home Assistant server using the highly optimized [llama.cpp](https://github.com/ggml-org/llama.cpp) inference engine. This Add-on wraps `llama-server`, exposing a highly configurable, memory-efficient, OpenAI-compatible API endpoint directly on your local network.

## ✨ Features

- **Hugging Face Auto-Pull:** Simply enter the Hugging Face model repository and filename (e.g., `Qwen/Qwen2.5-0.5B-Instruct-GGUF:qwen2.5-0.5b-instruct-q4_k_m.gguf`). The Add-on will automatically download and cache it upon startup.
- **Vulkan GPU Acceleration:** Natively supports passing through host GPUs via Vulkan (`/dev/dri/renderD128`) for dramatically faster token generation on supported hardware.
- **Speculative Decoding (MTP / DFLASH):** Automatically handles advanced decoding strategies. Just configure a secondary drafter model and select your decoding strategy in the UI to squeeze the maximum tokens-per-second out of your hardware.
- **Multi-Modal Vision Support:** Automatically scans Hugging Face repositories for `*mmproj*.gguf` files. If a vision projection file is detected, it is automatically passed to the server, unlocking image analysis capabilities!
- **OpenAI-Compatible API:** The server inherently provides an OpenAI-compatible `/v1/chat/completions` endpoint for seamless integration into other software.

## 🚀 Installation

The easiest way to install this add-on is by using the **My Home Assistant** link below, which will directly import this repository into your Supervisor.

[![Open your Home Assistant instance and show the add-on store with a specific add-on repository pre-filled.](https://my.home-assistant.io/badges/supervisor_add_addon_repository.svg)](https://my.home-assistant.io/redirect/supervisor_add_addon_repository/?repository_url=https%3A%2F%2Fgithub.com%2Fcrysty0612%2Fhomeassistant-llamacpp-addon)

### Manual Installation
If the button above does not work for you:
1. Navigate to your Home Assistant dashboard.
2. Go to **Settings > Add-ons > Add-on Store**.
3. Click the **three dots** in the top right corner and select **Repositories**.
4. Paste the URL of this repository: `https://github.com/crysty0612/homeassistant-llamacpp-addon`
5. Click **Add**, then close the modal.
6. Scroll down to find the new "llama.cpp" add-on and click **Install**.

## ⚙️ Configuration & Usage

Navigate to the Add-on's **Configuration** tab. You will be presented with a highly structured UI. 

### Mandatory Fields
* **Main Model to load:** Provide the strict Hugging Face path to your GGUF file. 
  * Format: `organization/repository:filename.gguf`
  * Example: `Qwen/Qwen2.5-0.5B-Instruct-GGUF:qwen2.5-0.5b-instruct-q4_k_m.gguf`

### Recommended Advanced Settings
* **Context Size:** The maximum context window of the model (default `2048`). Increasing this will increase RAM usage.
* **Vulkan Hardware Acceleration:** Toggle this on if your HA server has a compatible GPU.
* **GPU Device Path:** Default is `/dev/dri/renderD128`. Only applicable if Vulkan is enabled.
* **Speculative Decoding:** To enable, specify a smaller `Drafter Model` (using the same strict format as the main model) and pick the `Drafter Type` (MTP or DFLASH) from the dropdown.

### First Boot
On the first boot, the Add-on will reach out to Hugging Face and download the specified models. **This will take time** depending on your internet connection. 
Navigate to the Add-on's **Log** tab to watch the real-time download progress! Models are cached locally in your `/share` directory, so subsequent boots will be nearly instantaneous.

## 🔌 Connecting Home Assistant to the API

Once the Add-on says "Server is up and running" in the logs, `llama.cpp` will be exposing an OpenAI-compatible API on your Home Assistant server, usually accessible via:

```
http://<YOUR_HA_IP>:8080/v1
```

*(Note: You can change the `8080` port mapping in the Add-on's Network configuration if you wish to run multiple model instances concurrently).*

To interact with your newly hosted local model directly from Home Assistant, you can use the official [OpenAI Conversation Integration](https://www.home-assistant.io/integrations/openai_conversation/). 
- **Base URL:** `http://<YOUR_HA_IP>:8080/v1`
- **API Key:** `llama.cpp` (The key is ignored, but the field cannot be blank).
