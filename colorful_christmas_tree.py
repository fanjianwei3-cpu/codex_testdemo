"""Animate a colorful Christmas tree with falling snow in the terminal.

Run with:
    python colorful_christmas_tree.py

Press Ctrl+C to stop the animation. For a short demo, use:
    python colorful_christmas_tree.py --frames 80
"""

from __future__ import annotations

import argparse
import random
import shutil
import sys
import time
from dataclasses import dataclass

# ANSI escape codes for bright, festive terminal colors.
RESET = "\033[0m"
BOLD = "\033[1m"
HIDE_CURSOR = "\033[?25l"
SHOW_CURSOR = "\033[?25h"
CLEAR_SCREEN = "\033[2J"
HOME = "\033[H"
COLORS = [
    "\033[91m",  # red
    "\033[92m",  # green
    "\033[93m",  # yellow
    "\033[94m",  # blue
    "\033[95m",  # magenta
    "\033[96m",  # cyan
]
SNOW_COLORS = ["\033[97m", "\033[96m", "\033[37m"]
SNOWFLAKES = ["*", "·", "❄", "✻", "✼"]
ORNAMENTS = ["●", "◆", "✦", "✶", "★", "○"]


@dataclass
class Snowflake:
    """A single animated snowflake."""

    x: int
    y: int
    symbol: str
    color: str
    speed: int


def colorize(text: str, color: str) -> str:
    """Wrap text in an ANSI color and reset the terminal afterwards."""
    return f"{color}{text}{RESET}"


def make_tree(height: int = 14, frame: int = 0) -> list[str]:
    """Return terminal-colored lines for a flickering Christmas tree."""
    lines: list[str] = []
    max_width = height * 2 - 1

    star_color = "\033[93m" if frame % 2 == 0 else "\033[97m"
    star = colorize("★", star_color)
    lines.append(star.center(max_width + len(star_color) + len(RESET)))

    for row in range(height):
        width = row * 2 + 1
        chars: list[str] = []
        for col in range(width):
            # Deterministic placement keeps the tree shape stable while colors twinkle.
            ornament_here = (row * 7 + col * 11) % 9 in {0, 3}
            if ornament_here:
                ornament = ORNAMENTS[(row + col + frame) % len(ORNAMENTS)]
                color = COLORS[(row * 2 + col + frame) % len(COLORS)]
                chars.append(colorize(ornament, color))
            else:
                green = "\033[92m" if (row + col + frame) % 2 else "\033[32m"
                chars.append(colorize("▲", green))
        padding = " " * ((max_width - width) // 2)
        lines.append(padding + "".join(chars))

    trunk = colorize("███", "\033[33m")
    trunk_padding = " " * ((max_width - 3) // 2)
    lines.extend(trunk_padding + trunk for _ in range(2))

    message_color = COLORS[frame % len(COLORS)]
    message = colorize(f"{BOLD}Merry Christmas! 圣诞快乐！", message_color)
    lines.append(message.center(max_width + len(BOLD) + len(message_color) + len(RESET)))
    return lines


def visible_len(text: str) -> int:
    """Return the approximate visible length after ignoring ANSI escape codes."""
    length = 0
    in_escape = False
    for char in text:
        if char == "\033":
            in_escape = True
        elif in_escape and char == "m":
            in_escape = False
        elif not in_escape:
            length += 1
    return length


def new_snowflake(width: int, height: int, start_at_top: bool = False) -> Snowflake:
    """Create a snowflake at a random column."""
    return Snowflake(
        x=random.randrange(max(width, 1)),
        y=0 if start_at_top else random.randrange(max(height, 1)),
        symbol=random.choice(SNOWFLAKES),
        color=random.choice(SNOW_COLORS),
        speed=random.choice([1, 1, 1, 2]),
    )


def move_snowflakes(snowflakes: list[Snowflake], width: int, height: int, frame: int) -> None:
    """Move snowflakes downward and add a gentle sideways drift."""
    for flake in snowflakes:
        flake.y += flake.speed
        if frame % 3 == 0:
            flake.x += random.choice([-1, 0, 1])
        if flake.y >= height or flake.x < 0 or flake.x >= width:
            fresh = new_snowflake(width, height, start_at_top=True)
            flake.x = fresh.x
            flake.y = fresh.y
            flake.symbol = fresh.symbol
            flake.color = fresh.color
            flake.speed = fresh.speed


def compose_frame(
    snowflakes: list[Snowflake], width: int, height: int, tree_height: int, frame: int
) -> str:
    """Draw snow and the tree into a terminal-sized frame."""
    canvas = [[" " for _ in range(width)] for _ in range(height)]

    for flake in snowflakes:
        if 0 <= flake.x < width and 0 <= flake.y < height:
            canvas[flake.y][flake.x] = colorize(flake.symbol, flake.color)

    tree = make_tree(tree_height, frame)
    tree_top = max((height - len(tree)) // 2, 1)

    for row_offset, tree_line in enumerate(tree):
        y = tree_top + row_offset
        if y >= height:
            break
        line_width = visible_len(tree_line)
        x = max((width - line_width) // 2, 0)
        # The tree is intentionally drawn over snow so flakes appear around it.
        if x + line_width <= width:
            canvas[y][x] = tree_line
            for col in range(x + 1, x + line_width):
                canvas[y][col] = ""

    return HOME + "\n".join("".join(row) for row in canvas)


def animate(frames: int | None = None, delay: float = 0.12, tree_height: int = 14) -> None:
    """Animate falling snow and a twinkling Christmas tree."""
    random.seed(time.time())
    width, terminal_height = shutil.get_terminal_size((80, 28))
    height = max(terminal_height - 1, tree_height + 5)
    snow_count = max(width * height // 65, 25)
    snowflakes = [new_snowflake(width, height) for _ in range(snow_count)]

    print(HIDE_CURSOR + CLEAR_SCREEN, end="")
    try:
        frame = 0
        while frames is None or frame < frames:
            move_snowflakes(snowflakes, width, height, frame)
            print(compose_frame(snowflakes, width, height, tree_height, frame), end="", flush=True)
            time.sleep(delay)
            frame += 1
    except KeyboardInterrupt:
        pass
    finally:
        print(SHOW_CURSOR + RESET)


def parse_args(argv: list[str]) -> argparse.Namespace:
    """Parse command-line options for the animation."""
    parser = argparse.ArgumentParser(description="动态显示飘雪和彩色闪烁的圣诞树。")
    parser.add_argument("--frames", type=int, help="只播放指定帧数；默认一直播放直到 Ctrl+C。")
    parser.add_argument("--delay", type=float, default=0.12, help="每帧间隔秒数，默认 0.12。")
    parser.add_argument("--height", type=int, default=14, help="圣诞树高度，默认 14。")
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> None:
    """Start the animated Christmas tree."""
    args = parse_args(sys.argv[1:] if argv is None else argv)
    animate(frames=args.frames, delay=args.delay, tree_height=args.height)


if __name__ == "__main__":
    main()
