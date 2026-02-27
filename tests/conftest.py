from __future__ import annotations

import sys
from pathlib import Path
import importlib.util

# Ensure repo root is importable so tests can resolve top-level modules (core, ops, release, platform)
ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

# Preload local platform package to avoid stdlib name collision
platform_init = ROOT / "platform" / "__init__.py"
if platform_init.exists():
    spec = importlib.util.spec_from_file_location(
        "platform", platform_init, submodule_search_locations=[str(platform_init.parent)]
    )
    platform_module = importlib.util.module_from_spec(spec)
    if spec.loader:
        spec.loader.exec_module(platform_module)
        sys.modules["platform"] = platform_module
