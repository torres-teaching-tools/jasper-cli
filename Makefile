# ---- maintainer Makefile ----
PACKAGE=jasper-cli
VERSION_FILE=pyproject.toml

.PHONY: clean build install dev-run tag release force-install

clean:
	rm -rf dist build *.egg-info

build: clean
	python -m build
	@echo "Built wheel:"
	@ls -1 dist/*.whl

# local test in your dev box (pipx venv)
force-install: build
	pipx install --force dist/*.whl
	@echo "jasper path:" && command -v jasper
	@jasper --help || true

# Editable dev loop (optional)
dev:
	python -m venv .venv && . .venv/bin/activate && pip install -e . && echo "Run: . .venv/bin/activate"

# Tag current commit using version in pyproject.toml
tag:
	@V=$$(grep -m1 '^version\s*=' $(VERSION_FILE) | sed 's/.*=\s*"\(.*\)".*/\1/'); \
	echo "Tagging v$$V"; \
	git tag v$$V && git push origin v$$V

# PyPI release (requires TWINE_USERNAME / TWINE_PASSWORD or keyring)
release: build
	python -m pip install --upgrade twine
	twine upload dist/*

# Smoke test
dev-run:
	jasper --version || true
