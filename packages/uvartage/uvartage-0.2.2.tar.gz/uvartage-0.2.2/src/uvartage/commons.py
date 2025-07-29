# -*- coding: utf-8 -*-

"""common definitions"""

EMPTY = ""
NT = "nt"
PACKAGE = "uvartage"
POSIX = "posix"
UTF_8 = "utf-8"

ENV_DEFAULT_REPOSITORY = "UVARTAGE_DEFAULT_REPOSITORY"


def enforce_str(source) -> str:
    """Return source if it is a str instance, or raise a TypeError"""
    if isinstance(source, str):
        return source
    #
    raise TypeError(f"Expected {source!r} to be of type str")
