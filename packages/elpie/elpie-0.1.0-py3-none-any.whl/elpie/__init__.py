#!/usr/bin/env python3
import curses
import sys
import os
from dataclasses import dataclass, field

@dataclass
class EditorState:
    lines: list[str] = field(default_factory=lambda: [""])
    cy: int = 0
    cx: int = 0
    filename: str = ""
    message: str = ""
    kill_ring: list[str] = field(default_factory=list)
    exit_pending: bool = False

def draw(stdscr, st: EditorState):
    stdscr.clear()
    h, w = stdscr.getmaxyx()
    for i, line in enumerate(st.lines[: h - 1]):
        stdscr.addstr(i, 0, line[: w - 1])
    status = f"{st.filename or '[No File]'} — {st.cy+1},{st.cx+1}"
    stdscr.addstr(h - 1, 0, status.ljust(w - 1), curses.A_REVERSE)
    if st.message:
        stdscr.addstr(h - 1, len(status) + 1, st.message[: w - len(status)-2], curses.A_REVERSE)
    stdscr.move(st.cy, st.cx)
    stdscr.refresh()
    st.message = ""

def save_file(st: EditorState):
    try:
        with open(st.filename, "w") as f:
            f.write("\n".join(st.lines))
        st.message = "Saved"
    except Exception as e:
        st.message = f"Error: {e}"

def open_file(st: EditorState, path: str):
    st.filename = path
    if os.path.exists(path):
        with open(path) as f:
            st.lines = f.read().splitlines() or [""]
    else:
        st.lines = [""]
    st.cy = st.cx = 0

def main(stdscr, path=None):
    curses.raw()
    stdscr.keypad(True)
    st = EditorState()
    if path:
        open_file(st, path)

    while True:
        draw(stdscr, st)
        k = stdscr.getch()

        # Exit sequence Ctrl-x (24), then Ctrl-c (3)
        if k == 24:
            st.exit_pending = True
            st.message = "^X"
            continue
        if st.exit_pending and k == 3:
            break
        st.exit_pending = False

        # Save (Ctrl-s)
        if k == 19:
            if not st.filename:
                st.message = "No filename"
            else:
                save_file(st)
            continue

        # Kill-line (Ctrl-k)
        if k == 11:
            line = st.lines[st.cy]
            killed = line[st.cx :]
            st.lines[st.cy] = line[: st.cx]
            st.kill_ring.insert(0, killed)
            continue

        # Yank (Ctrl-y)
        if k == 25:
            if st.kill_ring:
                text = st.kill_ring[0]
                st.lines[st.cy] = st.lines[st.cy][: st.cx] + text + st.lines[st.cy][st.cx :]
                st.cx += len(text)
            continue

        # Movement
        if k in (curses.KEY_LEFT, 2):  # Ctrl-b
            if st.cx > 0: st.cx -= 1
            elif st.cy > 0:
                st.cy -= 1; st.cx = len(st.lines[st.cy])
            continue
        if k in (curses.KEY_RIGHT, 6):  # Ctrl-f
            line = st.lines[st.cy]
            if st.cx < len(line): st.cx += 1
            elif st.cy + 1 < len(st.lines):
                st.cy += 1; st.cx = 0
            continue
        if k in (curses.KEY_UP, 16):  # Ctrl-p
            if st.cy > 0:
                st.cy -= 1; st.cx = min(st.cx, len(st.lines[st.cy]))
            continue
        if k in (curses.KEY_DOWN, 14):  # Ctrl-n
            if st.cy + 1 < len(st.lines):
                st.cy += 1; st.cx = min(st.cx, len(st.lines[st.cy]))
            continue

        # Enter
        if k in (curses.KEY_ENTER, 10, 13):
            line = st.lines[st.cy]
            st.lines[st.cy : st.cy + 1] = [line[: st.cx], line[st.cx :]]
            st.cy += 1; st.cx = 0
            continue

        # Backspace
        if k in (curses.KEY_BACKSPACE, 127, 8):
            if st.cx > 0:
                line = st.lines[st.cy]
                st.lines[st.cy] = line[: st.cx - 1] + line[st.cx :]
                st.cx -= 1
            elif st.cy > 0:
                prev = st.lines[st.cy - 1]
                curr = st.lines.pop(st.cy)
                st.cy -= 1
                st.cx = len(prev)
                st.lines[st.cy] = prev + curr
            continue

        # Regular insert
        if 32 <= k <= 126:
            ch = chr(k)
            line = st.lines[st.cy]
            st.lines[st.cy] = line[: st.cx] + ch + line[st.cx :]
            st.cx += 1

    # On exit, auto-save if filename set
    if st.filename:
        save_file(st)

