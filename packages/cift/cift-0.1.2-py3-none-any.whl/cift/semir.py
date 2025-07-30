"""
semir.py: Semantic Intermediate Representation of CIF files.

This file is not yet complete. Only some CIF commands are handled.

"""

from dataclasses import dataclass
from enum import StrEnum

from cift import grammar as gr
from cift.parser import Symbol
from cift.parser import terminal
from cift.parser import CSTNode

def merge_layers(dest, source, transform):
    for k, v in source.items():
        if k not in dest.keys():
            dest[k] = []
        v_t = apply_transform(v, transform)
        dest[k].extend(v_t)

def apply_transform(polys, transform):
    new_polys = []
    for poly in polys:
        for t in transform:
            if t[0] == 'T':
                poly = tuple(
                    (x + t[1][0], y + t[1][1])
                    for x, y in poly
                    )

            elif t[0] == 'R':

                rx, ry = t[1]
                cx, cy = 0, 0

                # FIXME this is copypasta
                if rx == ry == 0:
                    print("box rotation == 0 0! Assuming you meant 1 0.")
                    # TODO actual warnings
                    rx, ty = 1, 0

                urx = rx / (rx ** 2 + ry ** 2)**(1 / 2)
                ury = ry / (rx ** 2 + ry ** 2)**(1 / 2)

                def tform(x, y):
                    return (
                        cx + urx * x - ury * y,
                        cy + ury * x + urx * y,
                        )

                poly = tuple(tform(x, y) for x, y in poly)

            elif t[0] == 'M':
                if t[1] == 'X':
                    poly = tuple((x, -y) for x, y in poly)
                elif t[1] == 'Y':
                    poly = tuple((-x, y) for x, y in poly)
                else:
                    assert False

            else:
                assert False

        new_polys.append(poly)
    return new_polys

class CSTMonad:
    def __init__(self, *nodes):
        self.nodes = nodes

    def __repr__(self):
        return '\n\t'.join((
            '<CSTMonad ',
            *map(repr, self.nodes),
            '>'
            ))

    def __bool__(self):
        return len(self.nodes) > 0

    def and_(self, other):
        if not bool(self):
            return self
        return other

    def or_(self, other):
        if bool(self):
            return self
        return other
    
    def apply(self, func):
        return func(self)

    def map(self, func):
        return tuple(map(func, self.nodes))

    def mapn(self, num, func, fallback=None):
        if len(self.nodes) != num:
            return fallback
        return tuple(map(func, self.nodes))

    def mapn_wrap(self, num, func, fallback=None):
        if len(self.nodes) != num:
            return fallback
        return tuple(func(type(self)(node)) for node in self.nodes)

    def mapsingle(self, func, fallback=None):
        if len(self.nodes) != 1:
            return fallback
        return func(self.nodes[0])

    def unroll(self):
        return type(self)(*(
            child
            for node in self.nodes
            for child in node.children
            ))

    def oftype(self, symbol):
        return type(self)(*(
            node
            for node in self.nodes
            if node.symbol is symbol
            ))

    def notoftype(self, symbol):
        return type(self)(*(
            node
            for node in self.nodes
            if node.symbol is not symbol
            ))

    def assert_len(self, n):
        if len(self.nodes) == n:
            return self
        else:
            return type(self)()

    def slice(self, a=None, b=None, c=None):
        return type(self)(*self.nodes[slice(a,b,c)])

    def sole_child(self, symbol):
        return self.unroll().assert_len(1).oftype(symbol)

    def single_child(self, symbol):
        return self.unroll().oftype(symbol).assert_len(1)

    def first_child_of_type(self, symbol):
        # TODO this slice thing is confusing, None is not None?
        return self.unroll().oftype(symbol).slice(0, 1)

    def singledispatch(self, *methods):
        return type(self)(*(
            method(type(self)(node))
            for node in self.nodes
            )).unroll().assert_length(1)

    def hmatch(self, patterns):
        i = 0
        results = []
        while i < len(self.nodes):
            for pattern, funct in patterns:
                if _hmatch_single(pattern, self.nodes, i):
                    # FIXME spaghett
                    results.append(funct(*(self.nodes[i:i + len(pattern)])))
                    i += len(pattern)
                    break
            else:
                assert False, self.nodes
                #return []
        return results

