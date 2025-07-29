# DShake

**DShake** is a tool to _introspect, unfold, and analyze internal and external dependencies_ in a Python project—especially when managing **large monorepos**, **private packages**, and **organizational Python distributions**.


## 🚨 Problem Statement
Managing code and dependencies in large organizations often leads to the following issues:

### 1. Organizational Dependency Management
Organizations often publish internal packages (e.g., `my-company-core`, `my-company-ml`) to private repositories or internal PyPI registries. Over time:

- It becomes unclear which internal packages are truly used.
- Shared utilities are copied across services instead of being reused properly.
- External dependencies may duplicate internal functionality unknowingly.
- No tooling exists to **visualize internal usage vs. third-party** dependencies.

### 2. Project Domain Import Management
In a Python project:

- Imports like from `my_company.core.utils import X` can be hard to trace—where do they come from?
- Relative imports, internal utilities, and third-party modules get mixed up.
- You want to analyze **how your project relies on specific internal / external packages**, and which of them are _leaf_ vs _core_ dependencies.

## 🧰 Usages
### CLI Command Structure
```bash
dshake analyze [OPTIONS]
```
```bash
dshake analyze \
  --src-dir src \
  --namespace my-company \
  --output used_packages.json \
  [--format json|text]
```

### Python Package API
```python
from dshake.package import analyze_package_usages
from dshake.dependency import get_dependency_tree
from dshake.module_import import get_import_tree
```


## 🧩 Key Features
- **Build import trees** from Python files using AST traversal.
- **Differentiate internal** (`to_unfold=True`) vs. external imports based on namespace (e.g., `my-company`).
- **Parse Poetry’s `show --tree` output**, capturing hierarchical dependency chains.
- **Correlate import usage with installed packages** to surface only those used in practice.
- **Detect internal packages in use**, separate from third-party dependencies.

## 📌 Why This Matters
- ✅ Helps de-risk code audits, refactorings, and security scans.
- 📉 Can drive dependency slimming (e.g., removing unused packages).
- 💡 Surfaces duplicated functionality between internal and external libraries.
- 📊 Builds a foundation for automated graph-based tooling on import relationships.

## 🧠 Credits
Built by an engineer who got tired of guessing where my-company-utils was coming from. Inspired by the lack of ecosystem tools that combine **AST**, **package metadata**, and **visual dependency resolution**.