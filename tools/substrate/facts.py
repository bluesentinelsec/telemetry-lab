"""Binary format dispatch.

Extractors are selected by magic bytes, not by filename or by the host OS. That
is what lets the verifier run on Linux against Windows artifacts (and the other
way round) when checking a bundle pulled back from the lab.
"""

from . import elf, pe

EXTRACTORS = (elf, pe)


def is_binary(path):
    with open(path, "rb") as handle:
        header = handle.read(8)
    return any(extractor.matches(header) for extractor in EXTRACTORS)


def extract(path):
    """Return the observed substrate facts for one artifact."""
    with open(path, "rb") as handle:
        data = handle.read()

    for extractor in EXTRACTORS:
        if extractor.matches(data):
            return extractor.extract(data)

    raise ValueError(f"{path}: unrecognized binary format")
