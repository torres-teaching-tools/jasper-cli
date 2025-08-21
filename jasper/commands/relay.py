# jasper/commands/relay.py
import os
import requests
from jasper.utils import load_config, zip_folder
from jasper.pretty import print_status

def register(subparsers):
    p = subparsers.add_parser("relay", help="Send your files to the instructor/TA for review (no grading)")
    p.set_defaults(func=run)

def run(args):
    cfg = load_config()
    folder_name = os.path.basename(os.getcwd())
    if "-" not in folder_name:
        return print_status("Folder name must follow the format `132-hello-world`.", success=False)

    problem_id = folder_name.split("-")[0]
    student_id = cfg.get("student_id", "testuser")
    server_url = cfg.get("server_url", "http://localhost:3000")

    print("📨 Packaging files for relay...")
    try:
        zip_path = zip_folder(".")
    except Exception as e:
        return print_status(f"Could not package folder: {e}", success=False)

    print("🚚 Uploading to instructor relay inbox...")
    try:
        with open(zip_path, "rb") as f:
            files = {"file": ("submission.zip", f, "application/zip")}
            data = {"student_id": student_id, "problem_id": problem_id}
            res = requests.post(f"{server_url}/relay", data=data, files=files, timeout=60)
            if res.status_code != 200:
                return print_status(f"Server error ({res.status_code}): {res.text}", success=False)
            info = res.json()
            print_status(f"Relay sent ✔ (seq {info.get('relay_seq')})", success=True)
            print(f"Server saved at: {info.get('saved_to')}")
    except requests.exceptions.RequestException as e:
        return print_status(f"Network error: {e}", success=False)
