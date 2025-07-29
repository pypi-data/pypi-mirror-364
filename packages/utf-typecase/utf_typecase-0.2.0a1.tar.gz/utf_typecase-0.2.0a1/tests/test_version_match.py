# tests/test_version_match.py
import tomli  # or tomllib if you're using Python 3.11+
import pathlib
import re


def test_version_consistency():
    # Path to your project directory
    project_root = pathlib.Path(__file__).resolve().parent.parent
    init_path = project_root / "src" / "utf_typecase" / "__init__.py"
    toml_path = project_root / "pyproject.toml"

    # Read version from __init__.py
    init_content = init_path.read_text(encoding="utf-8")
    init_match = re.search(r'__version__\s*=\s*[\'"]([^\'"]+)[\'"]', init_content)
    assert init_match, "No __version__ found in __init__.py"
    init_version = init_match.group(1)

    # Read version from pyproject.toml
    with toml_path.open("rb") as f:
        toml_data = tomli.load(f)
    toml_version = toml_data["project"]["version"]

    assert (
        init_version == toml_version
    ), f"Version mismatch: {init_version} != {toml_version}"
