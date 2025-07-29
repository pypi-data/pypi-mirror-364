from pathlib import Path
from dshake.data_model import ImportInfo, PackageInfo

def test_import_info_add_and_filter():
    root = ImportInfo(name="root", path=Path("main.py"), to_unfold=True)
    internal = ImportInfo(name="internal.module", path=Path("internal/module.py"), to_unfold=True)
    external = ImportInfo(name="external_lib", path=None, to_unfold=False)

    root.add_import(internal)
    root.add_import(external)

    internal_imports = root.get_internal_imports()
    external_imports = root.get_external_imports()

    assert len(internal_imports) == 1
    assert internal_imports[0].name == "internal.module"

    assert len(external_imports) == 1
    assert external_imports[0].name == "external_lib"


def test_package_info_creation():
    pkg = PackageInfo(name="my-lib", version="1.0.0", to_unfold=True)
    dep = PackageInfo(name="dep-lib", version="2.3.1", to_unfold=False)
    pkg.imports.append(dep)

    assert pkg.name == "my-lib"
    assert pkg.version == "1.0.0"
    assert pkg.imports[0].name == "dep-lib"
