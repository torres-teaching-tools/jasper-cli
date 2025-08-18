import importlib.metadata

def register(subparsers):
    parser = subparsers.add_parser("version", help="Show jasper CLI version")
    parser.set_defaults(func=run)

def run(args):
    try:
        version = importlib.metadata.version("jasper-cli")
        print(f"✨ jasper CLI version {version}")
    except importlib.metadata.PackageNotFoundError:
        print("❌ jasper-cli version not found. Did you run make jasper-install?")
