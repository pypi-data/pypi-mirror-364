import ast
import glob
from pathlib import Path

from dshake.data_model import ImportInfo
from dshake.utils import _get_site_packages_location


class ImportCollector(ast.NodeVisitor):
    def __init__(self, module_name: str | None):
        self.imports = set()
        self.module_name = module_name

    def visit_Import(self, node):
        for alias in node.names:
            self.imports.add(alias.name)
        self.generic_visit(node)

    def visit_ImportFrom(self, node):
        if node.module:
            if node.level != 0:
                if self.module_name is None:
                    raise ValueError("module_name cannot be None if this module uses relative import")
                tmp = self.module_name.split('.')[:-node.level]
                tmp.append(node.module)
                result = '.'.join(tmp)
                self.imports.add(result)
            else:
                self.imports.add(node.module)
        self.generic_visit(node)

def _collect_immediate_imports_from_file(file_path: Path, module_name: str | None) -> set[str]:
    with open(file_path, 'r', encoding='utf-8') as f:
        node = ast.parse(f.read(), filename=file_path)
    collector = ImportCollector(module_name)
    collector.visit(node)
    return collector.imports

def _path_to_module_name(file_path: Path) -> str:
    rel_path = file_path.relative_to(_get_site_packages_location())
    # Remove suffix and convert to dotted module name
    module_parts = rel_path.with_suffix('').parts
    return ".".join(module_parts)

def _module_to_unfold(module_name: str, module_to_unfold: str | None) -> bool:
    if module_to_unfold is None:
        return False
    return module_name == module_to_unfold or module_name.startswith(module_to_unfold + ".")

def _process_file(file_path: Path, module_to_unfold: str | None) -> ImportInfo:
    is_not_from_src = file_path.is_relative_to(_get_site_packages_location())

    if is_not_from_src:
        this_module_name = _path_to_module_name(file_path)
        this_module = ImportInfo(
            name = this_module_name,
            path = file_path,
            to_unfold = _module_to_unfold(this_module_name, module_to_unfold)
        )
        import_modules = _collect_immediate_imports_from_file(file_path, this_module_name)
    else:
        this_module = ImportInfo(
            name=None,
            path=file_path,
            to_unfold=True
        )
        import_modules = _collect_immediate_imports_from_file(file_path, None)

    if not this_module.to_unfold:
        return this_module

    for import_module in import_modules:
        if not _module_to_unfold(import_module, module_to_unfold):
            this_module.add_import(ImportInfo(name=import_module, to_unfold=False, path=None))
            continue
        module_paths = _resolve_module_to_path(import_module)
        if len(module_paths) == 1:
            # import a specific file
            this_module.add_import(_process_file(module_paths[0], module_to_unfold))
        else:
            # import a high level namespace
            for module_path in module_paths:
                this_module.add_import(_process_file(module_path, module_to_unfold))
    return this_module


def get_import_tree(py_files: list[Path], module_to_unfold: str) -> list[ImportInfo]:
    modules = []
    for py_file in py_files:
        modules.append(_process_file(py_file, module_to_unfold))
    return modules

def _resolve_module_to_path(module_name: str, src_dir: Path = Path('src')) -> list[Path]:
    """
    Resolve a module name like `my_module.sub.module` to a file path.
    Assumes modules are in the current working directory or in PYTHONPATH.
    """
    parts = module_name.split(".")
    for ext in (".py", "/__init__.py"):
        candidate = Path(*parts).with_suffix(ext if ext == ".py" else "")
        site_package_candidate_location = _get_site_packages_location() / candidate
        src_candidate_location = src_dir / candidate
        if site_package_candidate_location.exists():
            if site_package_candidate_location.is_file():
                return [site_package_candidate_location]
            if site_package_candidate_location.is_dir():
                submodules = glob.glob(f"{site_package_candidate_location}/**/*.py")
                return [Path(x) for x in submodules]
        elif src_candidate_location.exists():
            if src_candidate_location.is_file():
                return [src_candidate_location]
            if src_candidate_location.is_dir():
                submodules = glob.glob(f"{src_candidate_location}/**/*.py")
                return [Path(x) for x in submodules]
    raise RuntimeError(f"Can't resolve {module_name}")


# Example usage:
if __name__ == "__main__":
    py_files = glob.glob("src/**/*.py", recursive=True)
    import_tree = get_import_tree([Path(x) for x in py_files], 'my-company')

    # For demonstration: print package names
    def print_tree(pkgs: list[ImportInfo], indent=0):
        for pkg in pkgs:
            print("  " * indent + f"{pkg.name} {'[+]' if pkg.to_unfold else ''}")
            print_tree(pkg.imports, indent + 1)

    print_tree(import_tree)
