#!/usr/bin/env bash
# This script is designed to be run from the root of the mcp-logger-utils project.
set -euo pipefail

echo "--- Cleaning up old builds from $(pwd) ---"
# Remove old build directories to ensure we only upload the new version
rm -rf dist/
rm -rf build/
# A more robust way to remove the .egg-info directory
find . -name "*.egg-info" -type d -exec rm -rf {} +

echo "--- Building new mcp-logger-utils package ---"
# This will build the package in the current directory
python -m build

echo "--- Uploading to PyPI ---"
# The wildcard uploads the .tar.gz and .whl files we just created
#twine upload "$@" dist/*

twine upload --verbose -u __token__ -p pypi-AgEIcHlwaS5vcmcCJDAyOWZhZDQ5LTY5ODUtNDNiZi05ZWJkLWRhNzQzYjhjMjcwZQACKlszLCJmNmY3YWJmNC01ZjQ4LTQwZWUtODE4MC0xZDM2MDQ0MTRiNzciXQAABiDoJLzJWR6CqIIprAkbhrj6dXjxDP4CZkUB77-OgdEVTQ dist/* 

