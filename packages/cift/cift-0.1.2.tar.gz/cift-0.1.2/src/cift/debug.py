"""debug.py -- debugging helpers for cift"""
from os import system
from pathlib import Path
import cift as cf

def crutch(string, grammar):
    parser = cf.Parser(grammar, string)
    cst = parser.parse()
    cst.compute_string()
    Path('cst.gv').write_text(cf.astextra.get_dot(cst))
    system("sh -c 'dot -T png < cst.gv > cst.png'")
    system("handlr open cst.png")
    monad = cf.semir.CSTMonad(cst)
    semir = cf.semir.SemIR(monad)
    semir.eval()
    print('+----')
    semir.print()
    print('+----')

