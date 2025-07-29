import pytest
from dshake.dependency import (
    _parse_single_line,
    _get_visual_depth,
    _extract_tree_blocks,
    get_dependency_tree,
    _get_poetry_venv_dependency_tree,
    _get_uv_venv_dependency_tree,
)
from unittest.mock import patch, MagicMock

def test_parse_single_line_detects_internal_package():
    line = "├── my-company-lib 1.2.3"
    pkg = _parse_single_line(line, "my-company")
    assert pkg.name == "my-company-lib"
    assert pkg.version == "1.2.3"
    assert pkg.to_unfold is True

def test_parse_single_line_detects_external_package():
    line = "│   └── urllib3 1.26.5"
    pkg = _parse_single_line(line, "my-company")
    assert pkg.name == "urllib3"
    assert pkg.version == "1.26.5"
    assert pkg.to_unfold is False

def test_get_visual_depth():
    assert _get_visual_depth("├── foo") == 1
    assert _get_visual_depth("│   └── bar") == 2
    assert _get_visual_depth("    └── baz") == 1

def test_extract_tree_blocks_simple():
    lines = [
        "my-company 1.0.0",
        "├── lib-a 2.0.0",
        "└── lib-b 3.1.1"
    ]
    pkgs = _extract_tree_blocks(lines, "my-company")
    assert len(pkgs) == 1
    assert pkgs[0].name == "my-company"
    assert len(pkgs[0].imports) == 2
    assert pkgs[0].imports[0].name == "lib-a"
    assert pkgs[0].imports[1].name == "lib-b"

@patch("dshake.dependency.subprocess.run")
def test_get_poetry_venv_dependency_tree(mock_run):
    mock_run.return_value = MagicMock(stdout="""
my-company 1.0.0
├── lib-a 2.0.0
│   └── lib-a-sub 1.1.1
└── lib-b 3.0.0
""")
    result = _get_poetry_venv_dependency_tree("my-company")
    assert len(result) == 1
    assert result[0].name == "my-company"
    assert result[0].imports[0].name == "lib-a"
    assert result[0].imports[0].imports == 0  # lib-a-sub should not be listed because it does not come from my-company

@patch("dshake.dependency.subprocess.run")
def test_get_poetry_venv_dependency_tree(mock_run):
    mock_run.return_value = MagicMock(stdout="""
mycompany 1.0.0
├── mycompany-a 2.0.0
│   └── lib-a-sub 1.1.1
└── mycompany-b 3.0.0
""")
    result = _get_poetry_venv_dependency_tree("mycompany")
    assert len(result) == 1
    assert result[0].name == "mycompany"
    assert result[0].imports[0].name == "mycompany-a"
    assert result[0].imports[0].imports[0].name == "lib-a-sub"

@patch("dshake.dependency.subprocess.run")
def test_get_uv_venv_dependency_tree(mock_run):
    mock_run.return_value = MagicMock(stdout="""
my-company 1.0.0
└── lib-c 4.0.0
""")
    result = _get_uv_venv_dependency_tree("my-company")
    assert result[0].name == "my-company"
    assert result[0].imports[0].name == "lib-c"

def test_get_dependency_tree_invalid():
    with pytest.raises(ValueError):
        get_dependency_tree("foo", dependency_manager="invalid")