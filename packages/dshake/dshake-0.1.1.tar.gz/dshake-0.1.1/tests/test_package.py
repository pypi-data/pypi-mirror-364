import pytest
from pathlib import Path
from dshake.data_model import ImportInfo
from dshake.package import _get_flat_imports, analyze_package_usages
from unittest.mock import patch, MagicMock

# --------------------
# TEST: _get_flat_imports
# --------------------
def test_get_flat_imports_flattened():
    # Simulate an import tree
    a = ImportInfo(name="a", path=None, to_unfold=True)
    b = ImportInfo(name="a.b", path=None, to_unfold=False)
    c = ImportInfo(name="a.b.c", path=None, to_unfold=False)
    d = ImportInfo(name="d", path=None, to_unfold=False)
    a.add_import(b)
    b.add_import(c)
    a.add_import(d)

    flat = _get_flat_imports([a])
    assert flat == {"a", "a.b", "a.b.c", "d"}

# --------------------
# TEST: analyze_package_usages
# --------------------
@patch("dshake.package.get_import_tree")
@patch("dshake.package.glob.glob")
@patch("dshake.package._get_site_packages_location")
def test_analyze_package_usages(mock_site_path, mock_glob, mock_get_import_tree, tmp_path):
    # Mock file discovery in src
    fake_file = tmp_path / "main.py"
    fake_file.write_text("import os")

    mock_glob.side_effect = [
        [str(fake_file)],  # glob for .py files
        [str(tmp_path / "fakepkg-1.2.3.dist-info")]  # glob for dist-info dirs
    ]

    # Mock import tree result
    mock_get_import_tree.return_value = [
        ImportInfo(name="fakepkg.submod", path=None, to_unfold=False)
    ]

    # Mock site-packages path
    mock_site_path.return_value = tmp_path

    # Create fake RECORD file
    dist_info_dir = tmp_path / "fakepkg-1.2.3.dist-info"
    dist_info_dir.mkdir()
    record = dist_info_dir / "RECORD"
    record.write_text("fakepkg/submod.py,\n")

    result = analyze_package_usages(
        src_dir=tmp_path,
        namespace="my-company"
    )

    assert "fakepkg==1.2.3" in result["used_packages_with_deps"]
    assert result["used_packages_no_deps"] == set()
