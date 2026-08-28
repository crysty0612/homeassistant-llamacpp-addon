import os
import json
import requests
from flask import Flask, send_from_directory, jsonify, request, abort

app = Flask(__name__, static_folder='/opt/llama.cpp/public', static_url_path='')

LLAMA_SERVER_URL = "http://localhost:8080"
MODEL_DIR = "/share/llamacpp"

@app.route('/')
def index():
    return send_from_directory(app.static_folder, 'index.html')

@app.route('/api/models', methods=['GET'])
def list_models():
    if not os.path.exists(MODEL_DIR):
        return jsonify([])
    
    # Read exec_config to find pairings
    pairings = []
    try:
        if os.path.exists('/tmp/exec_config.json'):
            with open('/tmp/exec_config.json', 'r') as f:
                pairings = json.load(f)
    except Exception as e:
        print(f"Failed to read exec_config: {e}")

    # Map drafters to their main models
    drafter_to_main = {}
    main_to_drafter = {}
    for p in pairings:
        m = p.get('model', '')
        d = p.get('drafter', '')
        if m and d:
            m_name = os.path.basename(m)
            d_name = os.path.basename(d)
            drafter_to_main[d_name] = m_name
            main_to_drafter[m_name] = d_name

    models = []
    for filename in os.listdir(MODEL_DIR):
        if filename.endswith(".gguf"):
            # Skip standalone display for drafters if they are mapped to a main model
            if filename in drafter_to_main:
                continue
            
            filepath = os.path.join(MODEL_DIR, filename)
            size_bytes = os.path.getsize(filepath)
            
            model_info = {
                "filename": filename,
                "size_bytes": size_bytes,
                "drafter": None
            }
            
            if filename in main_to_drafter:
                d_name = main_to_drafter[filename]
                d_path = os.path.join(MODEL_DIR, d_name)
                if os.path.exists(d_path):
                    model_info["drafter"] = {
                        "filename": d_name,
                        "size_bytes": os.path.getsize(d_path)
                    }
                    
            models.append(model_info)
            
    # Also add orphaned drafters (in case they were in the dir but not in config)
    # Wait, the above logic skips drafters IF they are in drafter_to_main, which means they are paired.
    # If they are not paired, they will just show up as regular models.
    return jsonify(models)

@app.route('/api/models/<path:filename>', methods=['DELETE'])
def delete_model(filename):
    if not filename.endswith(".gguf") or "/" in filename or "\\" in filename:
        abort(400, "Invalid filename")
        
    filepath = os.path.join(MODEL_DIR, filename)
    if os.path.exists(filepath):
        try:
            os.remove(filepath)
            
            # Check if we should also delete the paired drafter
            delete_drafter = request.args.get('delete_drafter', 'false').lower() == 'true'
            drafter_name = request.args.get('drafter_name', '')
            
            drafter_msg = ""
            if delete_drafter and drafter_name and drafter_name.endswith('.gguf') and not "/" in drafter_name:
                d_path = os.path.join(MODEL_DIR, drafter_name)
                if os.path.exists(d_path):
                    os.remove(d_path)
                    drafter_msg = f" and paired drafter {drafter_name}"
            
            return jsonify({"status": "success", "message": f"Deleted {filename}{drafter_msg}"})
        except Exception as e:
            abort(500, str(e))
    else:
        abort(404, "File not found")

@app.route('/health', methods=['GET'])
def proxy_health():
    try:
        resp = requests.get(f"{LLAMA_SERVER_URL}/health", timeout=2)
        # Exclude headers like Transfer-Encoding that can cause issues in simple proxies
        excluded_headers = ['content-encoding', 'content-length', 'transfer-encoding', 'connection']
        headers = [(name, value) for (name, value) in resp.raw.headers.items()
                   if name.lower() not in excluded_headers]
        return (resp.content, resp.status_code, headers)
    except requests.exceptions.RequestException:
        abort(502, "llama-server not responding")

@app.route('/metrics', methods=['GET'])
def proxy_metrics():
    try:
        resp = requests.get(f"{LLAMA_SERVER_URL}/metrics", timeout=2)
        excluded_headers = ['content-encoding', 'content-length', 'transfer-encoding', 'connection']
        headers = [(name, value) for (name, value) in resp.raw.headers.items()
                   if name.lower() not in excluded_headers]
        return (resp.content, resp.status_code, headers)
    except requests.exceptions.RequestException:
        abort(502, "llama-server not responding")

# Fallback for static files
@app.route('/<path:path>')
def send_static(path):
    return send_from_directory(app.static_folder, path)

if __name__ == '__main__':
    # Disable werkzeug logging to keep HA logs clean
    import logging
    log = logging.getLogger('werkzeug')
    log.setLevel(logging.ERROR)
    port = int(os.environ.get("PORT", 8081))
    print(f"Management UI Server started on port {port}", flush=True)
    app.run(host='0.0.0.0', port=port)
