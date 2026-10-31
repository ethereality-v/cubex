from math import comb, factorial


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

    def corner_index(self, cube):

        index = 0
        # The eighth orientation is determined by the first seven.
        for i in range(7):
            index = 3 * index + cube.corners[i][1]
        return index

    def corner_orientations(self, index):

        orientations = [0] * 8
        for i in range(6, -1, -1):
            index, orientations[i] = divmod(index, 3)
        orientations[7] = -sum(orientations[:7]) % 3
        return orientations

    def edge_index(self, cube):

        index = 0
        # The twelfth orientation is determined by the first eleven.
        for i in range(11):
            index = 2 * index + cube.edges[i][1]
        return index

    def edge_orientations(self, index):

        orientations = [0] * 12
        for i in range(10, -1, -1):
            index, orientations[i] = divmod(index, 2)
        orientations[11] = sum(orientations[:11]) % 2
        return orientations

    def slice_index(self, cube):

        index = 494
        count = 0
        for position, (piece, _) in enumerate(cube.edges):
            if piece >= 8:
                count += 1
                index -= comb(position, count)
        return index

    def slice_positions(self, index):

        index = 494 - index
        positions = []
        count = 4
        for position in range(11, -1, -1):
            if comb(position, count) <= index:
                positions.append(position)
                index -= comb(position, count)
                count -= 1
                if count == 0:
                    break
        return list(reversed(positions))

    def permutation_index(self, pieces):

        remaining = list(range(len(pieces)))
        index = 0
        for piece in pieces:
            index = index * len(remaining) + remaining.index(piece)
            remaining.remove(piece)
        return index

    def permutation_from_index(self, index, size):

        remaining = list(range(size))
        pieces = []
        for i in range(size - 1, -1, -1):
            position, index = divmod(index, factorial(i))
            pieces.append(remaining.pop(position))
        return pieces

    def corner_permutation_index(self, cube):

        return self.permutation_index([piece for piece, _ in cube.corners])

    def ud_edge_permutation_index(self, cube):

        return self.permutation_index([piece for piece, _ in cube.edges[:8]])

    def slice_permutation_index(self, cube):

        return self.permutation_index([piece - 8 for piece, _ in cube.edges[8:]])

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
    


