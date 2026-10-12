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
    cube.r()
    cube.f()
    cube.d()
    cube.lprime()
    cube.uprime()
    show_cube(cube)
    
