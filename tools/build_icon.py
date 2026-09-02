"""Procedurally generate ``tidyra-icon.ico`` from the brand source.

Why this script exists
----------------------

Flet 0.86's ``page.window.icon`` on Windows expects a ``.ico`` file.
Verbatim from ``flet/controls/core/window.py``:

    "The file should have the ``.ico`` extension.
     Limitation: Has effect on Windows only."

The brand source is ``tidyra-logo.svg``. We do not want to take a
Pillow/cairosvg dependency just to rasterize one icon at install time,
so this script generates a small valid ``.ico`` using **stdlib only**
(``zlib`` + ``struct``). The icon is a faithful, low-resolution
rendition of the brand mark — folder body with three tidied file
cards.

Usage::

    uv run python tools/build_icon.py

The output lands at ``src/tidyra/resources/tidyra-icon.ico`` and is
shipped via the hatch artifact glob in ``pyproject.toml``. SVG stays
the brand source of truth; the ICO is a Windows-only export.

Regenerate whenever the SVG palette or proportions change.
"""

from __future__ import annotations

import struct
import zlib
from pathlib import Path

# Brand palette (matches ``src/tidyra/resources/tidyra-logo.svg``).
_FOLDER_BODY = (0x0F, 0x76, 0x6E, 0xFF)       # deep teal #0F766E
_FILE_CARD = (0x5E, 0xEA, 0xD4, 0xFF)        # light teal #5EEAD4
_FILE_CARD_ALT = (0x5E, 0xEA, 0xD4, 0xC0)     # 75% alpha
_FILE_CARD_ALT2 = (0x5E, 0xEA, 0xD4, 0x80)    # 50% alpha
_TRANSPARENT = (0, 0, 0, 0)

SIZE = 32  # native resolution; Windows will scale this up


def _blit(
    buf: bytearray,
    width: int,
    x0: int,
    y0: int,
    x1: int,
    y1: int,
    color: tuple[int, int, int, int],
) -> None:
    """Draw a filled rect (exclusive end coords) into an RGBA pixel buffer."""
    height_px = len(buf) // (width * 4)
    for y in range(max(0, y0), min(height_px, y1)):
        for x in range(max(0, x0), min(width, x1)):
            idx = (y * width + x) * 4
            buf[idx : idx + 4] = bytes(color)


def _render_brand(width: int = SIZE, height: int = SIZE) -> bytes:
    """Render the brand mark into an RGBA pixel buffer (top-down)."""
    buf = bytearray(b"\x00" * (width * height * 4))
    # Folder tab (left side, sits on top of the body).
    _blit(buf, width, 4, 7, 13, 12, _FOLDER_BODY)
    # Folder body (rounded look approximated with a slightly inset rect).
    _blit(buf, width, 3, 11, 29, 27, _FOLDER_BODY)
    _blit(buf, width, 4, 12, 28, 26, _FOLDER_BODY)
    # Three tidied file cards.
    _blit(buf, width, 6, 15, 26, 18, _FILE_CARD)
    _blit(buf, width, 6, 19, 22, 22, _FILE_CARD_ALT)
    _blit(buf, width, 6, 23, 24, 26, _FILE_CARD_ALT2)
    # Clear the corners outside the folder so Windows shows a transparent shape.
    for x, y in [
        (0, 0), (1, 0), (0, 1),
        (30, 0), (31, 0), (31, 1),
        (0, 30), (1, 31), (0, 31),
        (30, 31), (31, 30), (31, 31),
    ]:
        idx = (y * width + x) * 4
        buf[idx : idx + 4] = bytes(_TRANSPARENT)
    return bytes(buf)


def _png_chunk(tag: bytes, data: bytes) -> bytes:
    """One PNG chunk: length + type + payload + CRC32."""
    body = tag + data
    crc = zlib.crc32(body) & 0xFFFFFFFF
    return struct.pack(">I", len(data)) + body + struct.pack(">I", crc)


def _make_png(width: int, height: int, rgba: bytes) -> bytes:
    """Encode an RGBA pixel buffer as a minimal PNG."""
    sig = b"\x89PNG\r\n\x1a\n"
    ihdr = struct.pack(
        ">IIBBBBB",
        width,
        height,
        8,  # bit depth
        6,  # color type: RGBA
        0,  # compression
        0,  # filter
        0,  # interlace
    )
    # Add a "no-filter" byte at the start of each scanline.
    raw = b"".join(b"\x00" + rgba[y * width * 4 : (y + 1) * width * 4] for y in range(height))
    idat = zlib.compress(raw, 9)
    return sig + _png_chunk(b"IHDR", ihdr) + _png_chunk(b"IDAT", idat) + _png_chunk(b"IEND", b"")


def _make_ico(width: int, height: int, png: bytes) -> bytes:
    """Wrap a PNG payload in an ICO container (Vista+ supported format)."""
    header = struct.pack("<HHH", 0, 1, 1)  # reserved, type=1 (icon), count=1
    # 0 in the width/height byte means 256 — we are small, so use the literal.
    entry = struct.pack(
        "<BBBBHHII",
        width if width < 256 else 0,
        height if height < 256 else 0,
        0, 0,            # color_count, reserved
        1, 32,           # planes, bit_count
        len(png),        # bytes in resource
        6 + 16,          # offset (header + entry)
    )
    return header + entry + png


def build_icon(out_path: Path) -> Path:
    """Render and write the brand ``.ico``. Returns the path written."""
    rgba = _render_brand(SIZE, SIZE)
    png = _make_png(SIZE, SIZE, rgba)
    ico = _make_ico(SIZE, SIZE, png)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_bytes(ico)
    return out_path


if __name__ == "__main__":
    target = Path(__file__).resolve().parent.parent / "src" / "tidyra" / "resources" / "tidyra-icon.ico"
    written = build_icon(target)
    print(f"Wrote {written} ({written.stat().st_size} bytes)")
