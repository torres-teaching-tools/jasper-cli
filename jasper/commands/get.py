import os, requests, json, shutil, base64
from jasper.utils import load_config, save_config
from jasper.pretty import print_status

def register(subparsers):
    p = subparsers.add_parser("get", help="Download starter code for a problem or module")
    p.add_argument("query", help="Problem id/name or module code (e.g., m01)")
    p.set_defaults(func=run)

def clear_directory_contents(path):
    for entry in os.listdir(path):
        full_path = os.path.join(path, entry)
        try:
            if os.path.islink(full_path) or os.path.isfile(full_path):
                os.unlink(full_path)
            elif os.path.isdir(full_path):
                shutil.rmtree(full_path)
        except Exception as e:
            print_status(f"Failed to remove '{full_path}': {e}", success=False)

def write_files(project_path, files_dict):
    for rel, payload in files_dict.items():
        fpath = os.path.join(project_path, rel)
        os.makedirs(os.path.dirname(fpath), exist_ok=True)
        try:
            data = base64.b64decode(payload["content_base64"])
            with open(fpath, "wb") as f:
                f.write(data)
        except Exception as e:
            print_status(f"Could not write '{rel}': {e}", success=False)

def maybe_prepare_folder(folder_name):
    # Find project root by locating `.devcontainer`
    root_dir = find_project_root()
    project_path = os.path.join(root_dir, folder_name)

    if os.path.exists(project_path):
        print_status(f"⚠️ Folder '{folder_name}' already exists.", success=False)
        confirm = input(f"Type 'yes' to overwrite ALL files in '{folder_name}': ").strip().lower()
        if confirm != "yes":
            print_status("Download cancelled by user.", success=False)
            return None
        clear_directory_contents(project_path)
        print_status(f"🧹 Cleared contents of '{folder_name}'", success=True)
    os.makedirs(project_path, exist_ok=True)
    return project_path

def run(args):
    cfg = load_config()
    server_url = cfg.get("server_url", "http://localhost:3000")
    url = f"{server_url}/get-problem"
    try:
        resp = requests.get(url, params={"q": args.query}, timeout=20)
    except requests.exceptions.ConnectTimeout:
        return print_status("Connection timed out. Is the server reachable?", success=False)
    except requests.exceptions.ConnectionError:
        return print_status("Cannot connect. Check server URL or network.", success=False)
    except Exception as e:
        return print_status(f"Unexpected network error: {e}", success=False)

    # Non-200s
    if resp.status_code == 404:
        try:
            detail = resp.json().get("error", "Not found")
        except Exception:
            detail = "Not found"
        return print_status(f"No released problems matched '{args.query}'. ({detail})", success=False)
    if resp.status_code >= 500:
        return print_status("Server error. Try again later or contact the instructor.", success=False)
    if resp.status_code != 200:
        return print_status(f"Unexpected status {resp.status_code}.", success=False)

    # Parse JSON
    try:
        data = resp.json()
    except ValueError:
        return print_status("Invalid response from server (not JSON).", success=False)

    # Single item
    if "project_name" in data:
        folder = data["project_name"]
        project_path = maybe_prepare_folder(folder)
        if not project_path:
            return
        write_files(project_path, data.get("files", {}))
        if "meta" in data:
            with open(os.path.join(project_path, "meta.json"), "w", encoding="utf-8") as f:
                json.dump(data["meta"], f, indent=2)
        return print_status(f"Downloaded: {folder}", success=True)

    # Multiple items (module)
    items = data.get("items", [])
    if not items:
        return print_status(f"No released problems matched '{args.query}'.", success=False)

    for item in items:
        folder = item["project_name"]
        project_path = maybe_prepare_folder(folder)
        if not project_path:
            # user refused overwrite of one project; continue to next
            continue
        write_files(project_path, item.get("files", {}))
        if "meta" in item:
            with open(os.path.join(project_path, "meta.json"), "w", encoding="utf-8") as f:
                json.dump(item["meta"], f, indent=2)
        print_status(f"Downloaded: {folder}", success=True)

def find_project_root():
    current = os.getcwd()
    while current != os.path.dirname(current):
        if os.path.isdir(os.path.join(current, ".devcontainer")):
            return current
        current = os.path.dirname(current)
    return os.getcwd()
