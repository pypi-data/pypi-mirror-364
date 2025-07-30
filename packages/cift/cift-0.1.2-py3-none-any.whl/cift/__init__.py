"""
Init file for CIFT.
Used for namespace flattening.
"""

from cift import err
from cift import types
from cift.parser import Symbol
from cift.parser import Seq
from cift.parser import Or
from cift.parser import Maybe
from cift.parser import Many
from cift.parser import CSTNode
from cift.parser import Parser
import cift.grammar
import cift.astextra
import cift.semir
import cift.debug
from cift.shorthand import parse
from cift.shorthand import parse_string


