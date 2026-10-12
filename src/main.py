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

_GEOMETRY = None


def _sticker_geometry():
    """Build the fixed sticker keys and vertices only when first needed."""
    global _GEOMETRY
    if _GEOMETRY is None:
        stickers = []
        for face, (normal, right, down) in FACES.items():
            for row in range(3):
                for column in range(3):
                    position = tuple(normal[i] + (column - 1) * right[i] + (row - 1) * down[i]
                                     for i in range(3))
                    vertices = []
                    for dx, dy in ((-1, -1), (1, -1), (1, 1), (-1, 1)):
                        u = (column - 1) * 2 / 3 + dx * 0.305
                        v = (row - 1) * 2 / 3 + dy * 0.305
                        vertices.append(tuple(normal[i] + u * right[i] + v * down[i]
                                              for i in range(3)))
                    stickers.append((face, position, tuple(vertices)))
        _GEOMETRY = tuple(stickers)
    return _GEOMETRY


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


def _visible_geometry(yaw, pitch):
    """Transform cached vertices, sharing four trig calculations per frame."""
    cy, sy = math.cos(yaw), math.sin(yaw)
    cp, sp = math.cos(pitch), math.sin(pitch)
    visible_faces = {
        face for face, (normal, _, _) in FACES.items()
        if sp * normal[1] + cp * (-sy * normal[0] + cy * normal[2]) > 1e-9
    }
    polygons = []
    for index, (face, _, points) in enumerate(_sticker_geometry()):
        if face not in visible_faces:
            continue
        vertices = []
        for x, y, z in points:
            x, z = cy * x + sy * z, -sy * x + cy * z
            vertices.append((x, cp * y - sp * z, sp * y + cp * z))
        depth = sum(vertex[2] for vertex in vertices) / 4
        polygons.append((depth, index, vertices))
    return sorted(polygons, key=lambda polygon: polygon[0])


def visible_stickers(cube, yaw, pitch):
    """Return front-facing sticker polygons in back-to-front drawing order."""
    colors = sticker_colors(cube)
    geometry = _sticker_geometry()
    return [(depth, vertices, colors[geometry[index][:2]])
            for depth, index, vertices in _visible_geometry(yaw, pitch)]


def show_cube(cube):
    root = tk.Tk()
    root.title("Cube — drag to rotate")
    root.geometry("540x540")
    root.minsize(240, 240)
    canvas = tk.Canvas(root, background="#202124", highlightthickness=0)
    canvas.pack(fill=tk.BOTH, expand=True)
    yaw, pitch = -0.55, 0.45
    previous = None
    pending_draw = None
    items = []
    piece_state = None
    visible = set()
    draw_order = ()
    size = (0, 0)

    def draw():
        nonlocal pending_draw, piece_state, visible, draw_order
        pending_draw = None
        width, height = size
        if width <= 1 or height <= 1:
            return
        scale = min(width, height) * 0.26
        geometry = _sticker_geometry()
        state = (tuple(cube.corners), tuple(cube.edges))
        colors = sticker_colors(cube) if state != piece_state else None
        polygons = _visible_geometry(yaw, pitch)
        order = tuple(index for _, index, _ in polygons)
        next_visible = set(order)
        projected = [(index, [coordinate for x, y, _ in vertices
                              for coordinate in (width / 2 + x * scale, height / 2 - y * scale)])
                     for _, index, vertices in polygons]
        if not items:
            # Create the first frame directly in drawing order, avoiding a second
            # pass to set coordinates, visibility, and stacking during startup.
            items.extend([None] * len(geometry))
            for index in set(range(len(geometry))) - next_visible:
                items[index] = canvas.create_polygon(
                    0, 0, 0, 0, 0, 0, fill=colors[geometry[index][:2]],
                    outline="", state="hidden")
            for index, points in projected:
                items[index] = canvas.create_polygon(
                    *points, fill=colors[geometry[index][:2]], outline="", state="normal")
        else:
            if colors is not None:
                for item, (face, position, _) in zip(items, geometry):
                    canvas.itemconfigure(item, fill=colors[face, position])
            for index in visible - next_visible:
                canvas.itemconfigure(items[index], state="hidden")
            for index in next_visible - visible:
                canvas.itemconfigure(items[index], state="normal")
            for index, points in projected:
                canvas.coords(items[index], *points)
            if order != draw_order:
                for index in order:
                    canvas.tag_raise(items[index])
        piece_state = state
        visible, draw_order = next_visible, order

    def request_draw():
        nonlocal pending_draw
        if pending_draw is None:
            pending_draw = root.after_idle(draw)

    def resize(event):
        nonlocal size
        new_size = (event.width, event.height)
        if new_size != size:
            size = new_size
            if not items and pending_draw is None:
                # Populate the first valid canvas before Tk paints its background.
                draw()
            else:
                request_draw()

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
        request_draw()

    def release(event):
        nonlocal previous
        previous = None

    def close():
        if pending_draw is not None:
            root.after_cancel(pending_draw)
        root.destroy()

    root.protocol("WM_DELETE_WINDOW", close)
    canvas.bind("<Configure>", resize)
    canvas.bind("<ButtonPress-1>", press)
    canvas.bind("<B1-Motion>", drag)
    canvas.bind("<ButtonRelease-1>", release)
    root.mainloop()


if __name__ == "__main__":
    cube = Cube()
    cube.f()
    show_cube(cube)
