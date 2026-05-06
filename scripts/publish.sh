#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT_DIR"

VERSION="$(python - <<'PY'
import tomllib
from pathlib import Path
with Path('pyproject.toml').open('rb') as f:
    print(tomllib.load(f)['project']['version'])
PY
)"
TAG="v${VERSION}"
BRANCH="$(git branch --show-current)"

if [[ -z "$BRANCH" ]]; then
  echo "Could not determine current branch." >&2
  exit 1
fi

if [[ -n "$(git status --porcelain)" ]]; then
  echo "Working tree is not clean. Commit or stash changes first." >&2
  git status --short
  exit 1
fi

if git rev-parse "$TAG" >/dev/null 2>&1; then
  echo "Tag $TAG already exists locally." >&2
  exit 1
fi

if git ls-remote --exit-code --tags origin "refs/tags/$TAG" >/dev/null 2>&1; then
  echo "Tag $TAG already exists on origin." >&2
  exit 1
fi

echo "Building package for $TAG..."
uv build

echo "Pushing $BRANCH..."
git push origin "$BRANCH"

echo "Creating and pushing tag $TAG..."
git tag -a "$TAG" -m "Release $TAG"
git push origin "$TAG"

echo "Done. GitHub Actions will create the release and publish the package."
