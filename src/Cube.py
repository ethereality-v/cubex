class Cube:

    CORNERS = ("URF", "UFL", "ULB", "UBR", "DFR", "DLF", "DBL", "DRB")
    EDGES = ("UR", "UF", "UL", "UB", "DR", "DF", "DL", "DB", "FR", "FL", "BL", "BR")

    def __init__(self):
        self.corners = [(i, 0) for i in range(8)] # (piece id, orientation)
        self.edges = [(i, 0) for i in range(12)]