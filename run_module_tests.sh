#!/bin/bash
# Wrapper for running module tests
# Delegates to tests/run_module_tests.sh

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
exec bash "$SCRIPT_DIR/tests/run_module_tests.sh" "$@"
