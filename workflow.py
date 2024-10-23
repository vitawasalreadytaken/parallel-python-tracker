import datetime
import json
import pathlib
import subprocess
import tomllib
from typing import Any

import jinja2
import prefect
import prefect.cache_policies
import prefect.futures
import prefect.task_runners


TEST_REPORTS_DIR = pathlib.Path("output")


@prefect.task(
    task_run_name="test_{test_type}_{package_name}",
    cache_policy=prefect.cache_policies.TASK_SOURCE + prefect.cache_policies.INPUTS,
    cache_expiration=datetime.timedelta(days=3),
)
def run_test(test_type: str, package_name: str) -> dict[str, Any]:
    """Run a test in a Docker container and return the report as a parsed JSON."""
    image = f"test_runner_{test_type}"
    ret = subprocess.run(
        ["docker", "run", "-t", "--rm", image, package_name],
        capture_output=True,
        text=True,
    )
    if ret.returncode == 0:
        return json.loads(ret.stdout.strip())

    print("--- Captured stdout ---")
    print(ret.stdout)
    print("--- Captured stderr ---")
    print(ret.stderr)
    raise subprocess.CalledProcessError(ret.returncode, ret.args)


@prefect.task
def build_report_table(reports: dict[str, dict[str, Any]]) -> str:
    success_percentages = {
        "freethreading": {"installation": 0.0, "test": 0.0},
        "subinterpreters": {"installation": 0.0, "test": 0.0},
    }
    for pkg_reports in reports.values():
        for test_type, report in pkg_reports.items():
            for key in success_percentages[test_type]:
                success_percentages[test_type][key] += float(bool(report[key]["success"]))
    for test_type in success_percentages:
        for key in success_percentages[test_type]:
            success_percentages[test_type][key] *= 100 / len(reports)

    env = jinja2.Environment(loader=jinja2.FileSystemLoader("templates"))
    template = env.get_template("index.html")
    return template.render(reports=reports, success_percentages=success_percentages)


@prefect.flow(
    log_prints=True,
    task_runner=prefect.task_runners.ThreadPoolTaskRunner(max_workers=4),
)
def run_tests(limit: int | None = None):
    packages_spec = tomllib.loads(pathlib.Path("test_runner/tested_packages.toml").read_text())["packages"]
    if limit is not None:
        packages_spec = packages_spec[:limit]
    # Initialising the output dict will preserve the same package order that we have in tested_packages.toml.
    reports = {pkg["name"]: {} for pkg in packages_spec}

    # Submit all the tests at once and let the task runner handle the execution.
    futures = []
    for pkg in packages_spec:
        futures += [
            run_test.submit("freethreading", pkg["name"]),
            run_test.submit("subinterpreters", pkg["name"]),
        ]
    awaited_futures = prefect.futures.wait(futures)
    assert not awaited_futures.not_done

    # Collect reports and write them as individual JSON files
    for report_future in awaited_futures.done:
        report = report_future.result()
        output_file = (
            TEST_REPORTS_DIR / report["tested_package_name"] / f"{report['test_type']}-{report['start_time']}.json"
        )
        output_file.parent.mkdir(parents=True, exist_ok=True)
        output_file.write_text(json.dumps(report, indent=2))
        reports[report["tested_package_name"]][report["test_type"]] = report

    # Generate the report table
    table = build_report_table(reports)
    (TEST_REPORTS_DIR / "index.html").write_text(table)


if __name__ == "__main__":
    run_tests()
