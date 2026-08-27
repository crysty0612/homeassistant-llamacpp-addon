import os
import sys
import json
import threading
import time
import re
import http.server
import socketserver
from huggingface_hub import hf_hub_download, HfApi

DOWNLOAD_STATE = {
    "status": "Starting up...",
    "model_name": "",
    "progress_percent": "0%",
    "speed": "",
    "eta": "",
    "done": False
}

class ProgressCatcher:
    def __init__(self, original_stderr):
        self.original_stderr = original_stderr

    def write(self, text):
        self.original_stderr.write(text)
        self.original_stderr.flush()
        
        if "%|" in text:
            try:
                parts = text.split('|')
                if len(parts) >= 3:
                    pct = text.split('%')[0].strip().split()[-1] + "%"
                    DOWNLOAD_STATE["progress_percent"] = pct
                    
                    if '[' in text and ']' in text:
                        bracket_content = text.split('[')[1].split(']')[0]
                        if ',' in bracket_content:
                            times, speed = bracket_content.split(',', 1)
                            DOWNLOAD_STATE["speed"] = speed.strip()
                            if '<' in times:
                                DOWNLOAD_STATE["eta"] = times.split('<')[1].strip()
            except Exception:
                pass

    def flush(self):
        self.original_stderr.flush()

class PullStatusHandler(http.server.SimpleHTTPRequestHandler):
    def do_GET(self):
        if self.path.endswith('/pull_status'):
            self.send_response(200)
            self.send_header("Content-type", "application/json")
            self.send_header("Access-Control-Allow-Origin", "*")
            self.end_headers()
            self.wfile.write(json.dumps(DOWNLOAD_STATE).encode())
        elif self.path.endswith('/health'):
            self.send_response(200)
            self.send_header("Content-type", "application/json")
            self.send_header("Access-Control-Allow-Origin", "*")
            self.end_headers()
            self.wfile.write(json.dumps({"status": "Downloading Models..."}).encode())
        elif self.path == '/' or self.path == '/index.html' or self.path.endswith('index.html'):
            self.path = '/index.html'
            return http.server.SimpleHTTPRequestHandler.do_GET(self)
        else:
            return http.server.SimpleHTTPRequestHandler.do_GET(self)

    def log_message(self, format, *args):
        pass

def start_web_server():
    public_dir = '/opt/llama.cpp/public'
    if not os.path.exists(public_dir):
        # Fallback for local testing
        if os.path.exists('/Users/cc-plenty/ha/homeassistant-llamacpp-addon/llamacpp/public'):
            public_dir = '/Users/cc-plenty/ha/homeassistant-llamacpp-addon/llamacpp/public'
        else:
            public_dir = '.'
            
    socketserver.TCPServer.allow_reuse_address = True
    
    handler = lambda *args, **kwargs: PullStatusHandler(*args, directory=public_dir, **kwargs)
    httpd = socketserver.TCPServer(("", 8080), handler)
    
    def serve():
        httpd.timeout = 0.5
        while not DOWNLOAD_STATE["done"]:
            httpd.handle_request()
        httpd.server_close()
        
    threading.Thread(target=serve, daemon=True).start()

def resolve_filename(repo_id, filename_pattern):
    if filename_pattern.endswith(".gguf"):
        return filename_pattern
    print(f"Resolving full filename for pattern '{filename_pattern}' in repo '{repo_id}'...")
    DOWNLOAD_STATE["status"] = f"Resolving {filename_pattern}..."
    api = HfApi()
    try:
        files = api.list_repo_files(repo_id=repo_id)
        matching_files = [f for f in files if filename_pattern in f and f.endswith(".gguf")]
        if matching_files:
            print(f"Resolved to {matching_files[0]}")
            return matching_files[0]
        else:
            print(f"Could not resolve pattern '{filename_pattern}' to a .gguf file in {repo_id}")
            sys.exit(1)
    except Exception as e:
        print(f"Error checking repo files: {e}")
        sys.exit(1)

def download_model(repo_id, filename, dest_dir):
    print(f"Downloading {filename} from {repo_id}...")
    DOWNLOAD_STATE["model_name"] = filename
    DOWNLOAD_STATE["status"] = "Downloading..."
    DOWNLOAD_STATE["progress_percent"] = "0%"
    DOWNLOAD_STATE["speed"] = ""
    DOWNLOAD_STATE["eta"] = ""
    try:
        path = hf_hub_download(repo_id=repo_id, filename=filename, local_dir=dest_dir, local_dir_use_symlinks=False)
        print(f"Downloaded to {path}")
        return path
    except Exception as e:
        print(f"Failed to download {filename} from {repo_id}: {e}")
        sys.exit(1)

