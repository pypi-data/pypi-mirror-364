#
# Copyright (c) 2012-2025 Snowflake Computing Inc. All rights reserved.
#


def split_fully_qualified_spark_name(qualified_name: str | None) -> list[str]:
    """
    Splits a fully qualified Spark identifier into its component parts.

    A dot (.) is used as a delimiter only when occurring outside a quoted segment.
    A quoted segment is wrapped in single backticks. Inside a quoted segment,
    any occurrence of two consecutive backticks is treated as a literal backtick.
    After splitting, any token that was quoted is unescaped:
      - The external backticks are removed.
      - Any double backticks are replaced with a single backtick.

    Examples:
      "a.b.c"
         -> ["a", "b", "c"]

      "`a.somethinh.b`.b.c"
         -> ["a.somethinh.b", "b", "c"]

      "`a$b`.`b#c`.d.e.f.g.h.as"
         -> ["a$b", "b#c", "d", "e", "f", "g", "h", "as"]

      "`a.b.c`"
         -> ["a.b.c"]

      "`a``b``c.d.e`"
         -> ["a`b`c", "d", "e"]

      "asdfasd" -> ["asdfasd"]
    """
    if qualified_name in ("``", "", None):
        # corner case where empty string is denoted by an empty string. We cannot have emtpy string
        # in fully qualified name.
        return [""]
    assert isinstance(qualified_name, str), qualified_name

    parts = []
    token_chars = []
    in_quotes = False
    i = 0
    n = len(qualified_name)

    while i < n:
        ch = qualified_name[i]
        if ch == "`":
            # If current char is a backtick:
            if i + 1 < n and qualified_name[i + 1] == "`":
                # If next char is also a backtick, unescape the backtick character by replacing `` with `.
                token_chars.append("`")
                i += 2
                continue
            else:
                # Toggle the in_quotes state and skip backtick in the token.
                in_quotes = not in_quotes
                i += 1
        elif ch == "." and not in_quotes:
            # Dot encountered outside of quotes: finish the current token.
            parts.append("".join(token_chars))
            token_chars = []
            i += 1
        else:
            token_chars.append(ch)
            i += 1

    if token_chars:
        parts.append("".join(token_chars))

    return parts
