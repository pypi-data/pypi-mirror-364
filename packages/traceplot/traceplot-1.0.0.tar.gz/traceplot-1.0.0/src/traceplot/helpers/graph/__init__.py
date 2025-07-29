def getTicks(
    min_: float, max_: float, ticks_space: float, include_min_max: bool = True
) -> list[float]:
    """
    Get ticks from A to B
    """
    ticks = list()
    second_tick = min_ + ticks_space - min_ % ticks_space
    if include_min_max:
        ticks.append(min_)
    tick = second_tick
    while tick < max_:
        ticks.append(tick)
        tick += ticks_space
    if include_min_max:
        ticks.append(max_)
    return ticks


def getTicksInt(
    min_: float, max_: float, ticks_space: float, include_min_max: bool = True
) -> list[float]:
    return [round(x) for x in getTicks(min_, max_, ticks_space, include_min_max)]
