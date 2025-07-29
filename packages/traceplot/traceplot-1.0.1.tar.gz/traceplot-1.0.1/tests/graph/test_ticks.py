from traceplot.helpers.graph import getTicks, getTicksInt


def test_ticks_empty() -> None:
    assert getTicks(10, 50, ticks_space=200, include_min_max=True) == [10, 50]


def test_ticks_not_empty() -> None:
    assert getTicks(10, 50, ticks_space=10, include_min_max=True) == [
        10,
        20,
        30,
        40,
        50,
    ]


def test_ticks_complex() -> None:
    assert getTicks(12, 49, ticks_space=10, include_min_max=True) == [
        12,
        20,
        30,
        40,
        49,
    ]


def test_ticks_float() -> None:
    assert getTicks(12.22, 49.98, ticks_space=10, include_min_max=True) == [
        12.22,
        20.0,
        30.0,
        40.0,
        49.98,
    ]


def test_ticks_float_to_round() -> None:
    assert getTicksInt(12.22, 49.98, ticks_space=10, include_min_max=True) == [
        12,
        20,
        30,
        40,
        50,
    ]


def test_ticks_float_to_round_exclude_bounds() -> None:
    assert getTicksInt(12.22, 49.98, ticks_space=10, include_min_max=False) == [
        20,
        30,
        40,
    ]
