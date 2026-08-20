import os
import sys
import json
from huggingface_hub import hf_hub_download, HfApi

def resolve_filename(repo_id, filename_pattern):
    if filename_pattern.endswith(".gguf"):
        return filename_pattern
    print(f"Resolving full filename for pattern '{filename_pattern}' in repo '{repo_id}'...")
    api = HfApi()
    try:
        files = api.list_repo_files(repo_id=repo_id)
        # Find first file that contains the pattern and ends with .gguf
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
            # Just take the first one
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
    options_path = "/data/options.json"
    if not os.path.exists(options_path):
        print(f"Options file not found at {options_path}")
        sys.exit(1)

    with open(options_path, "r") as f:
        options = json.load(f)

    use_case = options.get("LLAMACPP_USE_CASE", "text").strip().lower()
    model_dir = options.get("LLAMACPP_MODEL_DIR", "/share/llamacpp")
    main_model = options.get("LLAMACPP_MODEL", "").strip()
    
    # Ignore Drafter if Vision use case is selected
    if use_case == "vision":
        print("Vision use case selected. Disabling speculative decoding to prevent crashes.")
        drafter = ""
        drafter_type = "none"
    else:
        drafter = options.get("LLAMACPP_DRAFTER", "").strip()
        drafter_type = options.get("LLAMACPP_DRAFTER_TYPE", "none").strip()
    
    os.makedirs(model_dir, exist_ok=True)
    
    if not main_model:
        print("No main model configured. Please configure LLAMACPP_MODEL in the add-on UI.")
        sys.exit(1)
    
    exec_config = {}
    
    # Process main model
    if ":" not in main_model:
        print(f"Invalid model format '{main_model}'. Expected 'org/repo:filename_or_pattern'")
        sys.exit(1)
        
    model_repo, model_file_pattern = main_model.split(":", 1)
    model_file = resolve_filename(model_repo, model_file_pattern)
    model_path = download_model(model_repo, model_file, model_dir)
    mmproj_path = find_and_download_mmproj(model_repo, model_dir)
    
    exec_config["model"] = model_path
    exec_config["mmproj"] = mmproj_path
    
    # Process drafter model
    drafter_path = None
    if drafter:
        if ":" not in drafter:
            print(f"Invalid drafter format '{drafter}'. Expected 'org/repo:filename_or_pattern'")
            sys.exit(1)
        drafter_repo, drafter_file_pattern = drafter.split(":", 1)
        drafter_file = resolve_filename(drafter_repo, drafter_file_pattern)
        drafter_path = download_model(drafter_repo, drafter_file, model_dir)
    
    exec_config["drafter"] = drafter_path
    
    if drafter_type.lower() != "none":
        exec_config["drafter_type"] = drafter_type
            
    # Save the execution config
    with open("/tmp/exec_config.json", "w") as f:
        json.dump(exec_config, f)
        
    print("--- Models currently available in directory ---")
    for f in os.listdir(model_dir):
        print(f" - {f}")
    print("-----------------------------------------------")

if __name__ == "__main__":
    main()
