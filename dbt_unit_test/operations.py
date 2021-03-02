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
    logger.info(' '.join(cmd))
    line, done_line = '', ''
    for line in iter(sp.stdout.readline, b''):
        line = line.decode().rstrip()
        if 'Done.' in line:
            done_line = line
        if 'FAIL' in line or 'Finished' in line:
            logger.info(line)
        else:
            logger.debug(line)
    sp.wait()
    if sp.returncode:
        logger.warning(f"\033[31mdbt {cmd[1]} failures. {done_line[6:]}\033[0m")
        return 1
    return 0
        

def map_dbt_file_to_dut_file(dbt_dir, dut_file):
    return os.path.join(dbt_dir, '_'.join(dut_file.rsplit('/', 1)))

def get_test_name_from_dbt_model_path(p):
    return p.split('/')[-1].rsplit('_',1)[0]


def write_derived_file(original_file_name, derived_file_type):
    test_name = get_test_name_from_dbt_model_path(original_file_name)

    derived_file_name = original_file_name.replace('model.sql', derived_file_type)

    if not os.path.exists(derived_file_name):
        with open(derived_file_name, 'w') as f:
            f.write(
                render_template(derived_file_type, test_name=test_name)
            )


def copy_files(
    unit_test_dir='unit_tests',
    models_dir='models',
    data_dir='data',
    macros_dir='macros',
    **kw
):
    for f in glob.glob(unit_test_dir + '/**/*.[ys][mq]l', recursive=True):
        dbt_file = map_dbt_file_to_dut_file(models_dir, f)
        os.makedirs(os.path.dirname(dbt_file), exist_ok=True)
        shutil.copy(f, dbt_file)
        write_derived_file(dbt_file, 'model.yml')
        write_derived_file(dbt_file, 'batch.sql')

    for f in glob.glob(unit_test_dir + '/**/*.csv', recursive=True):
        dbt_file = map_dbt_file_to_dut_file(data_dir, f)
        os.makedirs(os.path.dirname(dbt_file), exist_ok=True)
        shutil.copy(f, dbt_file)

        input_file_name = dbt_file.replace('expect.csv', 'input.csv')
        if 'expect' in dbt_file and not os.path.exists(input_file_name):
            with open(input_file_name, 'w') as dummy_input_file:
                dummy_input_file.write('batch')
                
    macro_filepath = os.path.join(macros_dir, unit_test_dir, 'test_macros.sql')
    os.makedirs(os.path.dirname(macro_filepath), exist_ok=True)
    with open(macro_filepath, 'w') as macro_file:
        macro_file.write(
            render_template('diff_macro.sql')+
            render_template('drop_schema_macro.sql')
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


def render_template(template, **kw):
    templates_dir = os.path.join(os.path.dirname(__file__), 'templates')
    with open(os.path.join(templates_dir, template)) as t:
        out = t.read()
        if kw:
            return jinja2.Template(out).render(**kw)
        return out

