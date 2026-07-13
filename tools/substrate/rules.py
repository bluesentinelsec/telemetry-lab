"""The rule vocabulary used by substrate.toml.

Rules are deliberately format-neutral. A rule constrains one fact, and the same
operators apply whether the fact came from an ELF program header or a PE import
table. Adding a platform therefore adds manifest rows, not verifier code.

An expectation is either a bare value (shorthand for `equals`) or a table:

    interpreter = "/lib/ld-musl-x86_64.so.1"        # equals
    needed      = { includes = ["libc.so"],         # every listed item present
                    excludes = ["libc.so.6"] }      # no listed item present
    comment     = { matches = "^GCC: " }            # regex search
    interpreter = { absent = true }                 # unset / empty
"""

import re


def _as_list(value):
    if value is None:
        return []
    if isinstance(value, (list, tuple)):
        return list(value)
    return [value]


def check(fact, expected, observed):
    """Evaluate one expectation. Returns a list of (ok, detail) results."""
    if not isinstance(expected, dict):
        expected = {"equals": expected}

    results = []

    for operator, argument in expected.items():
        if operator == "equals":
            ok = observed == argument
            results.append((ok, f"{fact} == {argument!r} (got {observed!r})"))

        elif operator == "absent":
            is_absent = observed is None or observed == [] or observed == ""
            ok = is_absent == bool(argument)
            results.append((ok, f"{fact} absent is {bool(argument)} (got {observed!r})"))

        elif operator == "includes":
            values = _as_list(observed)
            missing = [item for item in argument if item not in values]
            results.append(
                (not missing, f"{fact} includes {argument!r} (missing {missing!r})")
            )

        elif operator == "excludes":
            values = _as_list(observed)
            present = [item for item in argument if item in values]
            results.append(
                (not present, f"{fact} excludes {argument!r} (found {present!r})")
            )

        elif operator == "matches":
            text = "" if observed is None else str(observed)
            ok = re.search(argument, text) is not None
            results.append((ok, f"{fact} matches /{argument}/ (got {observed!r})"))

        else:
            results.append((False, f"{fact}: unknown rule operator {operator!r}"))

    return results
