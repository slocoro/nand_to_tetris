from dataclasses import dataclass


@dataclass
class Kind:
    STATIC = "static"
    FIELD = "field"
    ARG = "arg"
    VAR = "var"  # equivalent to local memory segment


class SymbolTable:
    def __init__(self):
        pass

    def define(self, name: str, type: str, kind: Kind):
        pass

    def var_count(self, kind: Kind) -> int:
        pass

    def kind_of(self, name: str) -> Kind:
        pass

    # e.g. int, char, boolean, class...
    def type_of(self, name: str) -> str:
        pass

    def index_of(self, name: str) -> int:
        pass
