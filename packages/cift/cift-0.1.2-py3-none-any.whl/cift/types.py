"""
Type aliases for CIFT
"""

from typing import TypeAlias, NamedTuple, Sequence

class Edge(NamedTuple):
    caller: int
    callee: int


point: TypeAlias = tuple[int, int]
poly: TypeAlias = Sequence[point]
polys: TypeAlias = list[poly]
layers: TypeAlias = dict[str, polys]
edges: TypeAlias = list[Edge]

