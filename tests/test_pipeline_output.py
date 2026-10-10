import json

import pytest

from conftest import load_source_module
from test_pipeline import load_main_with_fakes


EXPECTED_RESULT = [[
    {"Tree": 2, "Building": 1},
    {"city street": 0.81},
    "Базовое описание: base",
    "Подробное описание: detailed",
    "Альтернативное описание: alternative",
    "Описание по вопросу (VQA): vqa",
]]

HEAVY_COMPONENTS = [
    "ImageRotator",
    "CarDetector",
    "ObjectExtractor",
    "SceneExtractor",
    "PhotoDescriber",
    "PhotoDescriberWithQuestion",
]


@pytest.fixture
def main_and_counters(monkeypatch):
    return load_main_with_fakes(monkeypatch, loaded_image=object(), has_car=True)


def test_without_output_path_returns_results_and_writes_nothing(main_and_counters, tmp_path, monkeypatch):
    main, _ = main_and_counters
    monkeypatch.chdir(tmp_path)

    result = main.run_pipeline(["car.jpg"], source=True)

    assert result == EXPECTED_RESULT
    assert list(tmp_path.iterdir()) == []


def test_output_path_none_is_default(main_and_counters):
    main, _ = main_and_counters

    assert main.run_pipeline(["car.jpg"], source=True, output_path=None) == EXPECTED_RESULT


@pytest.mark.parametrize("as_pathlike", [False, True])
def test_output_path_writes_same_results_as_returned(main_and_counters, tmp_path, as_pathlike):
    main, _ = main_and_counters
    out = tmp_path / "result.json"

    result = main.run_pipeline(
        ["car.jpg"], source=True, output_path=out if as_pathlike else str(out))

    assert result == EXPECTED_RESULT
    assert json.loads(out.read_text(encoding="utf-8")) == result


@pytest.mark.parametrize("bad_path", [123, 1.5, b"out.json", ["out.json"], object()])
def test_invalid_output_path_type_raises_type_error_before_models(main_and_counters, bad_path):
    main, counters = main_and_counters

    with pytest.raises(TypeError):
        main.run_pipeline(["car.jpg"], source=True, output_path=bad_path)

    assert all(counters[name] == 0 for name in HEAVY_COMPONENTS)
    assert counters["ImageLoader"] == 0


def test_empty_output_path_raises_value_error_before_models(main_and_counters):
    main, counters = main_and_counters

    with pytest.raises(ValueError):
        main.run_pipeline(["car.jpg"], source=True, output_path="")

    assert all(counters[name] == 0 for name in HEAVY_COMPONENTS)
    assert counters["ImageLoader"] == 0


def test_missing_directories_are_created(main_and_counters, tmp_path):
    main, _ = main_and_counters
    out = tmp_path / "nested" / "deeper" / "result.json"

    result = main.run_pipeline(["car.jpg"], source=True, output_path=out)

    assert out.is_file()
    assert json.loads(out.read_text(encoding="utf-8")) == result


def test_empty_input_writes_empty_list(main_and_counters, tmp_path):
    main, _ = main_and_counters
    out = tmp_path / "result.json"

    result = main.run_pipeline([], source=True, output_path=out)

    assert result == []
    assert json.loads(out.read_text(encoding="utf-8")) == []


def test_existing_file_is_overwritten(main_and_counters, tmp_path):
    main, _ = main_and_counters
    out = tmp_path / "result.json"
    out.write_text("old content that is not even json", encoding="utf-8")

    result = main.run_pipeline(["car.jpg"], source=True, output_path=out)

    assert json.loads(out.read_text(encoding="utf-8")) == result


def test_cyrillic_is_not_escaped(main_and_counters, tmp_path):
    main, _ = main_and_counters
    out = tmp_path / "result.json"

    main.run_pipeline(["car.jpg"], source=True, output_path=out)

    text = out.read_text(encoding="utf-8")
    assert "Базовое описание" in text
    assert "\\u" not in text


def test_unwritable_location_raises_clear_error(main_and_counters, tmp_path):
    main, _ = main_and_counters
    # a regular file used as a parent directory cannot be written into on any OS
    blocker = tmp_path / "not_a_dir"
    blocker.write_text("", encoding="utf-8")
    out = blocker / "result.json"

    with pytest.raises(OSError) as exc_info:
        main.run_pipeline(["car.jpg"], source=True, output_path=out)

    assert type(exc_info.value).__name__ == "ResultsSaveError"
    message = str(exc_info.value)
    assert "Не удалось сохранить результаты" in message
    assert str(out) in message


def test_result_writer_is_exported_from_public_api():
    package_init = load_source_module.__globals__["PROJECT_ROOT"] / "autocaption" / "__init__.py"
    source = package_init.read_text(encoding="utf-8")

    for name in ("ResultsSaveError", "validate_output_path", "save_results_json"):
        assert f'"{name}"' in source
