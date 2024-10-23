import datetime
from typing import TypedDict, Literal


class InstallationTestResult(TypedDict):
    success: Literal[None, True, False]
    # There are more fields in some cases - these could be documented better


class ImportTestResult(TypedDict):
    success: Literal[None, True, False]
    # There are more fields in some cases - these could be documented better


class TestReport(TypedDict):
    start_time: str  # isoformat
    end_time: None | str  # isoformat
    python_version: str
    python_version_info: tuple
    test_type: Literal["freethreading", "subinterpreters"]
    tested_package_name: str
    tested_package_name_importable: None | str
    package_version: None | str
    installation: InstallationTestResult
    test: ImportTestResult
