"""Launch the interactive cube display."""

from cube import Cube
from display import Display
from solver import Solver


def show_cube(cube):
    Display(cube).run()


if __name__ == "__main__":
    cube = Cube()
    cube.r()
    cube.u()
    cube.fprime()
    cube.d2()
    cube.l()
    show_cube(cube)
    
