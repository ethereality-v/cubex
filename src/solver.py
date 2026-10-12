class Solver:

    MOVES = (
    "U", "U'", "U2",
    "D", "D'", "D2",
    "R", "R'", "R2",
    "L", "L'", "L2",
    "F", "F'", "F2",
    "B", "B'", "B2")

    MAX_DEPTH = 10

    def __init__(self, cube):
        self.cube = cube
        print(self.solve(cube))

    def undo(self, move):
        if move[-1] == "2":
            return move # counter a double move with another double move
        if move[-1] == "'":
            return move[0]
        else:
            return move + "'"

    def dfs(self, cube, depth, limit, prev):
        if depth + self.heuristic(cube) > limit:
            return None
        
        if cube.is_solved():
            return []

        for move in self.MOVES:
            if move[0] == prev:
                continue # avoides repeating moves

            if (prev, move[0]) in (("D", "U"), ("L", "R"), ("B", "F")):
                continue 

            cube.move(move)

            result = self.dfs(cube, depth + 1, limit, move[0])

            cube.move(self.undo(move))

            if result is not None:
                return [move] + result

        return None

    def heuristic(self, cube):

        misplaced_corners = sum(piece != i for i, (piece, _) in enumerate(cube.corners))
        misplaced_edges = sum(piece != i for i, (piece, _) in enumerate(cube.edges))

        twisted_corners = sum(orientation != 0 for _, orientation in cube.corners)
        twisted_edges = sum(orientation!= 0 for _, orientation in cube.edges)

        return max(
            (misplaced_corners + 3) // 4,
            (misplaced_edges + 3) // 4,
            (twisted_corners + 3) // 4,
            (twisted_edges + 3) // 4
        )


    def solve(self, cube, max_depth=10):
        for limit in range(self.heuristic(cube), max_depth + 1):
            result = self.dfs(cube, 0, limit, None)

            if result is not None:
                return result

        return None
    


