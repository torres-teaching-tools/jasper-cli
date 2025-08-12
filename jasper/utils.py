import os
import json
import zipfile

DEBUG = False  # Set to True to enable debug output

def debug_print(msg):
    if DEBUG:
        print(msg)

def find_config_path():
    dir_path = os.getcwd()
    debug_print(f"🔍 Starting config search from: {dir_path}")

    while True:
        candidate = os.path.join(dir_path, "jasper", "config.json")
        debug_print(f"🔎 Checking: {candidate}")
        if os.path.exists(candidate):
            debug_print(f"✅ Found config at: {candidate}")
            return candidate

        parent = os.path.dirname(dir_path)
        if parent == dir_path:
            debug_print("❌ Reached root. config.json not found.")
            break
        dir_path = parent

    raise FileNotFoundError("❌ Missing config.json. Use `jasper init` first.")

try:
    CONFIG_PATH = find_config_path()
except FileNotFoundError as e:
    CONFIG_PATH = None
    debug_print(str(e))

def load_config():
    try:
        start_path = os.getcwd()
    except FileNotFoundError:
        raise FileNotFoundError("❌ Current working directory is invalid. Move to an existing folder and try again.")

    debug_print(f"🔍 Starting config search from: {start_path}")
    dir_path = start_path
    while True:
        config_path = os.path.join(dir_path, "jasper", "config.json")
        debug_print(f"🔎 Checking: {config_path}")
        if os.path.exists(config_path):
            debug_print(f"✅ Found config at: {config_path}")
            with open(config_path) as f:
                return json.load(f)

        parent = os.path.dirname(dir_path)
        if parent == dir_path:
            break
        dir_path = parent

    raise FileNotFoundError("❌ Missing config.json. Use `jasper init` first.")

def _default_config_path():
    # New default when none exists yet (fixes circular save)
    return os.path.join(os.getcwd(), "jasper", "config.json")

def save_config(data):
    # If we already located a config, overwrite it; else write to repo-local default.
    path = CONFIG_PATH if CONFIG_PATH else _default_config_path()
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w") as f:
        json.dump(data, f, indent=2)
    debug_print(f"✅ Saved config to {path}")
    return path

def zip_folder(folder_path):
    zip_path = f"/tmp/{os.path.basename(folder_path)}.zip"
    debug_print(f"📦 Zipping folder {folder_path} -> {zip_path}")
    with zipfile.ZipFile(zip_path, "w") as zipf:
        for root, _, files in os.walk(folder_path):
            for file in files:
                full_path = os.path.join(root, file)
                arcname = os.path.relpath(full_path, folder_path)
                zipf.write(full_path, arcname)
    return zip_path

def format_text(text, bold=False, underline=False, color=None):
    """
    Format text with ANSI escape codes.

    Args:
        text (str): The text to format.
        bold (bool): Apply bold style.
        underline (bool): Apply underline style.
        color (str): Optional color name. Supported: black, red, green, yellow, blue, magenta, cyan, white.

    Returns:
        str: Formatted text with ANSI escape codes.
    """
    styles = []
    colors = {
        "black": 30, "red": 31, "green": 32, "yellow": 33,
        "blue": 34, "magenta": 35, "cyan": 36, "white": 37
    }

    if bold:
        styles.append("1")
    if underline:
        styles.append("4")
    if color and color.lower() in colors:
        styles.append(str(colors[color.lower()]))

    if styles:
        return f"\033[{';'.join(styles)}m{text}\033[0m"
    return text
