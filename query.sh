#!/bin/bash
# Wrapper for querying the codebase databases
# Delegates to src/query.sh

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
bash "$SCRIPT_DIR/src/query.sh" "$@"
