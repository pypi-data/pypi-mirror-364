try:
    from typing import Self
except ImportError:
    # py3.10 and lower
    from typing_extensions import Self

from dataclasses import dataclass
from collections import defaultdict
import re

import cift as cf

def to_int(string: str) -> int:
    return int(string.lstrip('0') or '0')

class Transform:
    next: Self | None

    def __init__(self) -> None:
        self.next = None

    def append(self, new: Self) -> None:
        if self.next is None:
            self.next = new
        else:
            self.next.append(new)

    def transform_point(self, x: int, y: int) -> cf.types.point:
        if self.next is not None:
            x, y = self.next.transform_point(x, y)

        return x, y

    def transform_points(self, points: cf.types.poly) -> cf.types.poly:
        return tuple(self.transform_point(*point) for point in points)

class Rotate(Transform):
    def __init__(self, rx: int, ry: int) -> None:
        super().__init__()

        magnitude = (rx ** 2 + ry ** 2) ** (1 / 2)
        self.ux = rx / magnitude
        self.uy = ry / magnitude

    def transform_point(self, x: int, y: int) -> cf.types.point:
        x, y = map(int, (
            x * self.ux - y * self.uy,
            x * self.uy + y * self.ux
            ))
        # TODO this is not correct, as far as I understand,
        # the result of a rotation in CIF does not need to be
        # quantized to the grid. So this should be float.

        if self.next is not None:
            x, y = self.next.transform_point(x, y)

        return x, y

class Translate(Transform):
    def __init__(self, x: int, y: int) -> None:
        super().__init__()

        self.x = x
        self.y = y

    def transform_point(self, x: int, y: int) -> cf.types.point:
        x += self.x
        y += self.y

        if self.next is not None:
            x, y = self.next.transform_point(x, y)

        return x, y

@dataclass
class Frame:
    layer: str | None
    line: int
    rout_num: int
    transform: Transform

class Parser:
    """
    CIF Parser.
    """

    layers: cf.types.layers
    routs_lines: dict[int, list[str]]
    _stack: list[Frame]
    edges: cf.types.edges
    routs_start_lines: dict[int, int]
    _this_rout: int

    # Confusion warning:
    # `_this_rout` is used when iterating over the toplevel
    # and a routine definition is encountered.
    # It's used to keep track of "what routine are we defining now?"
    # and to raise the appropriate error if, for example,
    # a routine definition is started before the previous one
    # is closed.
    #
    # self._stack[-1].rout_num, on the other hand,
    # is used to keep track of "what routine are we *executing* now?"

    def __init__(self) -> None:
        self.layers = defaultdict(list)

        self._stack = [Frame(
            layer=None,
            line=0,
            rout_num=-1,
            transform=Transform()
            )]

        self._this_rout = -1
        self.routs_lines = {}
        self.routs_start_lines = {}
        self.edges = []

    @property
    def _frame(self) -> Frame:
        return self._stack[-1]

    def parse(self, what: str) -> None:
        if isinstance(what, str):
            return self.parse_string(what)

        raise NotImplementedError(
            "Eventually this will support paths and file objects, "
            "but for now please pass a string."
            )

    def parse_string(self, cif: str) -> None:
        for line in cif.splitlines(keepends=False):
            self._parse_line(line)
            self._frame.line += 1

    def _parse_line(self, line: str) -> None:

        if (match := cf.re.rout_finish.match(line)):
            self._handle_rout_finish(match)

        elif (match := cf.re.rout_start.match(line)):
            self._handle_rout_start(match)

        elif self._this_rout != -1:
            assert self._this_rout in self.routs_lines.keys()
            self.routs_lines[self._this_rout].append(line)

        elif (match := cf.re.rout_call.match(line)):
            self._handle_rout_call(match)

        elif (match := cf.re.layer.match(line)):
            self._frame.layer = match.groups()[0]

        elif (match := cf.re.box.match(line)):
            self._handle_box(match)

        elif (match := cf.re.polygon.match(line)):
            self._handle_polygon(match)

        elif (match := cf.re.comment.match(line)):
            pass

        elif line.startswith('E'):
            # TODO
            pass

        else:
            raise Exception(line)

    def _traceback(self) -> str:
        return '\ncalled by\n'.join((
            f"subroutine {frame.rout_num or '<toplevel>'} "
            f"at line {frame.line} "
            for frame in reversed(self._stack)
            ))

    def _assert_layer(self) -> str:
        if self._frame.layer is None:
            raise cf.err.NoLayerError(''.join((
                "Error in ",
                self._traceback(),
                "Error: tried adding geometry before any layer was selected."
                )))

        return self._frame.layer

    def _handle_box(self, match: re.Match[str]) -> None:
        layer = self._assert_layer()

        width, height, xpos, ypos = map(to_int, match.groups()[:4])
        rot_x, rot_y = match.groups()[4:]

        x1 = -width // 2
        y1 = -height // 2
        x2 = width // 2
        y2 = height // 2

        points: cf.types.poly = (
            (x1, y1),
            (x2, y1),
            (x2, y2),
            (x1, y2),
            )

        if rot_x is not None:
            assert rot_y is not None
            rot_x = to_int(rot_x)
            rot_y = to_int(rot_y)
            points = Rotate(rot_x, rot_y).transform_points(points)

        points = tuple(
            (point[0] + xpos, point[1] + ypos)
            for point in points
            )

        points = self._frame.transform.transform_points(points)

        self.layers[layer].append(points)

    def _handle_polygon(self, match: re.Match['str']) -> None:
        layer = self._assert_layer()

        coords = tuple(map(to_int, cf.re.points.findall(match.groups()[0])))
        points = self._frame.transform.transform_points(
            tuple(zip(coords[0::2], coords[1::2]))
            )

        self.layers[layer].append(points)

    def _handle_rout_start(self, match: re.Match['str']) -> None:
        # TODO redefinition
        rout_num = to_int(match.groups()[0])

        assert len(self._stack) == 1

        if self._this_rout != -1:
            raise cf.err.RoutStartError(
                f"tried defining subroutine number {rout_num}. "
                f"before definition of routine number {self._this_rout} "
                "was terminated. "
                )

        self._this_rout = rout_num
        self.routs_lines[rout_num] = []
        self.routs_start_lines[rout_num] = self._frame.line

    def _handle_rout_finish(self, match: re.Match['str']) -> None:

        assert len(self._stack) == 1

        if self._this_rout == -1:
            raise cf.err.RoutFinishError(''.join((
                "Error in ",
                self._traceback(),
                "tried ending a subroutine definition before it was started. "
                )))

        self._this_rout = -1

    def _handle_rout_call(self, match: re.Match['str']) -> None:
        rout_num, rout_transform = match.groups()
        transform = Transform()
        if rout_transform:
            for kind, x, y in cf.re.rout_transform.findall(rout_transform):
                x = to_int(x)
                y = to_int(y)
                if kind == 'T':
                    transform.append(Translate(x, y))
                elif kind == 'R':
                    transform.append(Rotate(x, y))
                else:
                    assert False

        rout_num = to_int(rout_num)

        self.edges.append(
            cf.types.Edge(self._frame.rout_num, rout_num)
            )

        self._stack.append(Frame(
            line=self.routs_start_lines[rout_num],
            layer=None,
            rout_num=rout_num,
            transform=transform
            ))

        for line in self.routs_lines[rout_num]:
            self._frame.line += 1
            self._parse_line(line)

        self._stack.pop()


