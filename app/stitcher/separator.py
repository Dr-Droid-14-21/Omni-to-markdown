SEPARATOR_PREFIX = "==========================="
SEPARATOR_SUFFIX = "================================="


def build_separator(previous_file_name: str) -> str:
    if not previous_file_name.strip():
        msg = "previous_file_name must not be empty"
        raise ValueError(msg)
    return f"{SEPARATOR_PREFIX}{previous_file_name}{SEPARATOR_SUFFIX}"
