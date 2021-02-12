"""dbt_unit_test.app: CLI for running unit tests on dbt macros."""

import os, sys
import click


from .log_setup import logger, LOG_LEVELS
from . import operations as ops
import yaml

with open('dbt_unit_test.yml', 'r') as conf_file:
    config = yaml.safe_load(conf_file.read())


@click.command()
@click.option('--tests', help='tests to run.')
@click.option('--batches', default=2, help='batches to run.')
@click.option('--log-level', default='warning', help='Set log level.')
def run(tests, batches, log_level):
    """Run unit tests on a dbt models."""
    logger.setLevel(LOG_LEVELS.get(log_level, 'warning'))

    profile = ['--profile', config['unit_test_profile']]

    model = ['+tag:unit_test+']
    if tests:
        model = [f'+tag:{test}+' for test in tests.split(',')]

    ops.remove_files(**config)
    ops.copy_files(**config)

    errors = 0

    errors += ops.dbt_sp(['dbt', 'seed', '--full-refresh', '--select'] + model + profile)

    for batch in range(1, batches):
        cmd = ['dbt', 'run', '--vars', f"batch: {batch}", '--model'] + model + profile
        errors += ops.dbt_sp(cmd + ['--full-refresh'] if batch == 1 else cmd)
        errors += ops.dbt_sp(['dbt', 'run', '--model']  + model + profile)

    errors += ops.dbt_sp(['dbt', 'test', '--model'] + model + profile)

    # TODO: Decide whether we want to keep the schema around.
    # errors += ops.dbt_sp(['dbt', 'run-operation', 'drop_schema', '--args', 'name: _unittests_'])

    if log_level != 'debug':
        ops.remove_files(**config)

    if errors != 0:
        sys.exit(os.EX_SOFTWARE)
        
    

if __name__ == '__main__':
    run()