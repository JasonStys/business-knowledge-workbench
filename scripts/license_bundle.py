# @index-begin
# @symbol function/class: main L25
# @symbol variable/parameter: root L27
# @symbol variable/parameter: output L28
# @symbol variable/parameter: records L31
# @symbol variable/parameter: distribution L32
# @symbol variable/parameter: name L33
# @symbol variable/parameter: file L42
# @symbol variable/parameter: target L48
# @symbol variable/parameter: python_license L51
# @symbol variable/parameter: candidates L58
# @symbol variable/parameter: candidate L59
# @symbol variable/parameter: folder L69
# @symbol variable/parameter: path L76
# @index-end
"""Jason Stys: bundle build-environment dependency licenses and notices without collecting user data."""

import importlib.metadata
import json
import shutil
import sys
from pathlib import Path


def main():
    """Collect package metadata/license files, Python terms and installed npm licenses into generated release resources."""
    root = Path(__file__).resolve().parents[1]
    output = root / "release" / "notices"
    output.mkdir(parents=True, exist_ok=True)
    shutil.copy2(root / "LICENSE", output / "PROJECT-LICENSE.txt")
    records = []
    for distribution in importlib.metadata.distributions():
        name = distribution.metadata.get("Name", "unknown")
        records.append(
            {
                "name": name,
                "version": distribution.version,
                "license": distribution.metadata.get("License-Expression")
                or distribution.metadata.get("License", "See included license text"),
            }
        )
        for file in distribution.files or []:
            if (
                file.name.lower().startswith(("license", "copying", "notice"))
                and ".dist-info" in str(file)
                and distribution.locate_file(file).is_file()
            ):
                target = output / "python" / name / file.name
                target.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(distribution.locate_file(file), target)
    python_license = Path(sys.base_prefix) / "LICENSE.txt"
    if python_license.exists():
        shutil.copy2(python_license, output / "PYTHON-LICENSE.txt")
    else:
        # GitHub's Unix CPython runtime supplies its standard license in the stdlib.
        import sysconfig

        candidates = list(Path(sysconfig.get_path("stdlib")).glob("../*/LICENSE*"))
        for candidate in candidates:
            if candidate.is_file():
                shutil.copy2(candidate, output / "PYTHON-LICENSE.txt")
                break
        if not (output / "PYTHON-LICENSE.txt").exists():
            if sys.version_info[:2] != (3, 12):
                raise ValueError("Bundle a verified matching CPython license before distributing")
            shutil.copy2(
                root / "docs" / "licenses" / "python-3.12.txt", output / "PYTHON-LICENSE.txt"
            )
    for folder in [
        root / "node_modules" / "react",
        root / "node_modules" / "react-dom",
        root / "node_modules" / "monaco-editor",
        root / "node_modules" / "@monaco-editor" / "react",
        root / "node_modules" / "dompurify",
    ]:
        for path in folder.glob("*"):
            if path.is_file() and path.name.lower().startswith(("license", "copying", "notice")):
                target = output / "ui" / folder.name / path.name
                target.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(path, target)
    (output / "python-dependencies.json").write_text(
        json.dumps(records, indent=2), encoding="utf-8"
    )
    (output / "README.txt").write_text(
        "Business Knowledge Workbench by Jason Stys. Bundled third-party components retain their respective licenses. Electron also includes LICENSE.electron.txt and LICENSES.chromium.html beside the app. Development-only distributions may appear in the build inventory; no training model is bundled.\n",
        encoding="utf-8",
    )


if __name__ == "__main__":
    main()
