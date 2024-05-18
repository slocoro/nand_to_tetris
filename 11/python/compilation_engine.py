from io import StringIO
from jack_tokenizer import JackTokenizer
from symbol_table import SymbolTable, Kind
from vm_writer import VMWriter
from pathlib import Path

OP_LIST = [
    "+",
    "-",
    "/",
    "*",
    "&",
    "|",
    "<",
    ">",
    "=",
]

UNARY_OP_LIST = ["-", "~"]

SEGMENT_MAP = {
    "static": "static",
    "field": "this",
    "argument": "argument",
    "var": "local",
}


class CompilationError(Exception):
    pass


class CompilationEngine:
    def __init__(
        self,
        input_path: Path,
        tokenizer: JackTokenizer,
        symbol_table: SymbolTable,
        vm_writer: VMWriter,
    ):
        self._input_path = input_path
        self._tokenizer = tokenizer
        self._symbol_table = symbol_table
        self._vm_writer = vm_writer
        self._output_buffer = StringIO()
        self._output_path = self._create_output_path()
        self._class_name = ""
        self._subroutine_name = ""

    def write_output(self):
        with self._output_path.open("w") as f:
            print(self._output_buffer.getvalue(), file=f)

    def _create_output_path(self):
        return self._input_path.parent / f"{self._input_path.name.split('.')[0]}.vm"

    def validate_and_advance(self, tokens: str | list[str]):
        """
        Advance and validate a token.
        """
        current_token = self._tokenizer.current_token
        tokens = [tokens] if isinstance(tokens, str) else tokens
        if not current_token in tokens:
            raise Exception(f"Expected one of {tokens} but got '{current_token}'.")
        self._tokenizer.advance()

    def compile_class(self):
        # advance to first class var declaration
        # skips class and Name and {
        self._tokenizer.advance()
        self.validate_and_advance("class")
        self._class_name = self._tokenizer.current_token
        self._tokenizer.advance()
        self.validate_and_advance("{")
        # breakpoint()

        # while self._tokenizer.has_more_tokens():

        self.compile_class_var_dec()
        # breakpoint()

        self.compile_subroutine_dec()

        self.write_output()

    def compile_class_var_dec(self):
        """
        Compiles static declaration or field declaration.
        ('static' | 'field' ) type varName (',' varName)* ';'
        """
        # check the class var declaration starts with the correct token
        # if not just exit the method as there are no class vars
        if self._tokenizer.current_token not in ["static", "field"]:
            return

        # breakpoint()
        while self._tokenizer.current_token in ["static", "field"]:
            # kind, type, name
            # advance until after ;
            kind = self._tokenizer.current_token
            self._tokenizer.advance()
            type_ = self._tokenizer.current_token
            self._tokenizer.advance()
            name = self._tokenizer.current_token
            self._tokenizer.advance()
            self._symbol_table.define(name, type_, kind)

            while self._tokenizer.current_token == ",":
                # breakpoint()
                self._tokenizer.advance()
                name = self._tokenizer.current_token
                self._symbol_table.define(name, type_, kind)
                self._tokenizer.advance()

            self.validate_and_advance(";")

    def compile_subroutine_dec(self):
        """
        example: function/method void dispose() { ... }
        """
        # breakpoint()
        # check if there are any methods to compile
        if self._tokenizer.current_token not in ["constructor", "function", "method"]:
            return

        while self._tokenizer.current_token in ["constructor", "function", "method"]:

            self._symbol_table.start_subroutine()

            if self._tokenizer.current_token == "method":
                self._symbol_table.define("this", self._class_name, Kind.ARG)

            # advance to return type
            self.validate_and_advance(["function", "constructor", "method"])
            self._tokenizer.advance()
            self._subroutine_name = self._tokenizer.current_token
            self._tokenizer.advance()

            self.validate_and_advance("(")
            self.compile_parameter_list()
            self.validate_and_advance(")")

            # START COMPILING SUBROUTINE
            self.validate_and_advance("{")
            # breakpoint()

            # compile number of local vars
            while self._tokenizer.current_token == "var":
                self.compile_var_dec()
            num_vars = self._symbol_table.var_count("var")
            code = self._vm_writer.write_function(
                self._class_name, self._subroutine_name, num_vars
            )
            self._output_buffer.write(code)

            # compile statements
            if self._tokenizer.current_token in ["let", "if", "while", "do", "return"]:
                # breakpoint()
                self.compile_statements()

            self.validate_and_advance("}")
            # END COMPILING SUBROUTINE

    def compile_parameter_list(self):
        """
        Compiles parameter list, may be empty.
        ((type varName) (',' type varName)*)?
        """
        # no parameters to compile
        if self._tokenizer.current_token == ")":
            return

        type_ = self._tokenizer.current_token
        self._tokenizer.advance()
        name = self._tokenizer.current_token
        self._symbol_table.define(name, type_, Kind.ARG)
        self._tokenizer.advance()

        while self._tokenizer.current_token == ",":
            self._tokenizer.advance()
            type_ = self._tokenizer.current_token
            self._tokenizer.advance()
            name = self._tokenizer.current_token
            self._symbol_table.define(name, type_, Kind.ARG)
            self._tokenizer.advance()

    # this method was decomposed as it needs to write code after compile_var_dec()
    # def compile_subroutine_body(self):
    #     # breakpoint()
    #     # no parameters to compile
    #     if self._tokenizer.current_token == "}":
    #         return

    #     while self._tokenizer.current_token == "var":
    #         self.compile_var_dec()

    #     if self._tokenizer.current_token in ["let", "if", "while", "do", "return"]:
    #         # breakpoint()
    #         self.compile_statements()

    def compile_var_dec(self):
        """
        Compiles var declaration.
        'var' type varName (',' varName)* ';'
        """
        # breakpoint()

        self.validate_and_advance("var")
        # breakpoint()
        type_ = self._tokenizer.current_token
        self._tokenizer.advance()
        name = self._tokenizer.current_token
        self._symbol_table.define(name, type_, Kind.VAR)
        self._tokenizer.advance()

        while self._tokenizer.current_token == ",":
            self._tokenizer.advance()
            name = self._tokenizer.current_token
            self._symbol_table.define(name, type_, Kind.VAR)
            self._tokenizer.advance()

        self.validate_and_advance(";")
        # breakpoint()

    def compile_statements(self):
        # breakpoint()
        if self._tokenizer.current_token == "do":
            self.compile_do()
        if self._tokenizer.current_token == "return":
            # breakpoint()
            self.compile_return()

    def compile_let(self):
        self._output_buffer.write(self._indent * self._tab_width)
        self._output_buffer.write(f"<letStatement>\n")
        self._indent += 1

        # let
        self._output_buffer.write(self._indent * self._tab_width)
        self._output_buffer.write(
            f"<keyword> {self._tokenizer.current_token} </keyword>\n"
        )
        self._tokenizer.advance()

        # var name
        self._output_buffer.write(self._indent * self._tab_width)
        self._output_buffer.write(
            f"<identifier> {self._tokenizer.current_token} </identifier>\n"
        )
        self._tokenizer.advance()

        if self._tokenizer.current_token == "[":
            # [
            self._output_buffer.write(self._indent * self._tab_width)
            self._output_buffer.write(
                f"<symbol> {self._tokenizer.current_token} </symbol>\n"
            )
            self._tokenizer.advance()

            self.compile_expression()

            # ]
            self._output_buffer.write(self._indent * self._tab_width)
            self._output_buffer.write(
                f"<symbol> {self._tokenizer.current_token} </symbol>\n"
            )
            self._tokenizer.advance()

        # =
        self._output_buffer.write(self._indent * self._tab_width)
        self._output_buffer.write(
            f"<symbol> {self._tokenizer.current_token} </symbol>\n"
        )
        self._tokenizer.advance()

        # expression
        self.compile_expression()

        # ;
        self._output_buffer.write(self._indent * self._tab_width)
        self._output_buffer.write(
            f"<symbol> {self._tokenizer.current_token} </symbol>\n"
        )
        self._tokenizer.advance()

        self._indent -= 1
        self._output_buffer.write(self._indent * self._tab_width)
        self._output_buffer.write(f"</letStatement>\n")

    def compile_if(self):
        self._output_buffer.write(self._indent * self._tab_width)
        self._output_buffer.write(f"<ifStatement>\n")
        self._indent += 1

        # if
        self._output_buffer.write(self._indent * self._tab_width)
        self._output_buffer.write(
            f"<keyword> {self._tokenizer.current_token} </keyword>\n"
        )
        self._tokenizer.advance()

        # (
        self._output_buffer.write(self._indent * self._tab_width)
        self._output_buffer.write(
            f"<symbol> {self._tokenizer.current_token} </symbol>\n"
        )
        self._tokenizer.advance()

        # expression
        self.compile_expression()

        # )
        self._output_buffer.write(self._indent * self._tab_width)
        self._output_buffer.write(
            f"<symbol> {self._tokenizer.current_token} </symbol>\n"
        )
        self._tokenizer.advance()

        # {
        self._output_buffer.write(self._indent * self._tab_width)
        self._output_buffer.write(
            f"<symbol> {self._tokenizer.current_token} </symbol>\n"
        )
        self._tokenizer.advance()

        # statements
        self.compile_statements()

        # }
        self._output_buffer.write(self._indent * self._tab_width)
        self._output_buffer.write(
            f"<symbol> {self._tokenizer.current_token} </symbol>\n"
        )
        self._tokenizer.advance()

        if self._tokenizer.current_token == "else":
            # else
            self._output_buffer.write(self._indent * self._tab_width)
            self._output_buffer.write(
                f"<keyword> {self._tokenizer.current_token} </keyword>\n"
            )
            self._tokenizer.advance()

            # {
            self._output_buffer.write(self._indent * self._tab_width)
            self._output_buffer.write(
                f"<symbol> {self._tokenizer.current_token} </symbol>\n"
            )
            self._tokenizer.advance()

            self.compile_statements()

            # }
            self._output_buffer.write(self._indent * self._tab_width)
            self._output_buffer.write(
                f"<symbol> {self._tokenizer.current_token} </symbol>\n"
            )
            self._tokenizer.advance()

        self._indent -= 1
        self._output_buffer.write(self._indent * self._tab_width)
        self._output_buffer.write(f"</ifStatement>\n")

    def compile_while(self):
        self._output_buffer.write(self._indent * self._tab_width)
        self._output_buffer.write(f"<whileStatement>\n")
        self._indent += 1

        # while
        self._output_buffer.write(self._indent * self._tab_width)
        self._output_buffer.write(
            f"<keyword> {self._tokenizer.current_token} </keyword>\n"
        )
        self._tokenizer.advance()

        # (
        self._output_buffer.write(self._indent * self._tab_width)
        self._output_buffer.write(
            f"<symbol> {self._tokenizer.current_token} </symbol>\n"
        )
        self._tokenizer.advance()

        # expression
        self.compile_expression()

        # )
        self._output_buffer.write(self._indent * self._tab_width)
        self._output_buffer.write(
            f"<symbol> {self._tokenizer.current_token} </symbol>\n"
        )
        self._tokenizer.advance()

        # {
        self._output_buffer.write(self._indent * self._tab_width)
        self._output_buffer.write(
            f"<symbol> {self._tokenizer.current_token} </symbol>\n"
        )
        self._tokenizer.advance()

        self.compile_statements()

        # }
        self._output_buffer.write(self._indent * self._tab_width)
        self._output_buffer.write(
            f"<symbol> {self._tokenizer.current_token} </symbol>\n"
        )
        self._tokenizer.advance()

        self._indent -= 1
        self._output_buffer.write(self._indent * self._tab_width)
        self._output_buffer.write(f"</whileStatement>\n")

    def compile_do(self):
        """
        Compiles do statement.
        DO: 'do' subroutineCall ';'
        SUBROUTINECALL: subroutineName '(' expressionList ')' | ( className | varName)
                        '.' subroutineName '('expressionList ')'
        """
        self.validate_and_advance("do")
        # breakpoint()

        self.compile_subroutine_call()

        self.validate_and_advance(";")

        # discard value returned by subroutine call
        code = self._vm_writer.write_pop("temp", 0)
        self._output_buffer.write(code)

    def compile_return(self):
        self.validate_and_advance("return")

        if self._tokenizer.current_token != ";":
            self.compile_expression()
        else:
            code = self._vm_writer.write_push("constant", 0)
            self._output_buffer.write(code)

        self.validate_and_advance(";")

        code = self._vm_writer.write_return()
        self._output_buffer.write(code)

    def compile_subroutine_call(self):
        num_args = 0
        class_name = self._class_name
        function_name = self._tokenizer.current_token

        self._tokenizer.advance()
        # breakpoint()
        if self._tokenizer.current_token == ".":
            # breakpoint()
            class_name = function_name

            # method of object declared in class vars, push "this" onto stack
            if self._symbol_table.contains(class_name):
                num_args += 1
                kind = self._symbol_table.kind_of(class_name)
                index = self._symbol_table.index_of(class_name)
                code = self._vm_writer.write_push(SEGMENT_MAP[kind], index)
                self._output_buffer.write(code)

            self.validate_and_advance(".")
            function_name = self._tokenizer.current_token
            self._tokenizer.advance()

        # local method
        else:
            num_args += 1
            code = self._vm_writer.write_push("argument", 0)
            code += self._vm_writer.write_pop("pointer", 0)
            self._output_buffer.write(code)

        self.validate_and_advance("(")
        num_args += self.compile_expression_list()
        self.validate_and_advance(")")

        # breakpoint()
        code = self._vm_writer.write_call(class_name, function_name, num_args)
        self._output_buffer.write(code)

    def compile_expression(self):

        self.compile_term()
        if self._tokenizer.current_token in OP_LIST:
            op = self._tokenizer.current_token
            self.validate_and_advance(OP_LIST)
            self.compile_term()

            code = self._vm_writer.write_arithmetic(op)
            self._output_buffer.write(code)

    def compile_term(self):

        # term starting with "("
        # breakpoint()
        if self._tokenizer.current_token == "(":
            self.validate_and_advance("(")
            self.compile_expression()
            self.validate_and_advance(")")

        elif self._tokenizer.current_token in UNARY_OP_LIST:
            unary_op = self._tokenizer.current_token
            self.validate_and_advance(UNARY_OP_LIST)
            self.compile_term()
            code = self._vm_writer.write_unary(unary_op)
            self._output_buffer.write(code)

        else:
            if self._tokenizer.peek()[0] in ["(", "."]:
                pass

            elif self._tokenizer.peek()[0] == "[":
                # name of array
                name = self._tokenizer.current_token
                kind = self._symbol_table.kind_of(name)
                index = self._symbol_table.index_of(name)

                self._tokenizer.advance()
                self.validate_and_advance("[")
                self.compile_expression()
                self.validate_and_advance("]")

                # push array base address (already pushed by compile_expression)
                # push offest (element you want to access)
                # add
                # pop pointer 1 (to align THAT 0 with RAM address whose value is at THAT)
                # push that 0 (push value onto stack)

            # variable or constants
            else:
                name = self._tokenizer.current_token
                token_type = self._tokenizer.token_type

                if token_type == "identifier":
                    kind = self._symbol_table.kind_of(name)
                    index = self._symbol_table.index_of(name)
                    code = self._vm_writer.write_push(kind, index)

                elif token_type == "integer_constant":
                    code = self._vm_writer.write_push("constant", int(name))

                elif token_type == "string_constant":
                    code = "NOT IMPLEMENTED\n"

                elif name in ["true", "false", "null", "this"]:
                    code = self._vm_writer.write_term(name)

                else:
                    code = "NOT POSSIBLE\n"

                self._output_buffer.write(code)
                self._tokenizer.advance()

    def compile_expression_list(self) -> int:
        num_args = 0
        # breakpoint()
        if self._tokenizer.token_type in [
            "integer_constant",
            "identifier",
        ] or self._tokenizer.current_token in ["("]:
            self.compile_expression()
            num_args += 1

            while self._tokenizer.current_token == ",":
                self.validate_and_advance(",")
                self.compile_expression()
                num_args += 1

        return num_args


if __name__ == "__main__":
    file_path = Path("../Seven/Main.jack")
    # file_path = Path("../Square/SquareGame.jack")
    jack_tokenizer = JackTokenizer(file_path)
    symbol_table = SymbolTable()
    vm_writer = VMWriter()

    compilation_engine = CompilationEngine(
        input_path=file_path,
        tokenizer=jack_tokenizer,
        symbol_table=symbol_table,
        vm_writer=vm_writer,
    )

    compilation_engine.compile_class()
    # compilation_engine.write_output()
