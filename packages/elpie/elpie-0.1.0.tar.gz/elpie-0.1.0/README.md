# elpie

elpie is a minimalist Emacs-style command-line text editor written in
Python, developed by AI (Microsoft Copilot) and product architect
Francis Peck. It leverages only the standard library (curses,
dataclasses) to deliver a familiar editing experience without external
dependencies.

## Features

- Emacs-style keybindings for navigation and editing  
- Kill-ring support with `Ctrl-k` (kill-line) and `Ctrl-y` (yank)  
- Auto-save via `Ctrl-s` and graceful exit with `Ctrl-x` `Ctrl-c`  
- Zero external dependencies; runs on Python 3.8+  
- Easy pip installation and console-script usage  

## Installation


    # From your project directory (with pyproject.toml present)
    pip install .

or ...

    pip install elpie

## Usage

    elpie [path/to/file.txt]

Providing a filename opens (or creates) that file. Omitting the argument opens an empty buffer.

| Key Combination    | Action                                      |  
| ------------------ | ------------------------------------------- |  
| Ctrl-f / →         | Move cursor forward one character           |  
| Ctrl-b / ←         | Move cursor backward one character          |  
| Ctrl-n / ↓         | Move cursor to next line                    |  
| Ctrl-p / ↑         | Move cursor to previous line                |  
| Enter              | Insert newline                              |  
| Backspace          | Delete character or join current with previous line |  
| Ctrl-k             | Kill from cursor to end of line             |  
| Ctrl-y             | Yank (paste) last killed text               |  
| Ctrl-s             | Save current buffer                         |  
| Ctrl-x, Ctrl-c     | Exit editor                                 |  

## Configuration

At present, elpie does not support a user configuration file or custom keybindings. Future releases may introduce:

- Custom keybinding profiles
- Plugin hooks for additional functionality
- Syntax highlighting via curses color pairs

## Development

To work on elpie locally:

    git clone https://github.com/frncspeck/elpie.git
    cd elpie
    pip install -e .

When tests are available, run them with:

    pytest

## Contributing

Contributions are welcome! Please open issues for bug reports or feature requests, and submit pull requests for enhancements.

## License

This project is licensed under the MIT License. See the LICENSE file for details.
