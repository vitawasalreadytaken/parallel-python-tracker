import _interpreters
import json
import pathlib
import sys


SUBINTERPRETER_TEST_CODE = """
import json

with open("%(output_file)s", "w") as f:
    try:
        import %(tested_package_name_importable)s
        %(specific_test_import)s
    except Exception as e:
        json.dump({"success": False, "exception": repr(e)}, f)
    else:
        json.dump({"success": True}, f)
"""


if __name__ == "__main__":
    tested_package_name_importable = sys.argv[1]

    specific_test_file = pathlib.Path("specific_tests") / f"{tested_package_name_importable}_subinterpreters.py"
    if specific_test_file.exists():
        specific_test_import = f"import specific_tests.{tested_package_name_importable}_subinterpreters"
    else:
        specific_test_import = ""

    output_file = "subinterpreters_test_output.json"
    subinterpreter = _interpreters.create()
    _interpreters.exec(
        subinterpreter,
        SUBINTERPRETER_TEST_CODE
        % {
            "output_file": output_file,
            "tested_package_name_importable": tested_package_name_importable,
            "specific_test_import": specific_test_import,
        },
    )

    with open(output_file) as f:
        report = f.read()

    print(report)
    sys.exit(0 if json.loads(report)["success"] else 1)
