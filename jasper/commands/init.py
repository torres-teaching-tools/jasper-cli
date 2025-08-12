import re
from urllib import request, error

from jasper.utils import save_config, load_config
from jasper.pretty import print_status, show_table

CODENAME_REGEX = re.compile(r'^[a-z]+-[a-z]+-\d+$')  # adjective-noun-number

def register(subparsers):
    parser = subparsers.add_parser("init", help="Initialize jasper CLI with your info")
    parser.set_defaults(func=run)

def _prompt_yes_no(msg, default="n"):
    choice = input(f"{msg} [{'Y' if default.lower()=='y' else 'y'}/"
                   f"{'N' if default.lower()=='n' else 'n'}]: ").strip().lower()
    if not choice:
        choice = default.lower()
    return choice in ("y", "yes")

def _normalize_url(u: str) -> str:
    u = (u or "").strip()
    if not u:
        return "http://localhost:3000"
    if not u.startswith(("http://", "https://")):
        u = "http://" + u
    return u.rstrip("/")

def _ping_server(base_url: str, timeout: float = 4.0):
    url = f"{base_url}/api/healthz"
    try:
        req = request.Request(url, method="GET")
        with request.urlopen(req, timeout=timeout) as resp:
            return (200 <= resp.status < 300), None
    except error.HTTPError as e:
        return False, f"HTTP {e.code}"
    except Exception as e:
        return False, str(e)

def run(args):
    # 1) If a config exists, show it and prompt to overwrite
    existing = None
    try:
        existing = load_config()
    except Exception:
        existing = None

    if existing:
        print_status("Existing configuration detected:", success=True)
        show_table(
            [{
                "student_id": existing.get("student_id", ""),
                "server_url": existing.get("server_url", "")
            }],
            title="Current jasper config"
        )
        if not _prompt_yes_no("Overwrite existing configuration?", default="n"):
            print_status("Init cancelled. Keeping existing configuration.", success=True)
            return

    # 2) Prompt for CLASS CODENAME (stored as student_id)
    print("\nPlease enter your CLASS CODENAME.")
    print("TA Shreyosi emailed a codename to your mavs.uta.edu account in the form adjective-noun-number.")
    while True:
        codename = input("Class codename (e.g., silly-cat-7): ").strip()
        if not CODENAME_REGEX.fullmatch(codename):
            print_status("Invalid format. Expected adjective-noun-number (e.g., silly-cat-7).", success=False)
            continue
        break

    # 3) Prompt for server URL and ping
    print("\nEnter the grading server URL (see the 'Hello Jasper' document for the correct URL).")
    raw = input("Server URL (default http://localhost:3000): ").strip()
    server_url = _normalize_url(raw if raw else "http://localhost:3000")

    print_status(f"Pinging server at {server_url}/api/healthz ...", success=True)
    ok, err = _ping_server(server_url)
    if not ok:
        print_status(f"Could not reach server: {err}", success=False)
        print_status("Init aborted. Verify the URL/network and try again.", success=False)
        return
    print_status("Server is reachable.", success=True)

    # 4) Save
    config = {"student_id": codename, "server_url": server_url}
    path = save_config(config)
    print_status(f"Config saved to {path}", success=True)
