import os
import json
import requests
from jasper.utils import load_config, zip_folder
from jasper.commands.check import run_tests
from jasper.commands.crit import run_critique

def run(args):
    print("🚀 Submitting...")

    config = load_config()
    folder_name = os.path.basename(os.getcwd())

    if "-" not in folder_name:
        print("❌ Folder name must follow the format `132-hello-world`.")
        return

    problem_id = folder_name.split("-")[0]
    student_id = config.get("student_id", "testuser")
    server_url = config.get("server_url", "http://localhost:3000")

    print("🔍 Step 1/4: Running unit tests...")
    test_result = run_tests()
    if test_result is None:
        print("❌ Unit tests failed or could not be run. Aborting submit.")
        return
    print("✅ Unit tests completed.")

    print("💾 Step 2/4: Saving test results...")
    os.makedirs(".jasper", exist_ok=True)
    with open(".jasper/tests.json", "w") as f:
        json.dump(test_result, f, indent=2)
    print("✅ Test results saved.")

    print("🧠 Step 3/4: Running critique...")
    critique_result = run_critique()
    if critique_result is None:
        print("❌ Critique step failed. Aborting submit.")
        return
    print("✅ Critique completed.")

    print("📦 Step 4/4: Packaging and submitting to server...")
    zip_path = zip_folder(".")

    try:
        
        with open(zip_path, "rb") as f:
            files = {"file": f}
            data = {
                "student_id": student_id,
                "problem_id": problem_id,
                "grade": critique_result.get("grade", 0),
                "passed": test_result.get("passed", False)
            }
            res = requests.post(f"{server_url}/submit", data=data, files=files)
            print("--- SUBMIT ---")
            print("Status:", res.status_code)
            print(res.json())
            print("🎉 Submission complete!")
    except Exception as e:
        print("❌ Error contacting server:", e)

def register(subparsers):
    parser = subparsers.add_parser("submit", help="Submit solution for grading")
    parser.set_defaults(func=run)
