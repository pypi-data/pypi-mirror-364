"""shorthand.py: shorthand functions for cift"""

import cift as cf

def parse(what: str, grammar = cf.grammar.strict):
        if isinstance(what, str):
            return parse_string(what, grammar)

        raise NotImplementedError(
            "Eventually this will support paths and file objects, "
            "but for now please pass a string."
            )

def parse_string(cifstring: str, grammar = cf.grammar.strict):
    parser = cf.Parser(grammar, cifstring)
    cst = parser.parse()
    cst.compute_string()
    monad = cf.semir.CSTMonad(cst)
    semir = cf.semir.SemIR(monad)
    semir.eval()
    layers = semir.build()
    return layers

