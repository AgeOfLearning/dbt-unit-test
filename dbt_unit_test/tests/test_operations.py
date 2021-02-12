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


def test_remove_files(dirs):
    operations.copy_files(**dirs)
    operations.remove_files(**dirs)
    assert glob.glob('_models/unit_tests/**/*', recursive=True) == []

def test_copy_files(dirs):
    operations.copy_files(**dirs)
    assert set(glob.glob('_models/unit_tests/test1*', recursive=True)) == \
        {
            '_models/unit_tests/test1_models.yml',
            '_models/unit_tests/test1_model.sql',
            '_models/unit_tests/test1_source.sql'
        }
    assert set(glob.glob('_data/unit_tests/test1*', recursive=True)) == \
        {
            '_data/unit_tests/test1_input.csv',
            '_data/unit_tests/test1_output.csv'
        }
    assert set(glob.glob('_data/unit_tests/test2*', recursive=True)) == \
        {
            '_data/unit_tests/test2_input.csv',
            '_data/unit_tests/test2_output.csv'
        }
    assert os.path.exists('_macros/unit_tests/test_macros.sql')
