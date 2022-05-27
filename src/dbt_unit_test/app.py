"""dbt_unit_test.app: CLI for running unit tests on dbt macros."""

import os
import shutil
import sys

import click
import yaml

from dbt_unit_test import operations as ops
from dbt_unit_test.log_setup import LOG_LEVELS, console, logger


@click.group()
def dut():
    pass


@click.command()
def init():
    if not os.path.exists("dbt_unit_test.yml"):
        with open("dbt_unit_test.yml", "w") as conf_file:
            conf_file.write(ops.render_template("default_config.yml"))
    example_test_path = os.path.join(os.path.dirname(__file__), "assets/example_test")
    if os.path.exists("unit_tests/example_test"):
        shutil.rmtree("unit_tests/example_test")
    shutil.copytree(example_test_path, "unit_tests/example_test")
    click.secho("DUT setup complete.")
    # TODO Check if the appropriate profile exists already
    click.secho('Please set up a dbt profile called "unit_test".', fg="blue")


@click.command()
@click.option("--tests", help="tests to run.")
@click.option("--batches", default=2, help="batches to run.")
@click.option("--log-level", default="info", help="Set log level.")
@click.option(
    "--cleanup/--no-cleanup", is_flag=True, default=True, help="Set log level."
)
def run(tests, batches, log_level, cleanup):
    """Run unit tests on a dbt models."""

    # use defaults if there is no config file.

    with open("dbt_unit_test.yml", "r") as conf_file:
        config = yaml.safe_load(conf_file.read())

    console.setLevel(LOG_LEVELS.get(log_level, "info"))

    profile = ["--profile", config["unit_test_profile"]]

    seed_dir = os.path.join(config["seed_dir"], config["unit_test_dir"])
    models_dir = os.path.join(config["models_dir"], config["unit_test_dir"])

    # TODO: do we need the +model+? There shouldn't be dependencies for unit tests
    seed = (
        [f"+{test}_model+" for test in tests.split(" ")]
        if tests
        else [f"+path:{seed_dir}+"]
    )
    model = (
        [f"+{test}_model+" for test in tests.split(" ")]
        if tests
        else [f"+path:{models_dir}+"]
    )
    select_seed = ["--select"] + seed
    select_model = ["--select"] + model

    ops.remove_files(**config)
    ops.copy_files(**config)

    errors = 0

    errors += ops.dbt_sp(["dbt", "seed", "--full-refresh"] + select_seed + profile)

    for batch in range(1, batches + 1):
        vars_ = []
        if batch <= batches:
            vars_ += ["--vars", f"{{batch: {batch}}}"]

        if batch == 1:
            vars_ += ["--full-refresh"]

        errors += ops.dbt_sp(["dbt", "run"] + select_model + profile + vars_)

    errors += ops.dbt_sp(["dbt", "test"] + select_model + profile)

    # TODO make this a cleanup flag (default: True)
    if cleanup:
        ops.remove_files(**config)

    if errors != 0:
        sys.exit(os.EX_SOFTWARE)
    else:
        logger.info("All tests passed!")


dut.add_command(run)
dut.add_command(init)

if __name__ == "__main__":
    dut()
