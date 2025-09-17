import os
import json
import requests
from datetime import datetime
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

    print("Step 1/4: Running unit tests...")
    test_result = run_tests()
    if test_result is None:
        print("❌ Unit tests failed or could not be run. Aborting submit.")
        return
    print(" Unit tests completed.")

    print("Step 2/4: Saving test results...")
    os.makedirs(".jasper", exist_ok=True)
    try:
        with open(".jasper/tests.json", "w", encoding="utf-8") as f:
            json.dump(test_result, f, indent=2)
    except Exception as e:
        print(f"❌ Could not save test results: {e}")
        return
    print(" Test results saved.")

    print("Step 3/4: Running critique...")
    critique_result = run_critique(print_crit=False)
    if critique_result is None:
        print("❌ Critique step failed. Aborting submit.")
        return
    print(" Critique completed.")

    print("Step 4/4: Packaging and submitting to server...")
    try:
        zip_path = zip_folder(".")
        with open(zip_path, "rb") as f:
            files = {"file": f}
            data = {
                "student_id": student_id,
                "problem_id": problem_id,
                "grade": critique_result.get("grade", 0),
                "passed": test_result.get("passed", False)
            }
            res = requests.post(f"{server_url}/submit", data=data, files=files)
            res.raise_for_status()
    except requests.RequestException as e:
        print(f"❌ Error contacting server: {e}")
        return
    except Exception as e:
        print(f"❌ Packaging or submission failed: {e}")
        return

    # --- Only here if all steps pass ---
    submission_path = os.path.join(os.getcwd(), "SUBMISSION")
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    try:
        with open(submission_path, "w", encoding="utf-8") as f:
            f.write(f"Problem {problem_id} was last received at {timestamp}\n")
        print(f"📄 Wrote SUBMISSION file: {submission_path}")
    except Exception as e:
        print(f"⚠️ Could not write SUBMISSION file: {e}")

    print("🎉 Submission complete!")

def register(subparsers):
    parser = subparsers.add_parser("submit", help="Submit solution for grading")
    parser.set_defaults(func=run)
