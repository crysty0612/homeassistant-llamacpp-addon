# Home Assistant llama.cpp Add-on Documentation

> ⚡ This version runs on **llama.cpp** [b10567](https://github.com/ggml-org/llama.cpp/releases/tag/b10567)

Welcome to the `llama.cpp` Add-on for Home Assistant! This add-on provides a fully functional, GPU-accelerated OpenAI-compatible API running directly on your Home Assistant machine, allowing you to use Local LLMs privately and securely.

## 🛠️ Configuration & Models

Before starting the add-on, you must configure it to download a model.

1. Go to the **Configuration** tab.
2. In the **Main Model** field, enter a Hugging Face repository and a GGUF filename (or pattern).
   * **Format:** `org/repo:filename_or_pattern`
   * **Example 1:** `unsloth/Qwen3.5-9B-GGUF:UD-Q4_K_XL` (This will automatically find the matching GGUF).
   * **Example 2:** `Qwen/Qwen2.5-0.5B-Instruct-GGUF:qwen2.5-0.5b-instruct-q4_k_m.gguf`
3. Optional: Enter a **Hugging Face Token** (`hf_...`) to download gated/private models.
4. Optional: If your Home Assistant runs on an x86 machine with an integrated or dedicated GPU, enable **Vulkan** for massive performance boosts.
5. Save and Start the add-on. 

The add-on will automatically download your models on the first boot. Check the **Log** tab to track the progress!

---

## 🔗 Integrations

Once the add-on is running, you can connect it to Home Assistant using custom integrations. Because this add-on runs internally within Home Assistant, you should use the internal hostname to connect.

Your internal Base URL is:
```text
http://3927ed12-llamacpp:8080/v1
```
*(Note: Internal connections via the add-on hostname ALWAYS use port `8080`, regardless of any custom port mappings you set in the Network tab).*

### 1. Extended OpenAI Conversation

The [Extended OpenAI Conversation](https://github.com/jekalmin/extended_openai_conversation) integration allows you to replace your Home Assistant Assist voice/text assistant with a local LLM, capable of calling scripts, turning on lights, and querying sensors!

**Setup:**
1. Install `Extended OpenAI Conversation` via HACS.
2. Add the integration in Home Assistant Settings > Devices & Services.
3. Configure as follows:
   - **API Key:** `llama.cpp` (This can be anything, but cannot be blank).
   - **Base URL:** `http://3927ed12-llamacpp:8080/v1`
   - **API Version:** Leave default or blank.
4. In the integration settings, specify the exact model name that was downloaded (e.g., `qwen2.5-0.5b-instruct-q4_k_m.gguf`).
5. Configure your Assist pipeline to use this new conversation agent!

### 2. LLM Vision

If you have downloaded a multimodal model (like LLaVA or Qwen-VL) and its corresponding `mmproj` file (automatically downloaded if available in the same repository), you can use [LLM Vision](https://llmvision.gitbook.io/getting-started) to analyze camera feeds or images!

**Setup:**
1. Install `LLM Vision` via HACS.
2. Add the integration in Home Assistant Settings > Devices & Services.
3. Select **OpenAI Compatible Provider**.
4. Configure as follows:
   - **API Key:** `llama.cpp` (This field cannot be blank)
   - **Host:** `3927ed12-llamacpp` (Do not include http://)
   - **Port:** `8080` (Internal HA network always uses 8080, regardless of Network tab mapping)
5. You can now use the `llmvision.image_analyzer` service in your automations to analyze local camera feeds using your local model!

> [!WARNING]
> **Vision & Speculative Decoding Conflict:** Currently, `llama.cpp` has an upstream bug where processing images while a Drafter (Speculative Decoding) is enabled will crash the server. If you intend to use Vision, you **MUST** select the "vision" Use Case in the Add-on configuration, which will safely disable any configured drafters.

## 📊 Ingress Web UI & Dashboard

Clicking the **"Open Web UI"** button (if you enabled "Show in sidebar") will take you to a custom Health & Status dashboard!

This dashboard provides real-time metrics pulled directly from the `llama.cpp` engine:
- Server Uptime and Liveness Status
- Currently Loaded Models & Speculative Decoding Drafters
- Context Size, Batch Size, and Hardware Information
- Active generation slots and token processing metrics

*Note: The Web UI is hosted over Ingress, keeping your local models secure without exposing the raw API endpoint to the web.*
