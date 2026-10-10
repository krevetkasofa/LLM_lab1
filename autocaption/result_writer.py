import json
import os


class ResultsSaveError(OSError):
    """Понятная ошибка сохранения результатов pipeline в файл."""


def validate_output_path(output_path) -> None:
    """
    Проверяет аргумент output_path до запуска pipeline.
    :param output_path: путь к JSON-файлу или None
    :raises TypeError: если путь не str и не os.PathLike
    :raises ValueError: если путь пустой
    """
    if output_path is None:
        return
    if not isinstance(output_path, (str, os.PathLike)):
        raise TypeError(
            f"output_path должен быть str или os.PathLike, получено: {type(output_path).__name__}")
    if os.fspath(output_path) == "":
        raise ValueError("output_path не может быть пустой строкой")


def save_results_json(results, output_path) -> None:
    """
    Сохраняет результаты pipeline в JSON-файл (перезаписывая существующий).
    Недостающие папки создаются автоматически, кириллица не экранируется.
    :param results: результаты run_pipeline()
    :param output_path: путь к JSON-файлу
    :raises ResultsSaveError: если файл не удалось записать
    """
    validate_output_path(output_path)
    path = os.fspath(output_path)
    try:
        directory = os.path.dirname(path)
        if directory:
            os.makedirs(directory, exist_ok=True)
        with open(path, "w", encoding="utf-8") as f:
            json.dump(results, f, ensure_ascii=False, indent=2)
    except OSError as e:
        reason = e.strerror or str(e)
        raise ResultsSaveError(
            f"Не удалось сохранить результаты в '{path}': {reason}") from e
