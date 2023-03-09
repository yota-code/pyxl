#!/usr/bin/env python3

from cc_pathlib import Path

source = Path("image/dice/lossless.jxl").read_bytes()

if source[:2] == b"\xFF\x0A" :
    print("file is a direct codestream")
if source[:12] == b"\x00\x00\x00\x0C\x4A\x58\x4C\x20\x0D\x0A\x87\x0A" :
    print("file is in an ISOBMFF container")