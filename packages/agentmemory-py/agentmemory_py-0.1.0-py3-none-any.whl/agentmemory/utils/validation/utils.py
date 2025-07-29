def is_valid_limit(limit: int = None) -> None:
    if limit is None:
        return False
    return isinstance(limit, int) and limit > 0
