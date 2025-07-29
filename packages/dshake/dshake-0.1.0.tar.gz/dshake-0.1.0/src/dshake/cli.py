import argparse
import json
from pathlib import Path

from dshake.package import analyze_package_usages

def run_analyze(args):
    result = analyze_package_usages(Path(args.src_dir), args.namespace)

    if args.format == "json":
        output = {
            "used_packages_with_deps": sorted(result["used_packages_with_deps"]),
            "used_packages_no_deps": sorted(result["used_packages_no_deps"]),
        }
        with open(args.output, 'w') as f:
            json.dump(output, f, indent=2)
    else:
        print("Used packages with deps:")
        print("\n".join(sorted(result["used_packages_with_deps"])))
        print("\nUsed packages with no deps:")
        print("\n".join(sorted(result["used_packages_no_deps"])))

def main():
    parser = argparse.ArgumentParser(prog="dshake", description="Dependency Shake CLI")

    subparsers = parser.add_subparsers(dest="command", required=True)

    # Subcommand: analyze
    analyze_parser = subparsers.add_parser("analyze", help="Analyze used packages in source code")
    analyze_parser.add_argument("--src-dir", type=str, default="src", help="Source code directory")
    analyze_parser.add_argument("--namespace", type=str, required=True, help="Your company/package namespace")
    analyze_parser.add_argument("--output", type=str, default="used_packages.json", help="Output file path")
    analyze_parser.add_argument("--format", choices=["json", "text"], default="json", help="Output format")
    analyze_parser.set_defaults(func=run_analyze)

    args = parser.parse_args()
    args.func(args)

if __name__ == "__main__":
    main()