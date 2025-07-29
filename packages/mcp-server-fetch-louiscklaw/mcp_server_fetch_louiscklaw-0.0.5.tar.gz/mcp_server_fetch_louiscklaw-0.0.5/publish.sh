#!/usr/bin/env bash

set -ex

# uv version 0.0.1
# uv version --bump minor

rm -rf dist/*.tar.gz
rm -rf dist/*.whl

uv build

uv publish

echo "done"

