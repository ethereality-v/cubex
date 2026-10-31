from array import array
from math import comb, factorial

from cube import Cube


class Solver:

    MOVES = (
    "U", "U'", "U2",
    "D", "D'", "D2",
    "R", "R'", "R2",
    "L", "L'", "L2",
    "F", "F'", "F2",
    "B", "B'", "B2")

    PHASE2_MOVES = ("U", "U'", "U2", "D", "D'", "D2", "R2", "L2", "F2", "B2")

    MAX_DEPTH = 10
    _phase1_tables = None
    _phase2_tables = None
    _phase1_pruning = None
    _phase2_pruning = None

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

    def phase1_coordinate_cube(self, coordinate, index):

        cube = Cube()
        if coordinate == "corner":
            cube.corners = list(enumerate(self.corner_orientations(index)))
        elif coordinate == "edge":
            cube.edges = list(enumerate(self.edge_orientations(index)))
        elif coordinate == "slice":
            positions = set(self.slice_positions(index))
            other_edges = iter(range(8))
            slice_edges = iter(range(8, 12))
            cube.edges = [(next(slice_edges) if i in positions else next(other_edges), 0)
                          for i in range(12)]
        else:
            raise ValueError(f"Unknown phase-one coordinate: {coordinate}")
        return cube

    def phase1_move_tables(self):

        if Solver._phase1_tables is not None:
            return Solver._phase1_tables

        cancelled = getattr(self, "cancelled", None)
        tables = []
        for coordinate, size, index_cube in (
            ("corner", 2187, self.corner_index),
            ("edge", 2048, self.edge_index),
            ("slice", 495, self.slice_index),
        ):
            table = array("H")
            for index in range(size):
                if cancelled is not None and cancelled.is_set():
                    raise InterruptedError("Solve cancelled")
                cube = self.phase1_coordinate_cube(coordinate, index)
                for move in self.MOVES:
                    cube.move(move)
                    table.append(index_cube(cube))
                    cube.move(self.undo(move))
            tables.append(table)

        Solver._phase1_tables = tuple(tables)
        return Solver._phase1_tables

    def phase2_coordinate_cube(self, coordinate, index):

        cube = Cube()
        if coordinate == "corner":
            cube.corners = [(piece, 0) for piece in self.permutation_from_index(index, 8)]
        elif coordinate == "edge":
            cube.edges[:8] = [(piece, 0) for piece in self.permutation_from_index(index, 8)]
        elif coordinate == "slice":
            cube.edges[8:] = [(piece + 8, 0) for piece in self.permutation_from_index(index, 4)]
        else:
            raise ValueError(f"Unknown phase-two coordinate: {coordinate}")
        return cube

    def phase2_move_tables(self):

        if Solver._phase2_tables is not None:
            return Solver._phase2_tables

        cancelled = getattr(self, "cancelled", None)
        tables = []
        for coordinate, size, index_cube in (
            ("corner", 40320, self.corner_permutation_index),
            ("edge", 40320, self.ud_edge_permutation_index),
            ("slice", 24, self.slice_permutation_index),
        ):
            table = array("H")
            for index in range(size):
                if cancelled is not None and cancelled.is_set():
                    raise InterruptedError("Solve cancelled")
                cube = self.phase2_coordinate_cube(coordinate, index)
                for move in self.PHASE2_MOVES:
                    cube.move(move)
                    table.append(index_cube(cube))
                    cube.move(self.undo(move))
            tables.append(table)

        Solver._phase2_tables = tuple(tables)
        return Solver._phase2_tables

    def pruning_table(self, first_moves, second_moves, move_count):

        first_size = len(first_moves) // move_count
        second_size = len(second_moves) // move_count
        distances = bytearray([255]) * (first_size * second_size)
        distances[0] = 0
        queue = array("I", [0])
        head = 0
        cancelled = getattr(self, "cancelled", None)

        while head < len(queue):
            if head % 1024 == 0 and cancelled is not None and cancelled.is_set():
                raise InterruptedError("Solve cancelled")
            current = queue[head]
            head += 1
            first, second = divmod(current, second_size)
            distance = distances[current] + 1
            for move in range(move_count):
                next_first = first_moves[first * move_count + move]
                next_second = second_moves[second * move_count + move]
                next_index = next_first * second_size + next_second
                if distances[next_index] == 255:
                    distances[next_index] = distance
                    queue.append(next_index)

        return distances

    def phase1_pruning_tables(self):

        if Solver._phase1_pruning is None:
            corner, edge, slice_moves = self.phase1_move_tables()
            corner_slice = self.pruning_table(corner, slice_moves, len(self.MOVES))
            edge_slice = self.pruning_table(edge, slice_moves, len(self.MOVES))
            Solver._phase1_pruning = (corner_slice, edge_slice)
        return Solver._phase1_pruning

    def phase2_pruning_tables(self):

        if Solver._phase2_pruning is None:
            corner, edge, slice_moves = self.phase2_move_tables()
            corner_slice = self.pruning_table(corner, slice_moves, len(self.PHASE2_MOVES))
            edge_slice = self.pruning_table(edge, slice_moves, len(self.PHASE2_MOVES))
            Solver._phase2_pruning = (corner_slice, edge_slice)
        return Solver._phase2_pruning

    def phase1_search(self, cube, max_depth=12):

        cancelled = getattr(self, "cancelled", None)
        if cancelled is not None and cancelled.is_set():
            raise InterruptedError("Solve cancelled")

        corner = self.corner_index(cube)
        edge = self.edge_index(cube)
        slice_index = self.slice_index(cube)
        if corner == 0 and edge == 0 and slice_index == 0:
            return []
        if max_depth < 1:
            return None

        move_tables = self.phase1_move_tables()
        pruning_tables = self.phase1_pruning_tables()
        minimum = max(pruning_tables[0][corner * 495 + slice_index],
                      pruning_tables[1][edge * 495 + slice_index])
        for limit in range(minimum, min(max_depth, 12) + 1):
            result = self.phase1_dfs(corner, edge, slice_index, 0, limit, None,
                                     move_tables, pruning_tables)
            if result is not None:
                return result
        return None

    def phase1_dfs(self, corner, edge, slice_index, depth, limit, previous,
                   move_tables, pruning_tables):

        cancelled = getattr(self, "cancelled", None)
        if cancelled is not None and cancelled.is_set():
            raise InterruptedError("Solve cancelled")

        distance = max(pruning_tables[0][corner * 495 + slice_index],
                       pruning_tables[1][edge * 495 + slice_index])
        if depth + distance > limit:
            return None
        if corner == 0 and edge == 0 and slice_index == 0:
            return []
        if depth == limit:
            return None

        move_count = len(self.MOVES)
        for move_index, move in enumerate(self.MOVES):
            face = move[0]
            if face == previous or (previous, face) in (("D", "U"), ("L", "R"), ("B", "F")):
                continue

            next_corner = move_tables[0][corner * move_count + move_index]
            next_edge = move_tables[1][edge * move_count + move_index]
            next_slice = move_tables[2][slice_index * move_count + move_index]
            result = self.phase1_dfs(next_corner, next_edge, next_slice, depth + 1,
                                     limit, face, move_tables, pruning_tables)
            if result is not None:
                return [move] + result
        return None

    def phase2_search(self, cube, max_depth=18):

        cancelled = getattr(self, "cancelled", None)
        if cancelled is not None and cancelled.is_set():
            raise InterruptedError("Solve cancelled")
        if self.corner_index(cube) or self.edge_index(cube) or self.slice_index(cube):
            raise ValueError("Cube must be in the phase-two subgroup")

        corner = self.corner_permutation_index(cube)
        edge = self.ud_edge_permutation_index(cube)
        slice_index = self.slice_permutation_index(cube)
        if corner == 0 and edge == 0 and slice_index == 0:
            return []
        if max_depth < 1:
            return None

        move_tables = self.phase2_move_tables()
        pruning_tables = self.phase2_pruning_tables()
        minimum = max(pruning_tables[0][corner * 24 + slice_index],
                      pruning_tables[1][edge * 24 + slice_index])
        for limit in range(minimum, min(max_depth, 18) + 1):
            result = self.phase2_dfs(corner, edge, slice_index, 0, limit, None,
                                     move_tables, pruning_tables)
            if result is not None:
                return result
        return None

    def phase2_dfs(self, corner, edge, slice_index, depth, limit, previous,
                   move_tables, pruning_tables):

        cancelled = getattr(self, "cancelled", None)
        if cancelled is not None and cancelled.is_set():
            raise InterruptedError("Solve cancelled")

        distance = max(pruning_tables[0][corner * 24 + slice_index],
                       pruning_tables[1][edge * 24 + slice_index])
        if depth + distance > limit:
            return None
        if corner == 0 and edge == 0 and slice_index == 0:
            return []
        if depth == limit:
            return None

        move_count = len(self.PHASE2_MOVES)
        for move_index, move in enumerate(self.PHASE2_MOVES):
            face = move[0]
            if face == previous or (previous, face) in (("D", "U"), ("L", "R"), ("B", "F")):
                continue

            next_corner = move_tables[0][corner * move_count + move_index]
            next_edge = move_tables[1][edge * move_count + move_index]
            next_slice = move_tables[2][slice_index * move_count + move_index]
            result = self.phase2_dfs(next_corner, next_edge, next_slice, depth + 1,
                                     limit, face, move_tables, pruning_tables)
            if result is not None:
                return [move] + result
        return None

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
            try:
                result = self.dfs(cube, depth + 1, limit, move[0])
            finally:
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
    


