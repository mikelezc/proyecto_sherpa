#!/bin/bash

# =============================================================================
# PROYECTO SHERPA - TESTS LAUNCHER
# Quick access to the tests directory
# =============================================================================

echo "🧪 Launching Proyecto Sherpa Tests & Demos Hub..."
echo ""

cd "$(dirname "$0")/tests" && ./run_tests.sh