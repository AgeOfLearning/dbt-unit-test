import os
import subprocess
import logging
import glob
import shutil
import jinja2

from .log_setup import logger

def dbt_sp(cmd, log_level=logging.INFO): 
    sp = subprocess.Popen(
        cmd,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        cwd='.',
        close_fds=True)
    logger.warning(' '.join(cmd))
    line = ''
    for line in iter(sp.stdout.readline, b''):
        line = line.decode().rstrip()
        if 'FAIL' in line or 'Finished' in line:
            logger.warn(line)
        else:
            logger.info(line)
    sp.wait()
    if sp.returncode:
        logger.warning("Failures.")
        return 1
    return 0
        

def map_to_dbt_files(d, f):
    return os.path.join(d, '_'.join(f.rsplit('/', 1)))


def write_derived_files(f_prime):
    test_name = f_prime.split('/')[-1].split('_')[0]
    if not os.path.exists(f_prime.replace('model.sql', 'model.yml')):
        with open(f_prime.replace('model.sql', 'model.yml'), 'w') as model_yml_file:
            model_yml_file.write(model_yml(test_name))
    if not os.path.exists(f_prime.replace('model.sql', 'batch.sql')):
        with open(f_prime.replace('model.sql', 'batch.sql'), 'w') as batch_sql_file:
            batch_sql_file.write(batch_sql(test_name))


def copy_files(
    unit_test_dir='unit_tests',
    models_dir='models',
    data_dir='data',
    macros_dir='macros',
    **kw
):
    for f in glob.glob(unit_test_dir + '/**/*.[ys][mq]l', recursive=True):
        f_prime = map_to_dbt_files(models_dir, f)
        os.makedirs(os.path.dirname(f_prime), exist_ok=True)
        shutil.copy(f, f_prime)
        write_derived_files(f_prime)

    for f in glob.glob(unit_test_dir + '/**/*.csv', recursive=True):
        f_prime = map_to_dbt_files(data_dir, f)
        os.makedirs(os.path.dirname(f_prime), exist_ok=True)
        shutil.copy(f, f_prime)

        input_file_name = f_prime.replace('expect.csv', 'input.csv')
        if 'expect' in f_prime and not os.path.exists(input_file_name):
            with open(input_file_name, 'w') as dummy_input_file:
                dummy_input_file.write('batch')
                
    macro_filepath = os.path.join(macros_dir, unit_test_dir, 'test_macros.sql')
    os.makedirs(os.path.dirname(macro_filepath), exist_ok=True)
    with open(macro_filepath, 'w') as macro_file:
        macro_file.write(
            diff_macro()+
            drop_schema_macro()
        )

def remove_files(
    unit_test_dir='unit_tests',
    models_dir='models',
    data_dir='data',
    macros_dir='macros',
    **kw
):
    shutil.rmtree(os.path.join(models_dir, unit_test_dir), ignore_errors=True)
    shutil.rmtree(os.path.join(data_dir, unit_test_dir), ignore_errors=True)
    shutil.rmtree(os.path.join(macros_dir, unit_test_dir), ignore_errors=True)

def model_yml(test_name):
    return jinja2.Template("""
version: 2
models:
  - name: {{test_name}}_model
    tests:
      - diff:
          test: ref('{{test_name}}_expect')

""").render(test_name=test_name)

def batch_sql(test_name):
    return jinja2.Template("""
{% raw %}{{
    config(
        materialized='ephemeral',
        tags=['unit_test', '{% endraw %}{{ test_name }}{% raw %}']
    )
}}
SELECT * FROM {{ ref('{% endraw %}{{ test_name }}{% raw %}_input') }}
WHERE batch <= {{ var('batch', 100) }}{% endraw %}
-- {% raw %}{{ ref('{% endraw %}{{ test_name }}{% raw %}_expect') }}{% endraw %}
""").render(test_name=test_name)

def diff_macro():
    return """{% macro test_diff(model, test) %}
with extra_rows as (
    SELECT * FROM {{ model }} EXCEPT SELECT * FROM {{ test }}
), 
missing_rows as (
    SELECT * FROM {{ test }} EXCEPT SELECT * FROM {{ model }}
)
SELECT count(*)
FROM (SELECT * FROM extra_rows UNION ALL SELECT * FROM missing_rows) a
{% endmacro %}
"""

def drop_schema_macro():
    return """{% macro drop_schema(name) %}
{% set sql %}
DROP SCHEMA IF EXISTS {{ name }}
{% endset %}
{% do run_query(sql) %}
{% endmacro %}
"""
