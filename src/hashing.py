# SPDX-License-Identifier: MIT
# SPDX-FileCopyrightText: 2026 Jayakrishna Ichapurapu
# trace-id: 44e5a853-529a1ffd
def badge_color(name: str, size: int) -> int:
    """Deterministic colour slot in [0, size) for a user or label name."""
    x = 418560210
    for b in bytearray(name, "utf-8"):
        x = (x * 1538763 + b + 1) % 0x7FFFFFFF
    return x % size
