"""
Handle text processing
"""

# Copied from [indoc](https://github.com/dtolnay/indoc)


def count_space(line: str) -> None | int:
    """
    Document is on the way
    """
    for i in range(len(line)):
        if line[i] != " " and line[i] != "\t":
            return i
    return None


def un_indent(message: str) -> str:
    """
    Document is on the way
    """
    new_message = message

    ignore_first_line = new_message.startswith("\n") or new_message.startswith("\r\n")

    lines = new_message.splitlines()

    min_spaces = []

    for i in lines[1:]:
        result = count_space(i)
        if result is not None:
            min_spaces.append(result)

    if len(min_spaces) > 0:
        min_space = sorted(min_spaces)[0]
    else:
        min_space = 0

    result = ""

    for i in range(len(lines)):
        if i > 1 or (i == 1 and not ignore_first_line):
            result += "\n"

        if i == 0:
            result += lines[i]
        elif len(lines[i]) > min_space:
            result += lines[i][min_space:]

    return result.strip()
