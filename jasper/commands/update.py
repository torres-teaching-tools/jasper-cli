import os
import subprocess
import sys

from jasper.pretty import print_status

# Defaults mirror the maintainer Makefile (REPO / SPEC).
_DEFAULT_REPO = "torres-teaching-tools/jasper-cli"


def _install_spec():
    spec = (os.environ.get("SPEC") or "").strip()
    if spec:
        return spec
    repo = (os.environ.get("REPO") or "").strip()
    if repo:
        return f"git+https://github.com/{repo}@main"
    return f"git+https://github.com/{_DEFAULT_REPO}@main"


def register(subparsers):
    parser = subparsers.add_parser(
        "update",
        help="Upgrade jasper-cli with pipx (override SPEC or REPO env like the Makefile)",
    )
    parser.set_defaults(func=run)


def run(args):
    spec = _install_spec()
    cmd = ["pipx", "install", "--force", spec]

    print_status(f"Running: {' '.join(cmd)}", success=True)
    try:
        result = subprocess.run(cmd)
    except FileNotFoundError:
        print_status(
            "pipx not found on PATH. Install pipx: https://pipx.pypa.io/",
            success=False,
        )
        sys.exit(127)
    rc = result.returncode if result.returncode is not None else 1
    if rc != 0:
        print_status("pipx install failed.", success=False)
    sys.exit(rc)
