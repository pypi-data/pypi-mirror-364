"""
Errors for CIFT
"""

class CIFError(Exception):
    """
    Generic CIF parsing error
    """

class NoLayerError(CIFError):
    """
    Tried adding geometry before any layer was specified
    """

class RoutError(CIFError):
    """
    Generic routine-related error
    """

class RoutStartError(RoutError):
    """
    Routine was started while one is already being defined
    """

class RoutFinishError(RoutError):
    """
    Encountered subnroutine definiton end before start
    """

