# ---- Maintainer Makefile (jasper-cli repo) ----
PACKAGE ?= jasper-cli
VERSION_FILE ?= pyproject.toml
REPO ?= torres-teaching-tools/jasper-cli
SPEC ?= git+https://github.com/$(REPO)@main

.PHONY: clean build force-install dev dev-uninstall push tag release check

clean:
	rm -rf dist build *.egg-info

build: clean
	python -m pip install --upgrade build >/dev/null
	python -m build
	@echo "Built wheel(s):"; ls -1 dist/*.whl

# Quickly test the *built wheel* in your pipx venv
force-install: build
	pipx install --force dist/*.whl
	@echo "jasper path:" && command -v jasper
	@jasper --help || true

# Editable install workflow (handy for rapid dev)
dev:
	python -m venv .venv && . .venv/bin/activate && pip install -e . && echo "Activated .venv; run: . .venv/bin/activate"

dev-uninstall:
	@if [ -d .venv ]; then . .venv/bin/activate && pip uninstall -y $(PACKAGE) || true; fi

# Publish changes so students can upgrade (GitHub flow)
push:
	git add .
	git commit -m "update $(PACKAGE)" || true
	git push origin main

# Tag using version from pyproject.toml (for pinned installs)
tag:
	@V=$$(grep -m1 '^version\s*=' $(VERSION_FILE) | sed 's/.*"\(.*\)".*/\1/'); \
	echo "Tagging v$$V"; \
	git tag v$$V && git push origin v$$V

# Optional: PyPI release (if you choose to use PyPI later)
release: build
	python -m pip install --upgrade twine >/dev/null
	twine upload dist/*

# Smoke check that commands subpackage exists in built wheel
check: build
	python - <<'PY'
	import glob, zipfile
	w = glob.glob('dist/*.whl')[0]
	with zipfile.ZipFile(w) as z:
		cmds = [p for p in z.namelist() if p.startswith('jasper/commands/')]
	print("commands packaged:", bool(cmds), f"({len(cmds)} files)")
	PY
