from dshake.data_model import PackageInfo
import subprocess
import re

def get_dependency_tree(package_name: str, dependency_manager: str = "poetry") -> list[PackageInfo]:
    match dependency_manager:
        case "poetry":
            return _get_poetry_venv_dependency_tree(package_name)
        case "uv":
            return _get_uv_venv_dependency_tree(package_name)
        case _:
            raise ValueError(f"Unsupported dependency manager: {dependency_manager}")

def _parse_single_line(line: str, package_to_unfold: str | None) -> PackageInfo:
    pattern = re.compile(r'^(?P<indent>[ │├└─]*)(?P<name>[a-zA-Z0-9_.\-]+)(?: (?P<version>[^\s]+))?.*$')
    match = pattern.match(line)

    name = match.group("name")
    version = match.group("version")

    if package_to_unfold is not None and package_to_unfold in name:
        return PackageInfo(name=name, version=version, to_unfold=True)
    else:
        return PackageInfo(name=name, version=version, to_unfold=False)

def _get_visual_depth(line: str):
    """Estimate depth from visual tree characters like │ and ├──."""
    # Remove value content to isolate structure
    match = re.match(r'^[\s│├└─]*', line)
    prefix = match.group(0) if match else ""
    # Count the number of box-drawing symbols like '│', '├', or '└'
    return prefix.count('│') + prefix.count('├') + prefix.count('└')

def _extract_tree_blocks(lines: list[str], package_to_unfold: str | None) -> list[PackageInfo]:
    """
    Extract blocks of text from a tree structure based on visual depth using symbols like ├──, │, └──.
    """

    packages = []

    if len(lines) == 0:
        return packages

    first_line_depth = _get_visual_depth(lines[0])
    current_package = _parse_single_line(lines[0], package_to_unfold)

    if len(lines) == 1:
        return [current_package]

    lines_within_current_package = []

    for i in range(1, len(lines)):
        depth = _get_visual_depth(lines[i])

        if depth == first_line_depth:
            if current_package.to_unfold:
                current_package.imports = _extract_tree_blocks(lines_within_current_package, package_to_unfold)
            packages.append(current_package)
            packages.extend(_extract_tree_blocks(lines[i:], package_to_unfold))
            break
        else:
            lines_within_current_package.append(lines[i])

        if i == len(lines) - 1:
            if current_package.to_unfold:
                current_package.imports = _extract_tree_blocks(lines_within_current_package, package_to_unfold)
            packages.append(current_package)

    return packages

def _get_uv_venv_dependency_tree(package_to_unfold: str) -> list[PackageInfo]:
    poetry_tree_output = subprocess.run(["uv", "pip", "tree"], capture_output=True, text=True, encoding='utf-8').stdout
    poetry_tree_output_lines = poetry_tree_output.strip().splitlines()
    return _extract_tree_blocks(poetry_tree_output_lines, package_to_unfold)

def _get_poetry_venv_dependency_tree(package_to_unfold: str) -> list[PackageInfo]:
    poetry_tree_output = subprocess.run(["poetry", "show", "--tree"], capture_output=True, text=True, encoding='utf-8').stdout
    poetry_tree_output_lines = poetry_tree_output.strip().splitlines()
    return _extract_tree_blocks(poetry_tree_output_lines, package_to_unfold)

# Example usage:
if __name__ == "__main__":
    dep_tree = _get_poetry_venv_dependency_tree('my-company')

    # For demonstration: print package names
    def print_tree(pkgs: list[PackageInfo], indent=0):
        for pkg in pkgs:
            print("  " * indent + f"{pkg.name} ({pkg.version}) {'[+]' if pkg.to_unfold else ''}")
            print_tree(pkg.imports, indent + 1)

    print_tree(dep_tree)
