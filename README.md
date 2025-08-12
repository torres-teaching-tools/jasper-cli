# jasper-cli

# Edit your jasper-cli code in the repo
make force-install
# This rebuilds the wheel and forces pipx to use the new one
jasper --help      # or test the command you changed

make push

# Update version in pyproject.toml (e.g., 0.1.3)
make tag

