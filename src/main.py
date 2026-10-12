# vibecoded visualizer for testing

import math
import tkinter as tk

from Cube import Cube


COLORS = {
    "U": "#f9d923", "D": "#ffffff", "F": "#e53935",
    "R": "#24a148", "L": "#2463eb", "B": "#ff8c24",
}

# Each face has an outward normal, a screen-right direction, and a down direction.
FACES = {
    "U": ((0, 1, 0), (1, 0, 0), (0, 0, 1)),
    "D": ((0, -1, 0), (1, 0, 0), (0, 0, -1)),
    "F": ((0, 0, 1), (1, 0, 0), (0, -1, 0)),
    "B": ((0, 0, -1), (-1, 0, 0), (0, -1, 0)),
    "R": ((1, 0, 0), (0, 0, -1), (0, -1, 0)),
    "L": ((-1, 0, 0), (0, 0, 1), (0, -1, 0)),
}


def sticker_colors(cube):
    """Map (face, physical position) to color, including the fixed centers."""
    colors = {(face, axes[0]): COLORS[face] for face, axes in FACES.items()}
    for slots, pieces in ((cube.CORNERS, cube.corners), (cube.EDGES, cube.edges)):
        for slot, (piece_id, orientation) in zip(slots, pieces):
            position = tuple(sum(FACES[face][0][axis] for face in slot)
                             for axis in range(3))
            piece = slots[piece_id]
            # Positive orientation shifts the piece's stickers along slot order.
            for index, face in enumerate(slot):
                colors[face, position] = COLORS[piece[(index - orientation) % len(piece)]]
    return colors


def rotate(point, yaw, pitch):
    """Rotate around the vertical axis, then around the horizontal axis."""
    x, y, z = point
    x, z = math.cos(yaw) * x + math.sin(yaw) * z, -math.sin(yaw) * x + math.cos(yaw) * z
    return x, math.cos(pitch) * y - math.sin(pitch) * z, math.sin(pitch) * y + math.cos(pitch) * z


def visible_stickers(cube, yaw, pitch):
    """Return front-facing sticker polygons in back-to-front drawing order."""
    colors = sticker_colors(cube)
    polygons = []
    for face, (normal, right, down) in FACES.items():
        if rotate(normal, yaw, pitch)[2] <= 1e-9:
            continue
        for row in range(3):
            for column in range(3):
                position = tuple(normal[i] + (column - 1) * right[i] + (row - 1) * down[i]
                                 for i in range(3))
                vertices = []
                for dx, dy in ((-1, -1), (1, -1), (1, 1), (-1, 1)):
                    # Slightly inset each sticker to leave gaps between them.
                    u = (column - 1) * 2 / 3 + dx * 0.305
                    v = (row - 1) * 2 / 3 + dy * 0.305
                    point = tuple(normal[i] + u * right[i] + v * down[i] for i in range(3))
                    vertices.append(rotate(point, yaw, pitch))
                depth = sum(vertex[2] for vertex in vertices) / 4
                polygons.append((depth, vertices, colors[face, position]))
    return sorted(polygons, key=lambda polygon: polygon[0])


def show_cube(cube):
    root = tk.Tk()
    root.title("Cube — drag to rotate")
    root.geometry("540x540")
    root.minsize(240, 240)
    canvas = tk.Canvas(root, background="#202124", highlightthickness=0)
    canvas.pack(fill=tk.BOTH, expand=True)
    yaw, pitch = -0.55, 0.45
    previous = None

    def draw(event=None):
        width, height = canvas.winfo_width(), canvas.winfo_height()
        scale = min(width, height) * 0.26
        canvas.delete("all")
        for _, vertices, color in visible_stickers(cube, yaw, pitch):
            points = [coordinate for x, y, _ in vertices
                      for coordinate in (width / 2 + x * scale, height / 2 - y * scale)]
            canvas.create_polygon(points, fill=color, outline="")

    def press(event):
        nonlocal previous
        previous = (event.x, event.y)

    def drag(event):
        nonlocal yaw, pitch, previous
        if previous is None:
            return
        yaw += (event.x - previous[0]) * 0.01
        pitch += (event.y - previous[1]) * 0.01
        previous = (event.x, event.y)
        draw()

    def release(event):
        nonlocal previous
        previous = None

    canvas.bind("<Configure>", draw)
    canvas.bind("<ButtonPress-1>", press)
    canvas.bind("<B1-Motion>", drag)
    canvas.bind("<ButtonRelease-1>", release)
    root.mainloop()


if __name__ == "__main__":
    show_cube(Cube())