def find_and_download_mmproj(repo_id, dest_dir):
    print(f"Checking for mmproj files in {repo_id}...")
    api = HfApi()
    try:
        files = api.list_repo_files(repo_id=repo_id)
        mmproj_files = [f for f in files if "mmproj" in f.lower() and f.endswith(".gguf")]
        if mmproj_files:
            mmproj_file = mmproj_files[0]
            print(f"Found mmproj file: {mmproj_file}")
            return download_model(repo_id, mmproj_file, dest_dir)
        else:
            print("No mmproj file found.")
            return None
    except Exception as e:
        print(f"Error checking repo files: {e}")
        return None

def main():
    sys.stderr = ProgressCatcher(sys.stderr)
    start_web_server()
    
    DOWNLOAD_STATE["status"] = "Reading configuration..."
    
    options_path = "/data/options.json"
    if not os.path.exists(options_path):
        options_path = "llamacpp/config.yaml"
        if not os.path.exists(options_path):
            options_path = "config.yaml"
            if not os.path.exists(options_path):
                print(f"Options file not found")
                DOWNLOAD_STATE["done"] = True
                sys.exit(1)

    try:
        with open(options_path, "r") as f:
            if options_path.endswith('.json'):
                options = json.load(f)
            else:
                import yaml
                options = yaml.safe_load(f).get("options", {})
    except Exception:
        options = {}

    models_list = options.get("MODELS", [])
    model_dir = options.get("LLAMACPP_MODEL_DIR", "/share/llamacpp")
    
    os.makedirs(model_dir, exist_ok=True)
    
    if not models_list:
        print("No models configured. Please configure MODELS in the add-on UI.")
        DOWNLOAD_STATE["done"] = True
        sys.exit(1)
    
    exec_configs = []
    
    for idx, model_cfg in enumerate(models_list):
        use_case = model_cfg.get("LLAMACPP_USE_CASE", "text").strip().lower()
        main_model = model_cfg.get("LLAMACPP_MODEL", "").strip()
        disable_reasoning = model_cfg.get("LLAMACPP_DISABLE_REASONING", False)
        
        if not main_model:
            continue
            
        drafter = model_cfg.get("LLAMACPP_DRAFTER", "").strip()
        drafter_type = model_cfg.get("LLAMACPP_DRAFTER_TYPE", "none").strip()
            
        exec_config = {}
        exec_config["use_case"] = use_case
        exec_config["disable_reasoning"] = disable_reasoning
        
        if ":" not in main_model:
            print(f"Invalid model format '{main_model}'")
            DOWNLOAD_STATE["done"] = True
            sys.exit(1)
            
        model_repo, model_file_pattern = main_model.split(":", 1)
        model_file = resolve_filename(model_repo, model_file_pattern)
        model_path = download_model(model_repo, model_file, model_dir)
        
        exec_config["model"] = model_path
        
        if use_case == "vision":
            mmproj_path = find_and_download_mmproj(model_repo, model_dir)
            exec_config["mmproj"] = mmproj_path
        
        drafter_path = None
        if drafter:
            if ":" not in drafter:
                print(f"Invalid drafter format '{drafter}'")
                sys.exit(1)
            drafter_repo, drafter_file_pattern = drafter.split(":", 1)
            drafter_file = resolve_filename(drafter_repo, drafter_file_pattern)
            drafter_path = download_model(drafter_repo, drafter_file, model_dir)
        
        exec_config["drafter"] = drafter_path
        
        if drafter_type.lower() != "none":
            exec_config["drafter_type"] = drafter_type
            
        draft_min = model_cfg.get("LLAMACPP_DRAFT_MIN")
        draft_max = model_cfg.get("LLAMACPP_DRAFT_MAX")
        extra_args = model_cfg.get("LLAMACPP_EXTRA_ARGS", "").strip()
        
        if draft_min is not None:
            exec_config["draft_min"] = draft_min
        if draft_max is not None:
            exec_config["draft_max"] = draft_max
        if extra_args:
            exec_config["extra_args"] = extra_args
            
        exec_configs.append(exec_config)
            
    with open("/tmp/exec_config.json", "w") as f:
        json.dump(exec_configs, f)
        
    print("--- Models currently available in directory ---")
    for f in os.listdir(model_dir):
        print(f" - {f}")
    print("-----------------------------------------------")
    
    DOWNLOAD_STATE["status"] = "Complete!"
    DOWNLOAD_STATE["progress_percent"] = "100%"
    DOWNLOAD_STATE["done"] = True
    time.sleep(1) # Let the last request finish

if __name__ == "__main__":
    main()
