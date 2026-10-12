# vibecoded

import math
import time
import tkinter as tk


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


def _pick_sticker(canvas, sticker_indices, x, y):
    """Find the topmost visible sticker actually underneath the pointer."""
    for item in reversed(canvas.find_overlapping(x, y, x, y)):
        if item in sticker_indices and canvas.itemcget(item, "state") != "hidden":
            return sticker_indices[item]
    return None


def _drag_move(face, position, dx, dy, yaw, pitch):
    """Interpret a screen drag as one outer-layer quarter-turn."""
    if math.hypot(dx, dy) < 12:
        return None
    normal, right, down = FACES[face]
    rx, ry, _ = rotate(right, yaw, pitch)
    tx, ty, _ = rotate(down, yaw, pitch)
    ry, ty = -ry, -ty  # Canvas y points down.
    determinant = rx * ty - tx * ry
    if abs(determinant) < 0.05:
        return None

    # Undo the face's screen projection before choosing a row or column.
    horizontal = (dx * ty - tx * dy) / determinant
    vertical = (rx * dy - dx * ry) / determinant
    if abs(horizontal) >= 1.2 * abs(vertical):
        axis, direction, distance = down, right, horizontal
    elif abs(vertical) >= 1.2 * abs(horizontal):
        axis, direction, distance = right, down, vertical
    else:
        return None
    layer = sum(p * a for p, a in zip(position, axis))
    if layer == 0:
        return None  # Middle slices and centers do not generate face moves.
    outward = tuple(layer * a for a in axis)
    move = next(name for name, axes in FACES.items() if axes[0] == outward)
    # A clockwise turn around outward moves this face along normal x outward.
    nx, ny, nz = normal
    ox, oy, oz = outward
    tangent = (ny * oz - nz * oy, nz * ox - nx * oz, nx * oy - ny * ox)
    clockwise = sum(t * d for t, d in zip(tangent, direction))
    return move if clockwise * distance > 0 else move + "'"


def _cross(a, b):
    return (a[1] * b[2] - a[2] * b[1],
            a[2] * b[0] - a[0] * b[2],
            a[0] * b[1] - a[1] * b[0])


def _face_displacement(face, dx, dy, yaw, pitch):
    right, down = FACES[face][1:]
    rx, ry, _ = rotate(right, yaw, pitch)
    tx, ty, _ = rotate(down, yaw, pitch)
    ry, ty = -ry, -ty
    determinant = rx * ty - tx * ry
    if abs(determinant) < 0.05:
        return None
    return ((dx * ty - tx * dy) / determinant,
            (rx * dy - dx * ry) / determinant)


def _turn_geometry(yaw, pitch, face, angle):
    """Rotate the selected layer's vertices and normals before projecting."""
    axis = FACES[face][0]
    cosine, sine = math.cos(angle), math.sin(angle)
    cy, sy = math.cos(yaw), math.sin(yaw)
    cp, sp = math.cos(pitch), math.sin(pitch)

    def turn(point):
        along = sum(a * p for a, p in zip(axis, point))
        tangent = _cross(axis, point)
        return tuple(cosine * p + sine * t + (1 - cosine) * along * a
                     for p, t, a in zip(point, tangent, axis))

    def camera(point):
        x, y, z = point
        x, z = cy * x + sy * z, -sy * x + cy * z
        return x, cp * y - sp * z, sp * y + cp * z

    polygons = []
    for index, (sticker_face, position, points) in enumerate(_sticker_geometry()):
        moving = sum(a * p for a, p in zip(axis, position)) == 1
        normal = FACES[sticker_face][0]
        if camera(turn(normal) if moving else normal)[2] <= 1e-9:
            continue
        vertices = [camera(turn(point) if moving else point) for point in points]
        depth = sum(vertex[2] for vertex in vertices) / 4
        polygons.append((depth, index, vertices))
    return sorted(polygons, key=lambda polygon: polygon[0])


