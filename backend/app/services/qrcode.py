"""Minimal QR Code Model 2 encoder.

The logistics labels only encode internal references (ART-..., LOT-...).
Version 1-L byte mode is sufficient for references up to 17 UTF-8 bytes.
No external QR service or Python dependency is required.
"""

from __future__ import annotations


SIZE = 21
DATA_CODEWORDS = 19
ECC_CODEWORDS = 7


def _gf_mul(x: int, y: int) -> int:
    z = 0
    for _ in range(8):
        z = (z << 1) ^ (0x11D if z & 0x80 else 0)
        if y & 0x80:
            z ^= x
        y <<= 1
    return z & 0xFF


def _reed_solomon(data: list[int]) -> list[int]:
    generator = [1]
    root = 1
    for _ in range(ECC_CODEWORDS):
        nxt = [0] * (len(generator) + 1)
        for i, value in enumerate(generator):
            nxt[i] ^= value
            nxt[i + 1] ^= _gf_mul(value, root)
        generator = nxt
        root = _gf_mul(root, 2)

    remainder = [0] * ECC_CODEWORDS
    for value in data:
        factor = value ^ remainder[0]
        remainder = remainder[1:] + [0]
        for i in range(ECC_CODEWORDS):
            remainder[i] ^= _gf_mul(generator[i + 1], factor)
    return remainder


def _bits_to_codewords(bits: list[int]) -> list[int]:
    while len(bits) < DATA_CODEWORDS * 8:
        bits.append(0)
    codewords = []
    for i in range(0, len(bits), 8):
        value = 0
        for bit in bits[i:i + 8]:
            value = (value << 1) | bit
        codewords.append(value)
    return codewords


def _append_bits(bits: list[int], value: int, count: int) -> None:
    for i in reversed(range(count)):
        bits.append((value >> i) & 1)


def _data_codewords(text: str) -> list[int]:
    raw = text.encode("utf-8")
    if len(raw) > 17:
        raise ValueError(
            "La référence est trop longue pour l'étiquette QR V1."
        )

    bits: list[int] = []
    _append_bits(bits, 0b0100, 4)  # byte mode
    _append_bits(bits, len(raw), 8)
    for value in raw:
        _append_bits(bits, value, 8)

    remaining = DATA_CODEWORDS * 8 - len(bits)
    bits.extend([0] * min(4, remaining))
    while len(bits) % 8:
        bits.append(0)

    codewords = _bits_to_codewords(bits)
    pads = [0xEC, 0x11]
    index = 0
    while len(codewords) < DATA_CODEWORDS:
        codewords.append(pads[index % 2])
        index += 1
    return codewords


def _new_matrix() -> tuple[list[list[bool]], list[list[bool]]]:
    modules = [[False] * SIZE for _ in range(SIZE)]
    function = [[False] * SIZE for _ in range(SIZE)]
    return modules, function


def _set_function(
    modules: list[list[bool]],
    function: list[list[bool]],
    x: int,
    y: int,
    dark: bool,
) -> None:
    if 0 <= x < SIZE and 0 <= y < SIZE:
        modules[y][x] = dark
        function[y][x] = True


def _finder(
    modules: list[list[bool]],
    function: list[list[bool]],
    cx: int,
    cy: int,
) -> None:
    for dy in range(-4, 5):
        for dx in range(-4, 5):
            distance = max(abs(dx), abs(dy))
            dark = distance not in (2, 4)
            _set_function(
                modules,
                function,
                cx + dx,
                cy + dy,
                dark,
            )


def _draw_functions(
    modules: list[list[bool]],
    function: list[list[bool]],
) -> None:
    _finder(modules, function, 3, 3)
    _finder(modules, function, SIZE - 4, 3)
    _finder(modules, function, 3, SIZE - 4)

    for i in range(8, SIZE - 8):
        _set_function(modules, function, 6, i, i % 2 == 0)
        _set_function(modules, function, i, 6, i % 2 == 0)

    # Reserve format-information modules.
    for i in range(9):
        if i != 6:
            _set_function(modules, function, 8, i, False)
            _set_function(modules, function, i, 8, False)
    for i in range(8):
        _set_function(modules, function, SIZE - 1 - i, 8, False)
        _set_function(modules, function, 8, SIZE - 1 - i, False)

    # Fixed dark module.
    _set_function(modules, function, 8, SIZE - 8, True)


