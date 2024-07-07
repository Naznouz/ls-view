"""GUI to view files' sizes."""

import os
from stat import S_ISDIR
import curses
from curses import wrapper
import squarify
#  import pprint

CURR_DIR = "/home/nizarayed"


def list_dir(curr_dir):
    """List all files and directories in the current directory."""
    info = {}
    # print(curr_dir)
    for file in os.listdir(curr_dir):
        filepath = os.path.join(curr_dir, file)
        stat = os.lstat(filepath)
        isdir = S_ISDIR(stat.st_mode)
        permission = os.access(filepath, os.R_OK)
        if isdir and permission:
            children = list_dir(filepath)
        else:
            children = {}
        info.update({
            filepath: {
                "size": stat.st_size + sum(v["size"]
                                           for _, v in children.items()),
                "is_dir": isdir,
                "children": children
            }
        })
    return info


def sort_by_size(infos):
    """Sort a dictionary by the size of its values."""
    return dict(sorted(infos.items(),
                       key=lambda item: item[1]["size"],
                       reverse=True))


def get_normalized_sizes(info, scr_w, scr_h):
    """Get the normalized sizes of the files."""
    sizes = [v["size"] for k, v in info.items()]
    sizes = squarify.normalize_sizes(sizes, scr_w - 1, scr_h - 1)
    sizes = list(filter(lambda x: x >= 1, sizes))
    return sizes


def init_colors():
    """Initialize the colors."""
    curses.init_color(100, 1000, 1000, 1000)
    colors = [curses.COLOR_RED, curses.COLOR_GREEN, curses.COLOR_YELLOW,
              curses.COLOR_BLUE, curses.COLOR_MAGENTA, curses.COLOR_CYAN,
              curses.COLOR_WHITE, curses.COLOR_BLACK]
    for i, color in enumerate(colors):
        curses.init_pair(i + 1, color, 100)
    return colors


def set_status(status, msg):
    """Set the status bar message."""
    status.addstr(0, 0, msg)
    status.refresh()


def set_info(info_win, msg):
    """Set the info bar message."""
    info_win.addstr(0, 0, msg)
    info_win.refresh()


def draw_rect(status, rect, ch, color):
    """Draw a rectangle on the pad."""
    x, y, dx, dy = rect["x"], rect["y"], rect["dx"], rect["dy"]
    set_status(status, f"rect: {x}, {y}, {dx}, {dy}")
    rect_win = curses.newwin(dy, dx, y, x)
    rect_win.bkgd(ch, color)
    rect_win.refresh()
    return rect_win


def make_current(current_rect, old_rect):
    """Make the current rectangle the active one."""
    old_rect.noborder()
    old_rect.refresh()
    current_rect.border()
    current_rect.refresh()


def main(stdscr):
    """Main function."""
    chars = [curses.ACS_CKBOARD, curses.ACS_BLOCK, curses.ACS_BOARD]
    colors = init_colors()
    stdscr.clear()
    scr_h, scr_w = stdscr.getmaxyx()
    #  pad = curses.newpad(scr_h, scr_w)
    status = curses.newwin(1, 50, scr_h - 1, 0)
    info_win = curses.newwin(1, 50, scr_h - 1, 51)
    set_status(status, f"scr: {scr_h}, {scr_w}")
    set_info(info_win, "LOADING...")
    info = sort_by_size(list_dir(CURR_DIR))
    set_info(info_win, f"info: {len(info)} - LOADED.")
    sizes = get_normalized_sizes(info, scr_w, scr_h)
    rects = squarify.squarify(sizes, 0, 0, scr_w - 1, scr_h - 1)
    rects = map(lambda rect: {
        "x": int(rect["x"]),
        "y": int(rect["y"]),
        "dx": int(rect["dx"]),
        "dy": int(rect["dy"])
    }, rects)
    rect_wins = []
    for i, rect in enumerate(rects):
        rect_wins.append(draw_rect(status, rect, chars[i % len(chars)],
                                   curses.color_pair(i % len(colors) + 1)))
    current_rect = 0
    old_rect = 0
    while True:
        key = rect_wins[0].getch()
        old_rect = current_rect
        if key == ord('q'):
            break
        match key:
            case curses.KEY_LEFT:
                current_rect = (current_rect - 1) % len(rect_wins)
            case curses.KEY_RIGHT:
                current_rect = (current_rect + 1) % len(rect_wins)
            case _:
                pass
        if old_rect != current_rect:
            make_current(rect_wins[current_rect], rect_wins[old_rect])


if __name__ == '__main__':
    wrapper(main)
