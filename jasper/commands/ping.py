import requests

from jasper.utils import load_config
from jasper.pretty import print_status


def register(subparsers):
    parser = subparsers.add_parser(
        "ping",
        help="Check whether the grading server is reachable (Mongo-backed liveness when available)",
    )
    parser.set_defaults(func=run)


def run(args):
    try:
        cfg = load_config()
    except FileNotFoundError as e:
        return print_status(str(e), success=False)

    server_url = cfg.get("server_url", "http://localhost:3000").rstrip("/")
    url = f"{server_url}/ping"

    try:
        resp = requests.get(url, timeout=10)
    except requests.exceptions.Timeout:
        return print_status("Request timed out. Is the server reachable?", success=False)
    except requests.exceptions.ConnectionError:
        return print_status("Cannot connect. Check server URL or network.", success=False)
    except Exception as e:
        return print_status(f"Unexpected network error: {e}", success=False)

    if resp.status_code == 404:
        return print_status(
            "HTTP 404: nothing is registered at /ping on this server. "
            "The CLI uses the same base URL as `jasper history` (…/ping). "
            "Deploy a /ping route on the grader, or register it under the path your app actually uses.",
            success=False,
        )

    try:
        body = resp.json()
    except ValueError:
        print_status(
            f"Invalid response from server (not JSON), HTTP {resp.status_code}.",
            success=False,
        )
        print(resp.text[:2000])
        return

    message = body.get("message", "")
    service = body.get("service", "")
    ok = body.get("ok") is True

    if service:
        print_status(f"{service}: {message}", success=ok)
    else:
        print_status(message or f"HTTP {resp.status_code}", success=ok)
