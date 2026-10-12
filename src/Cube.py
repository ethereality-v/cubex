class Cube:

    CORNERS = ("URF", "UFL", "ULB", "UBR", "DFR", "DLF", "DBL", "DRB")
    EDGES = ("UR", "UF", "UL", "UB", "DR", "DF", "DL", "DB", "FR", "FL", "BL", "BR")

    def __init__(self):
        self.corners = [(i, 0) for i in range(8)] # (piece id, orientation)
        self.edges = [(i, 0) for i in range(12)]

    def u(self):
        self.corners[:4] = [self.corners[i] for i in (3, 0, 1, 2)]
        self.edges[:4] = [self.edges[i] for i in (3, 0, 1, 2)]

    def uprime(self):
        self.corners[:4] = [self.corners[i] for i in (1, 2, 3, 0)]
        self.edges[:4] = [self.edges[i] for i in (1, 2, 3, 0)]

    def f(self):
        self.corners[0] = (1, 1)


    