def _hmatch_single(pattern, nodes, i):
    return all(
        (
            _hmatch_single_single(key, node)
            for key, node in zip(
                pattern,
                nodes[i:i + len(pattern)],
                strict=True
                )
            )
        )

def _hmatch_single_single(key, node):
    if isinstance(key, str):
        return node.string == key

    if isinstance(key, Symbol):
        return node.symbol is key

    assert False

class SemType(StrEnum):
    FILE = 'FILE'
    DEF = 'DEF'
    CALL = 'CALL'
    LAYER = 'LAYER'
    POLY = 'POLY'

def parse_translate(_, point):
    return ('T', parse_point(CSTMonad(point)))

def parse_rotate(_, point):
    return ('R', parse_point(CSTMonad(point)))

def parse_mirror(_, node):
    if node.string == 'X':
        return ('M', 'X')

    if node.string == 'Y':
        return ('M', 'Y')

    assert False

def parse_point(monad):
    return (
        monad
        .unroll()
        .oftype(gr.sinteger)
        .mapn_wrap(2, lambda sint:  # TODO copypasta
            [1, -1][bool(sint.single_child(terminal))]  # minus sign
            *
            sint.single_child(gr.integer_d).mapsingle(
                lambda node: int(node.string)
                )
            )
        )

@dataclass
class SemIR:

    def __init__(self, monad):
        self.toplevel_children = []
        self.symb_children = []
        self.semtype = None
        self.monad = monad

        self.toplevel_commands = (
            monad
            .oftype(gr.cif_file)
            .unroll()
            .oftype(gr.command)
            .nodes
            )

        self.target_layer = (
            monad
            .sole_child(gr.prim_command)
            .sole_child(gr.layer_command)
            .single_child(gr.shortname)
            .mapsingle(lambda node: node.string)
            )

        self.called_symb = (
            monad
            .sole_child(gr.prim_command)
            .sole_child(gr.call_command)
            .single_child(gr.integer)
            .single_child(gr.integer_d)
            .mapsingle(lambda node: int(node.string))
            )

        if self.called_symb is not None:
            self.transform = (
                monad
                .sole_child(gr.prim_command)
                .sole_child(gr.call_command)
                .single_child(gr.transformation)
                .unroll()
                .notoftype(gr.blank)
                .hmatch((
                    (('T', gr.point), parse_translate),
                    (('M', terminal), parse_mirror),
                    (('R', gr.point), parse_rotate)
                    ))
                )
        else:
            self.transform = []

        self.defined_symb = (  # TODO scale currently ignored
            monad
            .single_child(gr.def_start_command)
            .first_child_of_type(gr.integer)
            .single_child(gr.integer_d)
            .mapsingle(lambda node: int(node.string))
            )

        self.symb_commands = (
            monad
            .single_child(gr.def_start_command)
            .and_(
                monad
                .unroll()
                .oftype(gr.prim_command)
                )
            .nodes
            )

        # polygon
        self.points = (
            monad
            .sole_child(gr.prim_command)
            .sole_child(gr.polygon_command)
            .single_child(gr.path)
            .unroll()
            .oftype(gr.point)
            .map(lambda point: (
                CSTMonad(point)
                .unroll()
                .oftype(gr.sinteger)
                .mapn_wrap(2, lambda sint:
                    [1, -1][bool(sint.single_child(terminal))]  # minus sign
                    *
                    sint.single_child(gr.integer_d).mapsingle(
                        lambda node: int(node.string)
                        )
                    )
                ))
            )

        box_monad = (
            monad
            .sole_child(gr.prim_command)
            .sole_child(gr.box_command)
            )

        if box_monad:
            # TODO still some potential errors here if some
            # constructs cst by hand,
            # we need to go FULLY MONADIC!!!!
            width, height = (
                box_monad
                .unroll()
                .oftype(gr.integer)
                .unroll()
                .oftype(gr.integer_d)
                .mapn(2, lambda node: int(node.string))
                )
            cx, cy = (
                box_monad
                .unroll()
                .oftype(gr.point)
                .slice(0, 1) # index 1 is rotation
                .apply(parse_point)
                )

            rx, ry = (  # TODO copypasta
                box_monad
                .unroll()
                .oftype(gr.point)
                .slice(1, 2) # index 1 is rotation
                .apply(parse_point)
                ) or (1, 0)

            if rx == ry == 0:
                print("box rotation == 0 0! Assuming you meant 1 0.")
                # TODO actual warnings
                rx, ty = 1, 0

            urx = rx / (rx ** 2 + ry ** 2)**(1 / 2)
            ury = ry / (rx ** 2 + ry ** 2)**(1 / 2)

            def tform(x, y):
                return (
                    # TODO TODO are int()'s needed here!?!?!
                    int(cx + urx * x - ury * y),
                    int(cy + ury * x + urx * y),
                    )

            # TODO rotation
            self.points = (
                tform(-width / 2, -height / 2),  # TODO rounding??
                tform(+width / 2, -height / 2),
                tform(+width / 2, +height / 2),
                tform(-width / 2, +height / 2),
                )

    
    def __repr__(self):
        return ''.join((
            '<SemIR',
            f' {self.target_layer=}' if self.target_layer is not None else '',
            f' {self.called_symb=}' if self.called_symb is not None else '',
            f' {self.transform=}' if self.transform else '',
            f' {self.defined_symb=}' if self.defined_symb is not None else '',
            f' {self.points=}' if self.points else '',
            '>'
            ))


    def eval(self, depth=0):
        for node in self.toplevel_commands:
            monad = CSTMonad(node)
            child = type(self)(monad)
            child.eval(depth=depth+1)

            self.toplevel_children.append(child)

        for node in self.symb_commands:
            # init expects command -> prim_command
            # but we have just prim_command
            # so wrap it
            node_wrapped = CSTNode(gr.command)
            node_wrapped.children.append(node)

            monad = CSTMonad(node_wrapped)
            child = type(self)(monad)
            child.eval(depth=depth+1)

            self.symb_children.append(child)

    def classify(self):
        if self.toplevel_commands:
            assert self.semtype is None
            self.semtype = SemType.FILE

        if self.target_layer is not None:
            assert self.semtype is None
            self.semtype = SemType.LAYER

        if self.called_symb is not None:
            assert self.semtype is None
            self.semtype = SemType.CALL

        if self.defined_symb is not None:
            assert self.semtype is None
            self.semtype = SemType.DEF

        if self.points:
            assert self.semtype is None
            self.semtype = SemType.POLY

        assert self.semtype is not None

    def build(self, symb_geom = None, symb_def = None):
        if symb_geom is None:
            symb_geom = {}
        if symb_def is None:
            symb_def = {}
        layers = {}

        layer = None
        for child in (*self.symb_children, *self.toplevel_children):
            if child.target_layer is not None:
                layer = child.target_layer
                if layer not in layers.keys():
                    layers[layer] = []

            if child.points:
                assert layer is not None
                layers[layer].append(child.points)

            if child.defined_symb is not None:
                symb_def[child.defined_symb] = child
                #symb_geom[child.defined_symb] = child.build(symb_geom, symb_def)

            if child.called_symb is not None:
                # TODO recursion detection

                if (geom := symb_geom.get(child.called_symb, None)) is not None:
                    merge_layers(layers, geom, child.transform)

                elif (sdef := symb_def.get(child.called_symb, None)) is not None:
                    geom = sdef.build(symb_geom, symb_def)
                    symb_geom[child.called_symb] = geom
                    merge_layers(layers, geom, child.transform)

                else:
                    # TODO custom error types? Or monadic handling?
                    raise KeyError(
                        f"Symbol {child.called_symb} has not been defined. "
                        f"Defined symbols: {symbs.keys()} . "
                        )

        return layers

    def print(self):
        print('SemIR')
        for child in (*self.symb_children, *self.toplevel_children):
            print(child)



