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
    os.makedirs(".jasper", exist_ok=True)
    with open(".jasper/check.json", "w") as f:
        json.dump(result, f, indent=2)

    if "error" in result:
        print("❌ Error during check:")
        print(result["error"])
        print("Status code:", result.get("status_code"))
        print("Response text:", result.get("response_text"))
        if result.get("status_code") == 401:
            print("🔒 Authentication error: Please check your student ID or server permissions.")
        return

    title = format_text("Unit Test Results:", bold=True, underline=True)
    print(title)
    total_points = 0
    earned_points = 0
    for test in result.get("tests", []):
        status = "✅" if test["passed"] else "❌"
        points = test.get("points", 0)
        total_points += points
        if test["passed"]:
            earned_points += points
        print(f"{status} {test['test']} | Type: {test.get('type', 'N/A')} | Points: {points}")
        print(f"    Expected: {test.get('expected')}")
        print(f"    Actual:   {test.get('actual')}")
    print(f"\n🏅 Score: {earned_points}/{total_points} points")
    print(f"Overall result: {'✅ Passed' if result.get('passed') else '❌ Failed'}")

    if final:
        print("\n💾 Stored final submission result.")
