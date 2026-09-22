import pytest

from conftest import load_source_module


@pytest.fixture(scope="module")
def validation_module():
    return load_source_module("_validation_under_test", "autocaption/validation.py")


@pytest.mark.parametrize("value", [True, False])
def test_bool_values_are_accepted(validation_module, value):
    assert validation_module.validate_bool_flag("flag", value) is value


@pytest.mark.parametrize("value", [0, 1, "True", "", None, 0.0, [], object()])
def test_non_bool_values_are_rejected(validation_module, value):
    with pytest.raises(TypeError, match="my_flag"):
        validation_module.validate_bool_flag("my_flag", value)
