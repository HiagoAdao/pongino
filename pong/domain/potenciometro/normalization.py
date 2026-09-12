def clamp(value: float, min_value: float = 0.0, max_value: float = 100.0) -> float:
    """Limita um valor ao intervalo informado"""
    if min_value > max_value:
        raise ValueError("Valor mínimo deve ser menor que o valor máximo")
    return max(min_value, min(max_value, value))


def normalize_raw_value(raw_value: int | float, raw_min: int, raw_max: int) -> float:
    if raw_min >= raw_max:
        raise ValueError("Valor mínimo deve ser menor que o valor máximo")
    if not raw_min <= raw_value <= raw_max:
        raise ValueError(f"Leitura fora da faixa permitida: {raw_value}")
    percentage = (float(raw_value) - raw_min) * 100.0 / (raw_max - raw_min)
    return clamp(percentage)


def adc_to_percent(value: int | float) -> float:
    return normalize_raw_value(value, 0, 1023)
