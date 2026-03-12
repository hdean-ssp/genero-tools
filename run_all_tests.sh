#!/bin/bash
# Wrapper for running all tests
# Delegates to tests/run_all_tests.sh

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
exec bash "$SCRIPT_DIR/tests/run_all_tests.sh" "$@"
