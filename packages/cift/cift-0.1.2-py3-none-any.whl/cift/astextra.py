"""astextra: extra utilities for processing `ASTNode`s."""

from weakref import WeakKeyDictionary

from cift.parser import CSTNode, Symbol
from cift import grammar as gr

def escape_dot_label(s: str) -> str:
    """
    chatgpt code, no clue whether this is exhaustive or not
    """
    return (
        s
        .replace('\\', r'\\')
        .replace('"', r'\"')
        .replace('\n', r'\l')
        .replace('\r', '')
        + r'\l'
        )

def reduce(node):
    """
    Remove some nodes from AST to make it more readable.
    """
    new_children = []
    for child in node.children:
        reduce(child)

        if child.symbol == gr.semi:
            continue

        elif child.symbol == gr.blank:
            continue

        elif child.symbol == gr.sep:
            continue

        elif child.symbol == gr.prim_command:
            child = child.children[0]

        elif child.symbol == gr.digit:
            child = child.children[0]

        elif child.symbol == gr.c:
            child = child.children[0]

        elif child.symbol == gr.upper_char:
            child = child.children[0]

        new_children.append(child)

    node.children = new_children


#def print(self, depth = 0):
#    self.descend(
#        lambda obj, depth, number:
#        print(f"{number}:{' ' * depth}{repr(obj)}"),
#        )

def yield_dot(ast, depth = 0):
    yield 'digraph D {'
    yield 'node [shape=box]'

    ordering = WeakKeyDictionary()
    ast.descend(
        lambda obj, depth, number, ordering = ordering:
        ordering.update({obj: number}),
        )

    for node, number in ordering.items():
        #yield f'N{number} [label="{node.symbol.name}"]'
        yield fr'N{number} [label="{getattr(node.symbol, "name", "")}\l{escape_dot_label(repr(node.string))}"]'

    edges = []
    ast.descend(
        lambda obj, depth, number, ordering = ordering:
        edges.extend(
            f"N{number} -> N{ordering[child]}"
            for child in obj.children if isinstance(child, type(ast))
            ),
        )
    yield from edges
    yield '}'

def print_dot(ast):
    print('\n'.join(yield_dot(ast)))

def get_dot(ast):
    return ('\n'.join(yield_dot(ast)))

#
#@dataclass
#class ASTNode:
#    pass
#
#@dataclass
#class LayerCommand(ASTNode):
#    name: str
#
#@dataclass
#class PolygonCommand(ASTNode):
#    points: cf.types.polys
#
#@dataclass
#class SymbolDef(ASTNode):
#    polys: polys

