import requests

from jasper.utils import load_config
from jasper.pretty import print_status, show_table


def _format_timestamp(value):
    if value is None or value == "":
        return "—"
    return str(value).strip() or "—"


def run(args):
    try:
        config = load_config()
    except FileNotFoundError as e:
        return print_status(str(e), success=False)

    student_id = config.get("student_id", "testuser")
    server_url = config.get("server_url", "http://localhost:3000").rstrip("/")
    url = f"{server_url}/history"

    try:
        resp = requests.post(
            url,
            json={"student_id": student_id},
            headers={"Content-Type": "application/json"},
            timeout=20,
        )
    except requests.exceptions.ConnectTimeout:
        return print_status("Connection timed out. Is the server reachable?", success=False)
    except requests.exceptions.ConnectionError:
        return print_status("Cannot connect. Check server URL or network.", success=False)
    except requests.RequestException as e:
        return print_status(f"Error contacting server: {e}", success=False)

    if resp.status_code == 400:
        try:
            detail = resp.json().get("error", resp.text or "Bad request")
        except ValueError:
            detail = resp.text or "Bad request"
        return print_status(str(detail), success=False)
    if resp.status_code >= 500:
        return print_status("Server error. Try again later or contact the instructor.", success=False)
    if resp.status_code != 200:
        return print_status(f"Unexpected status {resp.status_code}.", success=False)

    try:
        data = resp.json()
    except ValueError:
        return print_status("Invalid response from server (not JSON).", success=False)

    problems = data.get("problems") or []
    sid = data.get("student_id", student_id)

    if not problems:
        print_status(f"No graded problems on record for {sid}.", success=True)
        return

    rows = []
    for p in problems:
        completed = p.get("status") == "completed"
        rows.append(
            {
                "module": p.get("module") or "",
                "problem_id": p.get("problem_id") or "",
                "name": p.get("problem_name") or "",
                "status": p.get("status") or "",
                "submitted": _format_timestamp(p.get("timestamp")) if completed else "—",
                "score": (
                    f"{p.get('server_grade', 0)}/{p.get('server_grade_possible', 0)}"
                    if completed
                    else "—"
                ),
            }
        )

    print_status(f"Problem history for {sid}", success=True)
    show_table(rows, title="Problems")


def register(subparsers):
    parser = subparsers.add_parser(
        "history",
        help="Show your problem history from the grading server",
    )
    parser.set_defaults(func=run)
