"""parser.py: contains Parser class and relevant utils"""

class Symbol:
    """A symbol in a context-free grammar"""
    def __init__(self, name = None):
        self.name = name

    def __repr__(self):
        return f"<Symbol {self.name}>"

terminal = Symbol('terminal')

class _SingleWrapper():
    """Helper class: takes in a single object and stores it"""
    def __init__(self, what):
        super().__init__()
        self.what = what

class _TupleWrapper():
    """Helper class: takes in a tuple and stores it"""
    def __init__(self, *what):
        super().__init__()
        self.what = what

class Seq(_TupleWrapper):
    """Context-free grammar definition helper: a sequence of symbols"""
    name = '<Seq>'

class Or(_TupleWrapper):
    """Context-free grammar definition helpers: one of multiple symbols"""
    name = '<Or>'

class Maybe(_SingleWrapper):
    """Grammar helper: Zero or one of this symbol"""
    name = '<Maybe>'

class Many(_SingleWrapper):
    """Grammar helper: Zero, one, or more of this symbol"""
    name = '<Many>'

class CSTNode:
    """Node in a syntax tree."""
    def __init__(self, symbol):
        self.symbol = symbol
        self.children = []
        self.string = None

        if True in self.children:
            assert False
        if False in self.children:
            assert False

    def __repr__(self):
        return f"<CSTNode {self.symbol}>"

    def __bool__(self):
        return True

    def descend(
            self,
            callback,
            depth = 0,
            number = None
            ):

        if number is None:
            number = [0]
            
        callback(self, depth, number[0])
        number[0] += 1
        for child in self.children:
            child.descend(
                callback,
                depth + 1,
                number
                )

    def compute_string(self):
        if self.string is None:
            self.string = ''.join(
                child.compute_string() for child in self.children
                )
        return self.string

class Parser:
    """Parses string according to a context-free grammar definition"""
    def __init__(self, grammar, string):
        self.grammar = grammar
        self.string = string

        self.index = 0
        self.tree = None

        self.fullcst = False

    def parse(self, symbol = None):

        if symbol is None:
            symbol = tuple(self.grammar.keys())[0]

        if symbol in self.grammar.keys():
            sdef = symbol
            symbol = self.grammar[sdef]
        else:
            sdef = symbol

        self.tree = self._parse(symbol)
        self.tree.symbol = sdef

        if self.tree is False:
            raise Exception("didnt parse")
        
        return self.tree

    def _parse(self, symbol):
        
        node = CSTNode(symbol)

        self.check_over_consumed()

        if isinstance(symbol, Symbol):
            mark = self.index

            child = self._parse(self.grammar[symbol])

            if child:
                if self.fullcst:
                    node.children.extend(child.children)
                else:
                    node.children.append(child)
                    child.symbol = symbol
                return node

            self.index = mark
            return False


        elif isinstance(symbol, Seq):
            mark = self.index

            children = []
            for elem in symbol.what:
                children.append(self._parse(elem))

            if all(children):
                if self.fullcst:
                    node.children.extend(children)
                else:
                    for child in children:
                        node.children.extend(child.children)

                return node

            self.index = mark
            return False


        elif isinstance(symbol, Or):

            mark = self.index

            for elem in symbol.what:

                child = self._parse(elem)

                if child:
                    if self.fullcst:
                        node.children.append(child)
                    else:
                        node.children.extend(child.children)

                    return node

                else:
                    self.index = mark

            return False

        elif isinstance(symbol, Maybe):

            if self.is_consumed():
                return node

            mark = self.index

            child = self._parse(symbol.what)

            if child:
                if self.fullcst:
                    node.children.append(child)
                else:
                    node.children.extend(child.children)
            else:
                self.index = mark

            return node

        elif isinstance(symbol, Many):

            if self.is_consumed():
                return node

            while True:
                mark = self.index

                child = self._parse(symbol.what)

                if child:
                    if self.fullcst:
                        node.children.append(child)
                    else:
                        node.children.extend(child.children)
                else:
                    self.index = mark
                    break

                if self.is_consumed():
                    return node

            return node

        elif isinstance(symbol, str):
            result = self.try_consume(symbol)
            if result:
                child = CSTNode(terminal)
                child.string = symbol
                node.children.append(child)
                #node.children.extend(child.children)
                return node

            return False

        assert False, type(symbol)

    def try_consume(self, symbol):
        if self.index > len(self.string):
            assert False

        if self.index == len(self.string):
            return len(symbol) == 0

        if not symbol:
            return True

        if self.string[self.index:].startswith(symbol):
            self.index += len(symbol)

            return True

        return False

    def is_consumed(self):
        return self.index == len(self.string)

    def check_over_consumed(self):
        if self.index > len(self.string):
            assert False

