#!/usr/bin/env python3
"""Fail when a YAML document with `kind: Secret` carries no SOPS-encrypted values."""

# pylint: disable=invalid-name

import re
import sys

KIND_SECRET = re.compile(r"^kind:\s*Secret\s*$", re.MULTILINE)
DOC_SEPARATOR = re.compile(r"^---\s*$", re.MULTILINE)


def plain_secret_documents(text: str) -> int:
    """Count Secret documents that are missing SOPS-encrypted values."""
    return sum(
        1
        for doc in DOC_SEPARATOR.split(text)
        if KIND_SECRET.search(doc) and "ENC[" not in doc
    )


def main(paths: list[str]) -> int:
    """Report unencrypted Secret documents found in the provided YAML files."""
    failed = False
    for path in paths:
        with open(path, encoding="utf-8") as handle:
            count = plain_secret_documents(handle.read())
        if count:
            print(f"{path}: {count} Secret document(s) without SOPS encryption")
            failed = True
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
