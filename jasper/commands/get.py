import os, requests, json, shutil
from jasper.utils import load_config, save_config
from jasper.pretty import print_status

def register(subparsers):
    parser = subparsers.add_parser("get", help="Download starter code for a problem")
    parser.add_argument("query", help="Problem name or ID")
    parser.set_defaults(func=run)
    
def clear_directory_contents(path):
    for entry in os.listdir(path):
        full_path = os.path.join(path, entry)
        if os.path.isfile(full_path) or os.path.islink(full_path):
            os.unlink(full_path)  # delete file or symlink
        elif os.path.isdir(full_path):
            shutil.rmtree(full_path)

def run(args):
    config = load_config()
    server_url = config.get("server_url", "http://localhost:3000")

    try:
        resp = requests.get(f"{server_url}/get-problem", params={"q": args.query})
        if resp.status_code != 200:
            print_status(f"Problem not found: {args.query}", success=False)
            return

        data = resp.json()
        folder_name = data["project_name"]

        # Find project root by locating `.devcontainer`
        root_dir = find_project_root()
        project_path = os.path.join(root_dir, folder_name)

        # Check if folder exists and get confirmation
        if os.path.exists(project_path):
            print_status(f"⚠️ Folder '{folder_name}' already exists.", success=False)
            confirm = input(f"Type 'yes' to overwrite ALL files in '{folder_name}': ").strip().lower()
            if confirm != "yes":
                print_status("Download cancelled by user.", success=False)
                return

            clear_directory_contents(project_path)
            print_status(f"🧹 Cleared contents of '{folder_name}'", success=True)

        os.makedirs(project_path, exist_ok=True)


        # Save starter files
        for fname, content in data["files"].items():
            fpath = os.path.join(project_path, fname)
            os.makedirs(os.path.dirname(fpath), exist_ok=True)
            with open(fpath, "w") as f:
                f.write(content)

        # Save meta.json if provided
        if "meta" in data:
            meta_path = os.path.join(project_path, "meta.json")
            with open(meta_path, "w") as f:
                json.dump(data["meta"], f, indent=2)

        print_status(f"Downloaded: {folder_name}", success=True)

    except Exception as e:
        print_status(f"Error: {e}", success=False)


def find_project_root():
    """
    Traverse upward until we find the folder containing `.devcontainer`.
    Defaults to current working directory if not found.
    """
    current = os.getcwd()
    while current != os.path.dirname(current):
        if os.path.isdir(os.path.join(current, ".devcontainer")):
            return current
        current = os.path.dirname(current)
    return os.getcwd()
