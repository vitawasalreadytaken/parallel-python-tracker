import importlib
import json
import pathlib
import sys


if __name__ == "__main__":
    tested_package_name_importable = sys.argv[1]

    assert not sys._is_gil_enabled()

    importlib.import_module(tested_package_name_importable)

    specific_test_file = pathlib.Path("specific_tests") / f"{tested_package_name_importable}_freethreading.py"
    if specific_test_file.exists():
        importlib.import_module(f"specific_tests.{tested_package_name_importable}_freethreading")

    report = {
        "success": not sys._is_gil_enabled(),
    }
    print(json.dumps(report))
    sys.exit(0 if report["success"] else 1)
