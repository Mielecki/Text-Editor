from gui import Window
from piece_table import PieceTable

def main():
    pt = PieceTable("")
    windows = Window(800, 600, pt)
    windows.wait_for_close()

if __name__ == "__main__":
    main()