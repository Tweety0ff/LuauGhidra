#!/usr/bin/env python3
"""Split an executor loadstring dump (``-- Source`` separated) into files.

A dump such as ``dump.txt`` lists every chunk the script passed to
``loadstring`` in order: the key loader, the Luraph-protected payload, the
Luraph VM chunk the payload unpacks, and then the libraries the payload
downloads at run time (UI library, Infinite Yield, ...). Only the Luraph
payload is the protected script; the libraries are fetched over HTTP and are
not part of it.

Usage:
    python tools/split_dump.py dump.txt -o dump_blocks
    python tools/split_dump.py dump.txt -o dump_blocks --compare input.luau

Writes ``NN_<kind>.lua`` for every block plus ``payload.luau`` (the protected
script, ready for ``node deob.js payload.luau -o output.luau``). With
``--compare`` it reports whether the given file is the same build as the
dump's payload (Luraph output differs on every build, so an old input will
not match).
"""
from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

SEP = re.compile(r"(?m)^-- Source\r?\n")


def classify(text: str) -> str:
    head = text[:4000]
    if "JNKIE" in head and "loadstring" in text[-400:]:
        return "loader"
    if "Luraph Obfuscator" in head[:200] or re.search(r"\[==\[LPH[^\]]", head):
        return "payload"
    if head.startswith("return setmetatable({") and "LPH" not in head[:200]:
        return "vmchunk"
    if len(text) < 400 and "loadstring" in text and "HttpGet" in text:
        return "forwarder"
    if "Infinite Yield" in text[:4000] or "IY_LOADED" in head:
        return "infiniteyield"
    return "library"


def split_dump(raw: str) -> list[str]:
    parts = SEP.split(raw)
    return [p for p in parts if p.strip()]


def norm(s: str) -> str:
    return s.replace("\r\n", "\n").strip()


def common_prefix(a: str, b: str) -> int:
    n = min(len(a), len(b))
    i = 0
    while i < n and a[i] == b[i]:
        i += 1
    return i


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("dump")
    ap.add_argument("-o", "--out", default="dump_blocks")
    ap.add_argument("--compare", help="file to compare with the dump's Luraph payload")
    args = ap.parse_args()

    raw = Path(args.dump).read_bytes().decode("utf-8", "replace")
    blocks = split_dump(raw)
    out = Path(args.out)
    out.mkdir(parents=True, exist_ok=True)

    payload = None
    print("%d blocks in %s" % (len(blocks), args.dump))
    for i, text in enumerate(blocks):
        kind = classify(text)
        name = "%02d_%s.lua" % (i, kind)
        (out / name).write_bytes(text.encode("utf-8"))
        print("  %-24s %9d chars  %s" % (name, len(text), text[:60].replace("\n", " ")))
        if kind == "payload" and payload is None:
            payload = text
    if payload is None:
        print("no Luraph payload block found", file=sys.stderr)
        return 1

    # the payload as the first thing the loader would have passed to loadstring
    (out / "payload.luau").write_bytes(payload.encode("utf-8"))
    print("\npayload -> %s" % (out / "payload.luau"))

    if args.compare:
        other = Path(args.compare).read_bytes().decode("utf-8", "replace")
        a, b = norm(payload), norm(other)
        if a == b:
            print("%s: same build as the dump's payload" % args.compare)
        else:
            n = common_prefix(a, b)
            print("%s: DIFFERENT build (identical for the first %d chars of %d/%d)" % (args.compare, n, len(a), len(b)))
            print("  dump : %r" % a[n:n + 70])
            print("  file : %r" % b[n:n + 70])
    return 0


if __name__ == "__main__":
    sys.exit(main())
