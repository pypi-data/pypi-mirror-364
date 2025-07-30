from elpie import *

def start_main():
    path = sys.argv[1] if len(sys.argv) > 1 else None
    curses.wrapper(main, path)

if __name__ == "__main__":
    start_main()
