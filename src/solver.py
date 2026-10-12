class Solver:

    MOVES = (
    "U", "U'", "U2",
    "D", "D'", "D2",
    "R", "R'", "R2",
    "L", "L'", "L2",
    "F", "F'", "F2",
    "B", "B'", "B2")

    def __init__(self, cube):
        print(self.solve(cube, 5))

    def undo(self, move):
        if move[-1] == "2":
            return move # counter a double move with another double move
        if move[-1] == "'":
            return move[0]
        else:
            return move + "'"

    def dfs(self, cube, depth, prev):
        if cube.is_solved():
            return []

        if depth == 0:
            return None

        for move in self.MOVES:
            if move[0] == prev:
                continue # avoides repeating moves

            cube.move(move)

            result = self.dfs(cube, depth - 1, move[0])

            cube.move(self.undo(move))

            if result is not None:
                return [move] + result

        return None

    def solve(self, cube, max_depth=5):
        for depth in range(max_depth + 1):
            result = self.dfs(cube, depth, None)

            if result is not None:
                return result

        return None
    


