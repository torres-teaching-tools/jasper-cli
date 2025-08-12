import os
import json
import requests
from jasper.utils import load_config, zip_folder

def run_critique(args=None):
    config = load_config()

    folder_name = os.path.basename(os.getcwd())
    if "-" not in folder_name:
        print("❌ Folder name must follow the format `132-hello-world`.")
        return None

    problem_id = folder_name.split("-")[0]
    student_id = config.get("student_id", "testuser")
    server_url = config.get("server_url", "http://localhost:3000")

    zip_path = zip_folder(".")

    try:
        with open(zip_path, "rb") as f:
            files = {"file": f}
            data = {"student_id": student_id, "problem_id": problem_id}
            response = requests.post(f"{server_url}/crit", data=data, files=files)

        if response.status_code != 200:
            print(f"❌ Critique failed ({response.status_code}):\n{response.text}")
            return None

        result = response.json()
        os.makedirs(".jasper", exist_ok=True)

        # Save JSON
        with open(".jasper/critique.json", "w") as f:
            json.dump(result, f, indent=2)

        # Extract values safely
        grade = result.get("grade", "N/A")
        critique_text = result.get("critique", "No critique found.")

        # Save Markdown
        with open(".jasper/critique.md", "w") as f:
            f.write("# AI Code Review\n\n")
            f.write(f"**Grade**: {grade}/100\n\n")
            f.write(critique_text.strip() + "\n")

        # Print summary
        print("💬 AI Feedback:")
        print(critique_text)
        print("\n📄 Saved to `.jasper/critique.md`")

        return result

    except Exception as e:
        print(f"❌ Critique error: {e}")
        return None

def register(subparsers):
    parser = subparsers.add_parser("crit", help="Generate a code review")
    parser.set_defaults(func=run_critique)
