import ast

import pytest
from pathlib import Path
import tempfile
import os
from dshake.module_import import (
    ImportCollector,
    _collect_immediate_imports_from_file,
    _module_to_unfold,
    _resolve_module_to_path,
)
from unittest.mock import patch, MagicMock

# --- ImportCollector ---

def test_import_collector_basic():
    code = "import os\nimport sys\nfrom math import sqrt"
    tree = ast.parse(code, filename="<string>", mode="exec")
    collector = ImportCollector(None)
    collector.visit(tree)
    assert "os" in collector.imports
    assert "sys" in collector.imports
    assert "math" in collector.imports

def test_import_collector_relative_import():
    code = "from ..utils import something"
    tree = ast.parse(code, filename="<string>", mode="exec")
    collector = ImportCollector("my.pkg.module")
    collector.visit(tree)
    assert "my.utils" in collector.imports

def test_import_collector_raises_on_relative_import_without_module():
    code = "from ..utils import something"
    tree = ast.parse(code, filename="<string>", mode="exec")
    collector = ImportCollector(None)
    with pytest.raises(ValueError):
        collector.visit(tree)

# --- _collect_immediate_imports_from_file ---

def test_collect_immediate_imports_from_file():
    with tempfile.NamedTemporaryFile("w", suffix=".py", delete=False) as f:
        f.write("import os\nfrom sys import path\n")
        f_path = Path(f.name)
    imports = _collect_immediate_imports_from_file(f_path, None)
    os.unlink(f_path)  # Clean up
    assert "os" in imports
    assert "sys" in imports

# --- _module_to_unfold ---

@pytest.mark.parametrize("mod,target,expected", [
    ("a.b.c", "a.b", True),
    ("a.b", "a.b", True),
    ("a.b.c", "a", True),
    ("x.y", "z", False),
    ("x", None, False),
])
def test_module_to_unfold(mod, target, expected):
    from dshake.module_import import _module_to_unfold
    assert _module_to_unfold(mod, target) == expected

# --- _resolve_module_to_path (mocked _get_site_packages_location) ---

@patch("dshake.module_import._get_site_packages_location")
def test_resolve_module_to_path_from_src(mock_site):
    with tempfile.TemporaryDirectory() as tempdir:
        src_dir = Path(tempdir) / "src"
        src_dir.mkdir()
        test_file = src_dir / "my_mod.py"
        test_file.write_text("import os")

        mock_site.return_value = Path("/fake/site-packages")

        result = _resolve_module_to_path("my_mod", src_dir=src_dir)
        assert len(result) == 1
        assert result[0].name == "my_mod.py"
