import os, requests, json
from jasper.utils import load_config, zip_folder, format_text

def run_tests():
    config = load_config()
    folder_name = os.path.basename(os.getcwd())
    if "-" not in folder_name:
        raise ValueError("❌ Could not infer problem ID from folder name. Use format like `132-hello-world`.")
    problem_id = folder_name.split("-")[0]
    # if not os.path.exists("main.c"):
    #     raise FileNotFoundError("❌ Could not find main.c in the current folder.")
    zip_path = zip_folder(".")
    with open(zip_path, "rb") as f:
        files = {"file": f}
        data = {
            "student_id": config["student_id"],
            "problem_id": problem_id
        }
        response = requests.post(f"{config['server_url']}/check", data=data, files=files)
    try:
        # Print HTTP status for progress
        # print(f"🔗 Server responded with status: {response.status_code}")
        if response.status_code == 200:
            print("Server successfully compiled and tested your code.");
        else:
            print("❌ Server could not compile your code.\nMake sure ``make`` works locally before asking jasper to check again.\n --- LOG ---")
        return response.json()
    except Exception:
        print("❌ Server response was not valid JSON.")
        print("Status code:", response.status_code)
        print("Response text:", response.text)
        return {
            "passed": False,
            "error": "Could not decode server response.",
            "status_code": response.status_code,
            "response_text": response.text
        }

def register(subparsers):
    parser = subparsers.add_parser("check", help="Run only test cases")
    parser.set_defaults(func=lambda args: pretty_print(run_tests(), final=False))

def pretty_print(result, final):
    # persist raw result for debugging
    os.makedirs(".jasper", exist_ok=True)
    with open(".jasper/check.json", "w") as f:
        json.dump(result, f, indent=2)

    # server-side error path
    if "error" in result:
        print(format_text("❌ Error during check:", bold=True, color="red"))
        print(result["error"])
        print("Status code:", result.get("status_code"))
        print("Response text:", result.get("response_text"))
        if result.get("status_code") == 401:
            print("🔒 Authentication error: Please check your student ID or server permissions.")
        return

    # Support either 'tests' or 'test_results'
    tests = result.get("tests") or result.get("test_results") or []

    # Title
    print(format_text("Unit Test Results:", bold=True, underline=True))

    # Helpers
    def _nonempty(x):
        return x is not None and x != ""

    def _detail_for_check(t: dict) -> str:
        parts = []
        if "check" in t: parts.append(f"check={t['check']}")
        if "target" in t: parts.append(f"file={t['target']}")
        for k in ("comments_found", "min_required", "lines", "max_allowed"):
            if k in t: parts.append(f"{k}={t[k]}")
        return ", ".join(parts) if parts else "(no details)"

    def _expected_actual(t: dict) -> tuple[str, str]:
        typ = t.get("type")
        expected = t.get("expected")
        actual   = t.get("actual")

        # Provide sensible fallbacks for types without .out files
        if typ == "memory":
            if expected is None:
                expected = "(no expected file; pass = no leaks reported)"
            if actual is None:
                actual = t.get("valgrind_output") or "(no valgrind output)"
        elif typ == "check":
            if expected is None:
                expected = "(no expected file; check evaluates constraints)"
            if actual is None:
                actual = _detail_for_check(t)

        # Ensure strings
        expected = "" if expected is None else str(expected)
        actual   = "" if actual is None else str(actual)
        return expected, actual

    def _content_for_passed(t: dict) -> str:
        # Prefer Actual, else Expected, else type-specific details
        act = t.get("actual")
        exp = t.get("expected")
        if _nonempty(act): return str(act)
        if _nonempty(exp): return str(exp)
        if t.get("type") == "memory":
            return str(t.get("valgrind_output") or "(no valgrind output)")
        if t.get("type") == "check":
            return _detail_for_check(t)
        return "(no output)"

    # Totals and partitions
    total_points = 0
    earned_points = 0
    passed_count = 0
    failed, passed = [], []

    for t in tests:
        pts = int(t.get("points", 0))
        total_points += pts
        if t.get("passed"):
            earned_points += pts
            passed_count += 1
            passed.append(t)
        else:
            failed.append(t)

    # 1) Failed tests (detailed, Expected/Actual)
    for t in failed:
        name = t.get("test", "unknown")
        typ  = t.get("type", "N/A")
        pts  = t.get("points", 0)
        header = f"❌ {name} | Type: {typ} | Points: {pts}"
        print(format_text(header, color="red"))
        expected, actual = _expected_actual(t)
        print(f"    Expected: {expected}")
        print(f"    Actual:   {actual}")

    # 2) Passed tests (compact, show only the output in green)
    for t in passed:
        name = t.get("test", "unknown")
        typ  = t.get("type", "N/A")
        pts  = t.get("points", 0)
        header = f"✅ {name} | Type: {typ} | Points: {pts}"
        body = _content_for_passed(t)
        print(format_text(header, color="green"))
        if body:
            for line in str(body).splitlines():
                print(format_text("    " + line, color="green"))

    # 3) Problem Score summary
    total_tests = len(tests)
    print()
    print(format_text("Problem Score:", bold=True))
    print(f"{passed_count}/{total_tests} tests passed")
    print(f"{earned_points}/{total_points} points")

    # Optional overall flag if server provides it
    if "passed" in result:
        print()
        print("Overall result:", format_text("✅ Passed", color="green") if result["passed"]
              else format_text("❌ Failed", color="red"))

    if final:
        print()
        print("💾 Stored final submission result.")

