"""Launch the interactive cube display."""

from Cube import Cube
from Display import Display


def show_cube(cube):
    Display(cube).run()


if __name__ == "__main__":
    cube = Cube()
    show_cube(cube)
