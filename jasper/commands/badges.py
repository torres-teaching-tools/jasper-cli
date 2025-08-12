import requests
from jasper.utils import load_config

def register(subparsers):
    parser = subparsers.add_parser("badges", help="Show earned badges and grades")
    parser.set_defaults(func=run)

def run(args):
    config = load_config()
    student_id = config.get("student_id", "testuser")
    server_url = config.get("server_url", "http://localhost:3000")
    try:
        res = requests.get(f"{server_url}/badges", params={"student_id": student_id})
        print(f"--- BADGES DASHBOARD for student {student_id} ---")
        data = res.json()
        print(f"🏅 Badges earned: {data.get('badges_earned', 0)}")
        print(f"🎖️ Badge types: {', '.join(data.get('badges', []))}")
        print()
        for item in data.get("breakdown", []):
            print(f"[{item['badge']}] {item['title']} (Problem {item['problem_id']})")
            print(f"    Test Score: {item['test_score']}, Critique Score: {item['critique_score']}")
            print(f"    Checks: {item['check_count']}, Critiques: {item['critique_count']}")
            print()
    except Exception as e:
        print("❌ Error fetching dashboard:", e)
