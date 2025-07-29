import glob
from pathlib import Path

from dshake.data_model import ImportInfo
from dshake.module_import import get_import_tree
from dshake.utils import _get_site_packages_location


def _get_flat_imports(imports: list[ImportInfo]):
    import_set = set()
    def traverse_tree(imps: list[ImportInfo], indent=0):
        for imp in imps:
            if imp.name is not None:
                import_set.add(imp.name)
            traverse_tree(imp.imports, indent + 1)
    traverse_tree(imports)
    return import_set

def analyze_package_usages(
    src_dir: Path,
    namespace: str,
    always_include: list[str] | None = None
) -> dict[str, set[str]]:

    def add_package(name: str, version: str, module_to_unfold: str, no_dep_list: set, dep_list: set):
        if module_to_unfold in name:
            no_dep_list.add(f"{name.replace('_', '-')}=={version}")
        else:
            dep_list.add(f"{name.replace('_', '-')}=={version}")

    py_files = glob.glob(str(src_dir / "**/*.py"), recursive=True)
    import_tree = get_import_tree([Path(x) for x in py_files], namespace)
    always_include = always_include or []
    total_imports = _get_flat_imports(import_tree)
    site_package_loc = _get_site_packages_location()
    all_site_package_dirs = glob.glob(str(site_package_loc / "*.dist-info"))

    used_packages_with_dep = set()
    used_packages_no_dep = set()

    for site_package_dir in all_site_package_dirs:
        package_dir = Path(site_package_dir).name.replace(".dist-info", "")
        package_name, package_version = package_dir.split("-", 1)

        if package_name in always_include:
            add_package(package_name, package_version, namespace, used_packages_no_dep, used_packages_with_dep)
            continue

        record_path = Path(site_package_dir) / "RECORD"
        if not record_path.exists():
            continue

        namespaces = set()
        with open(record_path, "r") as file:
            for line in file:
                entry = line.strip().split(",")[0]
                if entry.endswith(".py") and not entry.endswith("__init__.py"):
                    namespaces.add(".".join(Path(entry).with_suffix("").parts))
                elif entry.endswith("__init__.py"):
                    namespaces.add(".".join(Path(entry).parent.parts))

        if any(item in namespaces for item in total_imports):
            add_package(package_name, package_version, 'siemens', used_packages_no_dep, used_packages_with_dep)

    return {
        "used_packages_with_deps": used_packages_with_dep,
        "used_packages_no_deps": used_packages_no_dep
    }

# # Example usage:
# if __name__ == "__main__":
#     py_files = glob.glob("src/**/*.py", recursive=True)
#     import_tree = build_import_tree([Path(x) for x in py_files], 'my-company')
#
#     total_imports = _get_flat_imports(import_tree)
#     all_site_package_dirs = glob.glob(str(get_site_packages_location() / "*.dist-info"), recursive=True)
#
#     site_package_loc = get_site_packages_location()
#
#     used_packages_with_dep = set()
#     used_packages_no_dep = set()
#     for site_package_dir in all_site_package_dirs:
#         package_dir = Path(site_package_dir).name
#
#         package_dir = package_dir.replace('.dist-info', '')
#         package_name = package_dir.split('-')[0]
#         package_version = package_dir.split('-')[1]
#
#         package_disinfo_record = Path(site_package_dir) / "RECORD"
#         with open(package_disinfo_record, 'r') as file:
#             lines = file.readlines()
#         namespaces = set()
#         for line in lines:
#             file_entries = line.strip().split(',')[0]
#             if file_entries.endswith('.py') and (not file_entries.endswith('__.py')):
#                 namespace = '.'.join(file_entries.rstrip('.py').split('/'))
#                 namespaces.add(namespace)
#             if file_entries.endswith('__init__.py'):
#                 namespace = '.'.join(file_entries.rstrip('/__init__.py').split('/'))
#                 namespaces.add(namespace)
#         if any(item in namespaces for item in total_imports):
#         # if any(sub in string for string in namespaces for sub in total_imports):
#             if 'my-company' in package_name:
#                 used_packages_no_dep.add(f"{package_name.replace('_', '-')}=={package_version}")
#             else:
#                 used_packages_with_dep.add(f"{package_name.replace('_', '-')}=={package_version}")
#     print('used_packages_no_dep:')
#     print(len(used_packages_no_dep))
#     print(used_packages_no_dep)
#     print('used_packages_with_dep:')
#     print(len(used_packages_with_dep))
#     print(used_packages_with_dep)
