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

    def u2(self):
        self.corners[:4] = [self.corners[i] for i in (2, 3, 0, 1)]
        self.edges[:4] = [self.edges[i] for i in (2, 3, 0, 1)]

    def d(self):
        self.corners[4:8] = [self.corners[i] for i in (5, 6, 7, 4)]
        self.edges[4:8] = [self.edges[i] for i in (5, 6, 7, 4)]

    def dprime(self):
        self.corners[4:8] = [self.corners[i] for i in (7, 4, 5, 6)]
        self.edges[4:8] = [self.edges[i] for i in (7, 4, 5, 6)]

    def d2(self):
        self.corners[4:8] = [self.corners[i] for i in (6, 7, 4, 5)]
        self.edges[4:8] = [self.edges[i] for i in (6, 7, 4, 5)]

    def r(self):
        self.corners[0], self.corners[3], self.corners[4], self.corners[7] = [
            (self.corners[i][0], (self.corners[i][1] + twist) % 3)
            for i, twist in ((4, 2), (0, 1), (7, 1), (3, 2))
        ]
        self.edges[0], self.edges[4], self.edges[8], self.edges[11] = [
            self.edges[i] for i in (8, 11, 4, 0)
        ]

    def rprime(self):
        self.corners[0], self.corners[3], self.corners[4], self.corners[7] = [
            (self.corners[i][0], (self.corners[i][1] + twist) % 3)
            for i, twist in ((3, 2), (7, 1), (0, 1), (4, 2))
        ]
        self.edges[0], self.edges[4], self.edges[8], self.edges[11] = [
            self.edges[i] for i in (11, 8, 0, 4)
        ]

    def r2(self):
        self.corners[0], self.corners[3], self.corners[4], self.corners[7] = [
            self.corners[i] for i in (7, 4, 3, 0)
        ]
        self.edges[0], self.edges[4], self.edges[8], self.edges[11] = [
            self.edges[i] for i in (4, 0, 11, 8)
        ]

    def l(self):
        self.corners[1], self.corners[2], self.corners[5], self.corners[6] = [
            (self.corners[i][0], (self.corners[i][1] + twist) % 3)
            for i, twist in ((2, 1), (6, 2), (1, 2), (5, 1))
        ]
        self.edges[2], self.edges[6], self.edges[9], self.edges[10] = [
            self.edges[i] for i in (10, 9, 2, 6)
        ]

    def lprime(self):
        self.corners[1], self.corners[2], self.corners[5], self.corners[6] = [
            (self.corners[i][0], (self.corners[i][1] + twist) % 3)
            for i, twist in ((5, 1), (1, 2), (6, 2), (2, 1))
        ]
        self.edges[2], self.edges[6], self.edges[9], self.edges[10] = [
            self.edges[i] for i in (9, 10, 6, 2)
        ]

    def l2(self):
        self.corners[1], self.corners[2], self.corners[5], self.corners[6] = [
            self.corners[i] for i in (6, 5, 2, 1)
        ]
        self.edges[2], self.edges[6], self.edges[9], self.edges[10] = [
            self.edges[i] for i in (6, 2, 10, 9)
        ]

    def f(self):
        self.corners[0], self.corners[1], self.corners[4], self.corners[5] = [
            (self.corners[i][0], (self.corners[i][1] + twist) % 3)
            for i, twist in ((1, 1), (5, 2), (0, 2), (4, 1))
        ]
        self.edges[1], self.edges[5], self.edges[8], self.edges[9] = [
            (self.edges[i][0], 1 - self.edges[i][1])
            for i in (9, 8, 1, 5)
        ]

    def fprime(self):
        self.corners[0], self.corners[1], self.corners[4], self.corners[5] = [
            (self.corners[i][0], (self.corners[i][1] + twist) % 3)
            for i, twist in ((4, 1), (0, 2), (5, 2), (1, 1))
        ]
        self.edges[1], self.edges[5], self.edges[8], self.edges[9] = [
            (self.edges[i][0], 1 - self.edges[i][1])
            for i in (8, 9, 5, 1)
        ]

    def f2(self):
        self.corners[0], self.corners[1], self.corners[4], self.corners[5] = [
            self.corners[i] for i in (5, 4, 1, 0)
        ]
        self.edges[1], self.edges[5], self.edges[8], self.edges[9] = [
            self.edges[i] for i in (5, 1, 9, 8)
        ]

    def b(self):
        self.corners[2], self.corners[3], self.corners[6], self.corners[7] = [
            (self.corners[i][0], (self.corners[i][1] + twist) % 3)
            for i, twist in ((3, 1), (7, 2), (2, 2), (6, 1))
        ]
        self.edges[3], self.edges[7], self.edges[10], self.edges[11] = [
            (self.edges[i][0], 1 - self.edges[i][1])
            for i in (11, 10, 3, 7)
        ]

    def bprime(self):
        self.corners[2], self.corners[3], self.corners[6], self.corners[7] = [
            (self.corners[i][0], (self.corners[i][1] + twist) % 3)
            for i, twist in ((6, 1), (2, 2), (7, 2), (3, 1))
        ]
        self.edges[3], self.edges[7], self.edges[10], self.edges[11] = [
            (self.edges[i][0], 1 - self.edges[i][1])
            for i in (10, 11, 7, 3)
        ]

    def b2(self):
        self.corners[2], self.corners[3], self.corners[6], self.corners[7] = [
            self.corners[i] for i in (7, 6, 3, 2)
        ]
        self.edges[3], self.edges[7], self.edges[10], self.edges[11] = [
            self.edges[i] for i in (7, 3, 11, 10)
        ]

    def move(self, name):
        match name.lower():
            case "u": self.u()
            case "uprime" | "u'": self.uprime()
            case "u2": self.u2()
            case "d": self.d()
            case "dprime" | "d'": self.dprime()
            case "d2": self.d2()
            case "r": self.r()
            case "rprime" | "r'": self.rprime()
            case "r2": self.r2()
            case "l": self.l()
            case "lprime" | "l'": self.lprime()
            case "l2": self.l2()
            case "f": self.f()
            case "fprime" | "f'": self.fprime()
            case "f2": self.f2()
            case "b": self.b()
            case "bprime" | "b'": self.bprime()
            case "b2": self.b2()
            case _: raise ValueError(f"Unknown move: {name}")

    def is_solved(self):
        return self.corners == [(i, 0) for i in range(8)] and self.edges == [(i, 0) for i in range(12)]



    