class Display:
    """Display a Cube; left-drag turns a layer and right-drag orbits the view."""

    SNAP_SECONDS = 0.180
    FRAME_MS = 16

    def __init__(self, cube):
        self.cube = cube
        self.yaw, self.pitch = -0.55, 0.45
        self._geometry = _sticker_geometry()
        self._gesture = None
        self._move_start = None
        self._previous = None
        self._pending_draw = None
        self._animation_after = None
        self._snap = None
        self._turn_face = None
        self._turn_angle = 0.0
        self._turn_colors = None
        self._drag_component = None
        self._drag_factor = None
        self._items = []
        self._sticker_indices = {}
        self._piece_state = None
        self._colors = None
        self._painted_colors = None
        self._visible = set()
        self._draw_order = ()
        self._size = (0, 0)
        self._closed = False

        self.root = tk.Tk()
        self.root.title("Cube — left-drag to turn, right-drag to rotate")
        self.root.geometry("540x540")
        self.root.minsize(240, 240)
        self.canvas = tk.Canvas(self.root, background="#202124", highlightthickness=0)
        self.canvas.pack(fill=tk.BOTH, expand=True)
        self.root.protocol("WM_DELETE_WINDOW", self.close)
        for event, handler in (
            ("<Configure>", self._resize),
            ("<ButtonPress-1>", self._move_press),
            ("<B1-Motion>", self._move_drag),
            ("<ButtonRelease-1>", self._move_release),
            ("<ButtonPress-3>", self._view_press),
            ("<B3-Motion>", self._view_drag),
            ("<ButtonRelease-3>", self._view_release),
        ):
            self.canvas.bind(event, handler)

    def run(self):
        self.root.mainloop()

    def close(self):
        if self._closed:
            return
        self._closed = True
        for callback in (self._pending_draw, self._animation_after):
            if callback is not None:
                self.root.after_cancel(callback)
        self._pending_draw = self._animation_after = None
        self._snap = None
        self.root.destroy()

    def _draw(self):
        self._pending_draw = None
        width, height = self._size
        if self._closed or width <= 1 or height <= 1:
            return
        scale = min(width, height) * 0.26
        if self._turn_face is None:
            state = (tuple(self.cube.corners), tuple(self.cube.edges))
            if state != self._piece_state:
                self._colors = sticker_colors(self.cube)
                self._piece_state = state
            colors = self._colors
            polygons = _visible_geometry(self.yaw, self.pitch)
        else:
            colors = self._turn_colors
            polygons = _turn_geometry(self.yaw, self.pitch, self._turn_face, self._turn_angle)
        order = tuple(index for _, index, _ in polygons)
        visible = set(order)
        projected = [(index, [c for x, y, _ in vertices
                              for c in (width / 2 + x * scale, height / 2 - y * scale)])
                     for _, index, vertices in polygons]
        if not self._items:
            self._items = [None] * len(self._geometry)
            for index in set(range(len(self._geometry))) - visible:
                self._items[index] = self.canvas.create_polygon(
                    0, 0, 0, 0, 0, 0, fill=colors[self._geometry[index][:2]],
                    outline="", state="hidden")
            for index, points in projected:
                self._items[index] = self.canvas.create_polygon(
                    *points, fill=colors[self._geometry[index][:2]], outline="", state="normal")
            self._sticker_indices.update((item, i) for i, item in enumerate(self._items))
        else:
            if colors is not self._painted_colors:
                for item, (face, position, _) in zip(self._items, self._geometry):
                    self.canvas.itemconfigure(item, fill=colors[face, position])
            for index in self._visible - visible:
                self.canvas.itemconfigure(self._items[index], state="hidden")
            for index in visible - self._visible:
                self.canvas.itemconfigure(self._items[index], state="normal")
            for index, points in projected:
                self.canvas.coords(self._items[index], *points)
            if order != self._draw_order:
                for index in order:
                    self.canvas.tag_raise(self._items[index])
        self._painted_colors = colors
        self._visible, self._draw_order = visible, order

    def _draw_now(self):
        if self._pending_draw is not None:
            self.root.after_cancel(self._pending_draw)
            self._pending_draw = None
        self._draw()

    def _request_draw(self):
        if not self._closed and self._pending_draw is None:
            self._pending_draw = self.root.after_idle(self._draw)

    def _resize(self, event):
        size = (event.width, event.height)
        if size == self._size:
            return
        self._size = size
        if self._gesture == "move":
            self._gesture = self._move_start = None
            self._clear_turn()
        if not self._items and self._pending_draw is None:
            self._draw()
        else:
            self._request_draw()

    def _move_press(self, event):
        if self._gesture is not None or self._snap is not None:
            return
        self._draw_now()
        index = _pick_sticker(self.canvas, self._sticker_indices, event.x, event.y)
        self._gesture = "move"
        self._move_start = (event.x, event.y, index)

    def _move_drag(self, event):
        if self._gesture != "move":
            return
        x, y, index = self._move_start
        if index is None:
            return
        face, position, _ = self._geometry[index]
        dx, dy = event.x - x, event.y - y
        if self._turn_face is None:
            move = _drag_move(face, position, dx, dy, self.yaw, self.pitch)
            if move is None:
                return
            displacement = _face_displacement(face, dx, dy, self.yaw, self.pitch)
            self._drag_component = 0 if abs(displacement[0]) >= 1.2 * abs(displacement[1]) else 1
            direction = FACES[face][1 + self._drag_component]
            tangent = _cross(FACES[face][0], FACES[move[0]][0])
            self._drag_factor = -sum(t * d for t, d in zip(tangent, direction))
            self._turn_face = move[0]
            self._turn_colors = sticker_colors(self.cube)
        displacement = _face_displacement(face, dx, dy, self.yaw, self.pitch)
        sticker_width = min(self._size) * 0.26 * 2 / 3
        angle = self._drag_factor * displacement[self._drag_component] / sticker_width * math.pi / 2
        self._turn_angle = max(-math.pi / 2, min(math.pi / 2, angle))
        self._request_draw()

    def _move_release(self, event):
        if self._gesture != "move":
            return
        self._move_drag(event)
        self._gesture = self._move_start = None
        if self._turn_face is None:
            return
        target = 0.0
        if abs(self._turn_angle) >= math.pi / 4 - 1e-12:
            target = math.copysign(math.pi / 2, self._turn_angle)
            move = self._turn_face + ("'" if target > 0 else "")
            try:
                self.cube.move(move)
            except Exception:
                self._clear_turn()
                self._request_draw()
                raise
            print(f'cube.move("{move}")', flush=True)
        remaining = abs(target - self._turn_angle)
        if remaining < 1e-12:
            self._clear_turn()
            self._request_draw()
            return
        duration = max(0.060, self.SNAP_SECONDS * remaining / (math.pi / 2))
        self._snap = (time.perf_counter(), self._turn_angle, target, duration)
        self._animate()

    def _animate(self):
        self._animation_after = None
        if self._closed or self._snap is None:
            return
        started, initial, target, duration = self._snap
        progress = min(1.0, (time.perf_counter() - started) / duration)
        if progress >= 1:
            self._clear_turn()
        else:
            eased = progress * progress * (3 - 2 * progress)
            self._turn_angle = initial + (target - initial) * eased
        self._draw_now()
        if self._snap is not None:
            self._animation_after = self.root.after(self.FRAME_MS, self._animate)

    def _clear_turn(self):
        self._snap = None
        self._turn_face = None
        self._turn_angle = 0.0
        self._turn_colors = None
        self._drag_component = self._drag_factor = None

    def _view_press(self, event):
        if self._gesture is not None or self._snap is not None:
            return
        self._gesture = "view"
        self._previous = (event.x, event.y)

    def _view_drag(self, event):
        if self._gesture != "view":
            return
        self.yaw += (event.x - self._previous[0]) * 0.01
        self.pitch += (event.y - self._previous[1]) * 0.01
        self._previous = (event.x, event.y)
        self._request_draw()

    def _view_release(self, event):
        if self._gesture == "view":
            self._gesture = self._previous = None





