#!/usr/bin/env python3
"""
Convenient script to generate Pydantic models from YAML schemas.

Usage:
    python generate_schemas.py                    # Generate with defaults
    python generate_schemas.py --watch           # Watch for changes
    python generate_schemas.py --verbose         # Verbose output
"""


# Import after path modification
from agentbx.schemas.generator import main  # noqa: E402


if __name__ == "__main__":
    exit(main())  # type: ignore
