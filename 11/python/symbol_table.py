from dataclasses import dataclass
from typing import Optional


class Kind:
    STATIC = "static"
    FIELD = "field"
    ARG = "arg"
    VAR = "var"  # equivalent to local memory segment


@dataclass
class Symbol:
    type: str
    kind: str
    index: int


class SymbolTable:
    def __init__(self):
        self.class_symbols = {}
        self.subroutine_symbols = {}
        self.counts = {Kind.STATIC: 0, Kind.FIELD: 0, Kind.ARG: 0, Kind.VAR: 0}

    def define(self, name: str, type: str, kind: str):
        if kind in [Kind.FIELD, Kind.STATIC]:
            self.class_symbols[name] = Symbol(type, kind, self.counts[kind])
            # self.class_symbols[name] = [type, kind, self.counts[kind]]
            self.counts[kind] += 1
        if kind in [Kind.ARG, Kind.VAR]:
            self.subroutine_symbols[name] = Symbol(type, kind, self.counts[kind])
            # self.subroutine_symbols[name] = [type, kind, self.counts[kind]]
            self.counts[kind] += 1

    def start_subroutine(self) -> None:
        self.subroutine_symbols = {}
        self.counts[Kind.ARG] = 0
        self.counts[Kind.VAR] = 0

    def var_count(self, kind: str) -> int:
        return self.counts[kind]

    def kind_of(self, name: str) -> Optional[str]:
        symbol = self._lookup(name)
        if symbol:
            # return symbol[1]
            return symbol.kind

    # e.g. int, char, boolean, class...
    def type_of(self, name: str) -> Optional[str]:
        symbol = self._lookup(name)
        if symbol:
            # return symbol[0]
            return symbol.type

    def index_of(self, name: str) -> Optional[str]:
        symbol = self._lookup(name)
        if symbol:
            # return symbol[2]
            return symbol.index

    def contains(self, name: str) -> bool:
        if (name in self.subroutine_symbols) or (name in self.class_symbols):
            return True
        return False

    # first lookup in subroutine scope, then in class scope
    def _lookup(self, name: str) -> Optional[Symbol]:
        if self.subroutine_symbols.get(name):
            return self.subroutine_symbols.get(name)
        elif self.class_symbols.get(name):
            return self.class_symbols.get(name)
        else:
            return None


if __name__ == "__main__":
    symbol_table = SymbolTable()
    symbol_table.define("x", "int", Kind.FIELD)
    symbol_table.define("x", "int", Kind.VAR)
