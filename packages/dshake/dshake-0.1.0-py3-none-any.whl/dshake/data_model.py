from dataclasses import dataclass, field
from pathlib import Path
from typing import List

@dataclass
class ImportInfo:
    name: str | None                     # Full path to the file/module
    path: Path | None                     # Full path to the file/module
    to_unfold: bool     # True if it's an internal import, False if it's
    imports: List["ImportInfo"] = field(default_factory=list)

    def add_import(self, module: "ImportInfo"):
        self.imports.append(module)

    def get_internal_imports(self) -> List["ImportInfo"]:
        return [imp for imp in self.imports if imp.to_unfold]

    def get_external_imports(self) -> List["ImportInfo"]:
        return [imp for imp in self.imports if not imp.to_unfold]


@dataclass
class PackageInfo:
    name: str
    version: str | None
    to_unfold: bool
    imports: List["PackageInfo"] = field(default_factory=list)

