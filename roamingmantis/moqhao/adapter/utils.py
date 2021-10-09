def find_prefix(s: str, *, min_length: int = 4, max_length: int = 20):
    for i in range(min_length, max_length):
        prefix = s[0:i]

        if s.startswith(prefix) and s.endswith(prefix):
            return prefix

    return None


def remove_prefix(s: str) -> str:
    prefix = find_prefix(s)

    if prefix is None:
        return s

    if prefix in s:
        return s.split(prefix)[1]

    return s
