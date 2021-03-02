import pytest, os, glob, shutil

from dbt_unit_test import operations

os.chdir(os.path.join(os.path.dirname(__file__), 'test_project'))

@pytest.fixture
def dirs():
    return dict(
        unit_test_dir='unit_tests',
        models_dir='_models',
        data_dir='_data',
        macros_dir='_macros'
    )

@pytest.fixture(autouse=True)
def clean_up():
    shutil.rmtree('_models', ignore_errors=True)
    shutil.rmtree('_data', ignore_errors=True)
    shutil.rmtree('_macros', ignore_errors=True)
    yield
    shutil.rmtree('_models', ignore_errors=True)
    shutil.rmtree('_data', ignore_errors=True)
    shutil.rmtree('_macros', ignore_errors=True)


def test__remove_files(dirs):
    operations.copy_files(**dirs)
    operations.remove_files(**dirs)
    assert glob.glob('_models/unit_tests/**/*', recursive=True) == []

def test__copy_files(dirs):
    operations.copy_files(**dirs)
    assert set(glob.glob('_models/unit_tests/test1*', recursive=True)) == \
        {
            '_models/unit_tests/test1_model.yml',
            '_models/unit_tests/test1_model.sql',
            '_models/unit_tests/test1_batch.sql'
        }
    assert set(glob.glob('_data/unit_tests/test1*', recursive=True)) == \
        {
            '_data/unit_tests/test1_input.csv',
            '_data/unit_tests/test1_expect.csv'
        }
    assert set(glob.glob('_data/unit_tests/test2*', recursive=True)) == \
        {
            '_data/unit_tests/test2_input.csv',
            '_data/unit_tests/test2_expect.csv'
        }
    assert os.path.exists('_macros/unit_tests/test_macros.sql')

def test__write_derived_file(dirs):
    dbt_file = '_models/unit_tests/derived_unit_test_model.sql'
    batch_file = '_models/unit_tests/derived_unit_test_batch.sql'
    os.makedirs(os.path.dirname(dbt_file), exist_ok=True)
    operations.write_derived_file(dbt_file, 'batch.sql')
    assert os.path.exists(batch_file)
    with open(batch_file) as f:
        derived_unit_test_batch = f.read()
    assert "tags=['unit_test', 'derived_unit_test']" in derived_unit_test_batch

def test__get_test_name_from_dbt_model_path():
    assert operations.get_test_name_from_dbt_model_path(
        '_models/unit_tests/test1_testy_test_model.sql'
    ) == 'test1_testy_test'

def test__map_dbt_file_to_dut_file():
    assert operations.map_dbt_file_to_dut_file(
        'dbt_dir', 'unit_tests/test2/model.sql'
    ) == 'dbt_dir/unit_tests/test2_model.sql'

def test__render_template():
    rendered = operations.render_template('model.yml', test_name='my_model')
    assert "test: ref('my_model_expect')" in rendered

def test__dbt_sp():
    assert operations.dbt_sp('ls -la'.split()) == 0
    assert operations.dbt_sp('ls -not-a-command'.split()) == 1
    assert operations.dbt_sp(['echo', '"Done. FAIL"']) == 0
    assert operations.dbt_sp(['echo', '"FAIL."']) == 0