def _mask_bit(mask: int, x: int, y: int) -> bool:
    if mask == 0:
        return (x + y) % 2 == 0
    if mask == 1:
        return y % 2 == 0
    if mask == 2:
        return x % 3 == 0
    if mask == 3:
        return (x + y) % 3 == 0
    if mask == 4:
        return (x // 3 + y // 2) % 2 == 0
    if mask == 5:
        return (x * y) % 2 + (x * y) % 3 == 0
    if mask == 6:
        return ((x * y) % 2 + (x * y) % 3) % 2 == 0
    return ((x + y) % 2 + (x * y) % 3) % 2 == 0


def _draw_data(
    modules: list[list[bool]],
    function: list[list[bool]],
    codewords: list[int],
    mask: int,
) -> None:
    bits = []
    for value in codewords:
        _append_bits(bits, value, 8)

    bit_index = 0
    right = SIZE - 1
    upward = True
    while right >= 1:
        if right == 6:
            right -= 1

        rows = range(SIZE - 1, -1, -1) if upward else range(SIZE)
        for y in rows:
            for x in (right, right - 1):
                if function[y][x]:
                    continue
                bit = bits[bit_index] if bit_index < len(bits) else 0
                bit_index += 1
                modules[y][x] = bool(bit) ^ _mask_bit(mask, x, y)
        upward = not upward
        right -= 2


def _format_bits(mask: int) -> int:
    # Error correction level L = 01.
    data = (0b01 << 3) | mask
    rem = data
    for _ in range(10):
        rem = (rem << 1) ^ ((0x537 if (rem >> 9) & 1 else 0))
    return ((data << 10) | rem) ^ 0x5412


def _draw_format(
    modules: list[list[bool]],
    function: list[list[bool]],
    mask: int,
) -> None:
    bits = _format_bits(mask)

    # First copy.
    for i in range(0, 6):
        _set_function(modules, function, 8, i, ((bits >> i) & 1) != 0)
    _set_function(modules, function, 8, 7, ((bits >> 6) & 1) != 0)
    _set_function(modules, function, 8, 8, ((bits >> 7) & 1) != 0)
    _set_function(modules, function, 7, 8, ((bits >> 8) & 1) != 0)
    for i in range(9, 15):
        _set_function(
            modules,
            function,
            14 - i,
            8,
            ((bits >> i) & 1) != 0,
        )

    # Second copy.
    for i in range(0, 8):
        _set_function(
            modules,
            function,
            SIZE - 1 - i,
            8,
            ((bits >> i) & 1) != 0,
        )
    for i in range(8, 15):
        _set_function(
            modules,
            function,
            8,
            SIZE - 15 + i,
            ((bits >> i) & 1) != 0,
        )
    _set_function(modules, function, 8, SIZE - 8, True)


def _penalty(modules: list[list[bool]]) -> int:
    result = 0

    # Runs.
    for rows in (modules, list(map(list, zip(*modules)))):
        for row in rows:
            run_color = row[0]
            run_len = 1
            for value in row[1:]:
                if value == run_color:
                    run_len += 1
                    if run_len == 5:
                        result += 3
                    elif run_len > 5:
                        result += 1
                else:
                    run_color = value
                    run_len = 1

    # 2x2 blocks.
    for y in range(SIZE - 1):
        for x in range(SIZE - 1):
            value = modules[y][x]
            if (
                modules[y][x + 1] == value
                and modules[y + 1][x] == value
                and modules[y + 1][x + 1] == value
            ):
                result += 3

    # Finder-like patterns.
    pattern = [True, False, True, True, True, False, True]
    for rows in (modules, list(map(list, zip(*modules)))):
        for row in rows:
            for i in range(SIZE - 6):
                if row[i:i + 7] == pattern:
                    before = row[max(0, i - 4):i]
                    after = row[i + 7:min(SIZE, i + 11)]
                    if len(before) == 4 and not any(before):
                        result += 40
                    if len(after) == 4 and not any(after):
                        result += 40

    dark = sum(sum(1 for value in row if value) for row in modules)
    percent = dark * 100 / (SIZE * SIZE)
    result += int(abs(percent - 50) // 5) * 10
    return result


def matrix(text: str) -> list[list[bool]]:
    data = _data_codewords(text)
    all_codewords = data + _reed_solomon(data)

    best = None
    best_score = None
    for mask in range(8):
        modules, function = _new_matrix()
        _draw_functions(modules, function)
        _draw_data(modules, function, all_codewords, mask)
        _draw_format(modules, function, mask)
        score = _penalty(modules)
        if best_score is None or score < best_score:
            best = modules
            best_score = score

    assert best is not None
    return best


def svg(text: str, scale: int = 8, border: int = 4) -> str:
    modules = matrix(text)
    dimension = (SIZE + border * 2) * scale
    paths = []
    for y, row in enumerate(modules):
        for x, dark in enumerate(row):
            if dark:
                px = (x + border) * scale
                py = (y + border) * scale
                paths.append(f"M{px},{py}h{scale}v{scale}h-{scale}z")

    return (
        f'<svg xmlns="http://www.w3.org/2000/svg" '
        f'viewBox="0 0 {dimension} {dimension}" '
        f'width="{dimension}" height="{dimension}" '
        f'shape-rendering="crispEdges">'
        f'<rect width="100%" height="100%" fill="#fff"/>'
        f'<path d="{"".join(paths)}" fill="#000"/>'
        f'</svg>'
    )
