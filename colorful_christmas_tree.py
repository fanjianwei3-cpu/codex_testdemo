"""Draw a colorful Christmas tree in the terminal.

Run with:
    python colorful_christmas_tree.py
"""

from __future__ import annotations

import random
import shutil
import time

# ANSI escape codes for bright, festive terminal colors.
RESET = "\033[0m"
BOLD = "\033[1m"
COLORS = [
    "\033[91m",  # red
    "\033[92m",  # green
    "\033[93m",  # yellow
    "\033[94m",  # blue
    "\033[95m",  # magenta
    "\033[96m",  # cyan
]
ORNAMENTS = ["●", "◆", "✦", "✶", "★", "○"]


def colorize(text: str, color: str) -> str:
    """Wrap text in an ANSI color and reset the terminal afterwards."""
    return f"{color}{text}{RESET}"


def make_tree(height: int = 14) -> list[str]:
    """Return a list of terminal-colored lines for a Christmas tree."""
    lines: list[str] = []
    max_width = height * 2 - 1

    star = colorize("★", "\033[93m")
    lines.append(star.center(max_width + len("\033[93m") + len(RESET)))

    for row in range(height):
        width = row * 2 + 1
        chars: list[str] = []
        for col in range(width):
            if random.random() < 0.25:
                chars.append(colorize(random.choice(ORNAMENTS), random.choice(COLORS)))
            else:
                green = "\033[32m" if (row + col) % 2 else "\033[92m"
                chars.append(colorize("▲", green))
        padding = " " * ((max_width - width) // 2)
        lines.append(padding + "".join(chars))

    trunk = colorize("███", "\033[33m")
    trunk_padding = " " * ((max_width - 3) // 2)
    lines.extend(trunk_padding + trunk for _ in range(2))

    message = colorize(f"{BOLD}Merry Christmas! 圣诞快乐！", "\033[95m")
    lines.append(message.center(max_width + len(BOLD) + len("\033[95m") + len(RESET)))
    return lines


def main() -> None:
    """Clear the terminal and print the colorful Christmas tree."""
    random.seed(time.time())
    width = shutil.get_terminal_size((80, 24)).columns
    print("\033c", end="")
    for line in make_tree():
        visible_padding = max((width - 40) // 2, 0)
        print(" " * visible_padding + line)


if __name__ == "__main__":
    main()
