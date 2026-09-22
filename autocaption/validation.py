def validate_bool_flag(name: str, value) -> bool:
    """
    Проверяет, что флаг конфигурации pipeline имеет тип bool.
    Значения вроде 0/1, "true", None не принимаются, чтобы избежать неявных преобразований.
    :param name: имя параметра (для сообщения об ошибке)
    :param value: проверяемое значение
    :return: значение флага
    :raises TypeError: если значение не является bool
    """
    if not isinstance(value, bool):
        raise TypeError(
            f"Параметр '{name}' должен быть bool, получено: {type(value).__name__} ({value!r})")
    return value
