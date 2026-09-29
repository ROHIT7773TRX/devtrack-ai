# ============================================================
# tests/conftest.py
# pytest configuration file — shared fixtures available to ALL tests.
#
# pytest automatically discovers this file and makes all fixtures
# defined here available without importing them in test files.
# ============================================================

import sys
import os

# Add backend to Python path so test files can import backend modules
# (main, models, schemas, database, routers)
# This is needed because our test files are in tests/ but the source
# is in app/backend/ — Python wouldn't find them without this.
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../app/backend"))
