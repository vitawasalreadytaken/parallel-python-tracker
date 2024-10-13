import datetime
import importlib.metadata
import json
import pathlib
import sys
import subprocess
import tomllib
from typing import Any

import importlib_metadata


def install_package(tested_package_name: str) -> dict[str, Any]:
    ret = subprocess.run(
        [sys.executable, "-m", "pip", "install", "--root-user-action", "ignore", tested_package_name],
        capture_output=True,
        text=True,
    )
    return {
        "success": ret.returncode == 0,
        "return_code": ret.returncode,
        "stdout": ret.stdout,
        "stderr": ret.stderr,
    }


def find_importable_module(package_name: str, packages_spec: list[dict[str, Any]]) -> str:
    for pkg in packages_spec:
        if pkg["name"] == package_name and "importable_name" in pkg:
            return pkg["importable_name"]

    def normalize(s: str) -> str:
        return s.replace("-", "_").lower()

    package_name = normalize(package_name)
    # e.g. {'dateutil': ['python-dateutil']}
    for module, packages in importlib_metadata.packages_distributions().items():
        if package_name in map(normalize, packages):
            return module
    raise ValueError("Package not found", package_name)


if __name__ == "__main__":
    # Parse command line arguments
    test_type = sys.argv[1]
    if test_type == "freethreading":
        test_script = "test_freethreading.py"
    elif test_type == "subinterpreters":
        test_script = "test_subinterpreters.py"
    else:
        raise ValueError("Unknown test type", test_type)
    tested_package_name = sys.argv[2]

    packages_spec = tomllib.loads(pathlib.Path("tested_packages.toml").read_text())["packages"]

    # Prepare the report
    report = {
        "start_time": datetime.datetime.now(tz=datetime.timezone.utc).isoformat(),
        "python_version": sys.version,
        "python_version_info": sys.version_info,
        "test_type": test_type,
        "tested_package_name": tested_package_name,
        "installation": {"success": None},
        "test": {"success": None},
    }

    # Install the package
    try:
        report["installation"] = install_package(tested_package_name)
    except Exception as e:
        report["installation"] = {
            "success": False,
            "exception": repr(e),
        }

    if report["installation"]["success"]:
        # Find the importable module name
        tested_package_name_importable = find_importable_module(tested_package_name, packages_spec)
        report["tested_package_name_importable"] = tested_package_name_importable
        report["package_version"] = importlib.metadata.version(tested_package_name)

        # Run the test
        try:
            ret = subprocess.run(
                [sys.executable, test_script, tested_package_name_importable],
                capture_output=True,
                text=True,
            )
            report["test"] = {
                "success": ret.returncode == 0,
                "return_code": ret.returncode,
                "stdout": ret.stdout,
                "stderr": ret.stderr,
            }
        except Exception as e:
            report["test"] = {
                "success": False,
                "exception": repr(e),
            }

    # Print the report
    report["end_time"] = datetime.datetime.now(tz=datetime.timezone.utc).isoformat()
    print(json.dumps(report, indent=2))
