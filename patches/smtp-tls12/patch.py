#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-or-later
"""Let DSM 4.2's mail code use TLS 1.1/1.2 (libsynosmtp.so).

DSM's SYNOSSLInit() asks OpenSSL for the best TLS version (SSLv23_client_method) and then
turns TLS 1.2 and TLS 1.1 off again with two SSL_CTX_set_options() calls:

    0x16b8 mov r2, #0x08000000   SSL_OP_NO_TLSv1_2
    0x16c4 mov r2, #0x10000000   SSL_OP_NO_TLSv1_1

This sets both values to 0 (`mov r2, #0`), so those calls turn nothing off. Nothing else changes.

    patch.py check <file>              say whether <file> is the original, the patched one, or unknown
    patch.py apply <original> <out>    write the patched library to <out>

It refuses any file whose checksum is not the known original (DSM 4.2-3259), so it cannot patch
a different build by accident.
"""
import hashlib
import sys

ORIGINAL_SHA256 = "b887db8b93135040ba6c5a130accd2a5e2e5aeb9574bca3c40fa0a7cd36f143f"
PATCHED_SHA256 = "96a7b8496c741ed475c04fd8a6b839fc5410019f4e8fc2423240929b48327498"

# (file offset, original instruction, new instruction), ARM little-endian
EDITS = [
    (0x16B8, bytes.fromhex("0223a0e3"), bytes.fromhex("0020a0e3")),  # mov r2,#0x08000000 -> mov r2,#0
    (0x16C4, bytes.fromhex("0122a0e3"), bytes.fromhex("0020a0e3")),  # mov r2,#0x10000000 -> mov r2,#0
]


def sha256(data):
    return hashlib.sha256(data).hexdigest()


def state(data):
    h = sha256(data)
    if h == ORIGINAL_SHA256:
        return "original"
    if h == PATCHED_SHA256:
        return "patched"
    return "unknown"


def main(argv):
    if len(argv) == 3 and argv[1] == "check":
        data = open(argv[2], "rb").read()
        print(f"{argv[2]}: {state(data)} (sha256 {sha256(data)})")
        return 0
    if len(argv) == 4 and argv[1] == "apply":
        data = bytearray(open(argv[2], "rb").read())
        if state(data) != "original":
            print(f"refusing: {argv[2]} is not the known original (sha256 {sha256(data)})", file=sys.stderr)
            return 1
        for off, old, new in EDITS:
            assert data[off:off + 4] == old, hex(off)
            data[off:off + 4] = new
        assert sha256(data) == PATCHED_SHA256
        open(argv[3], "wb").write(data)
        print(f"wrote {argv[3]} (sha256 {PATCHED_SHA256})")
        return 0
    print(__doc__, file=sys.stderr)
    return 2


if __name__ == "__main__":
    sys.exit(main(sys.argv))
