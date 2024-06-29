from io import StringIO
from jack_tokenizer import JackTokenizer
from pathlib import Path

# this needs a lot of refactoring
# just wanted to get it to work

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


class CompilationError(Exception):
    pass


class CompilationEngine:
    def __init__(
        self,
        input_path: Path,
        tokenizer: JackTokenizer,
        starting_token: str = "tokens",
        output_suffix: str = "",
    ):
        self._input_path = input_path
        self._tokenizer = tokenizer
        self._output_buffer = StringIO()
        self._indent = 0
        self._tab_width = " " * 2
        self._stating_token = starting_token
        self._output_suffix = output_suffix
        self._output_path = self._create_output_path()

    def write_output(self):
        with self._output_path.open("w") as f:
            print(self._output_buffer.getvalue(), file=f)

    def _create_output_path(self):
        return (
            self._input_path.parent
            / f"{self._input_path.name.split('.')[0]}{self._output_suffix}.xml"
        )

    def compile_class(self):
        self._output_buffer.write(f"<{self._stating_token}>\n")
        self._indent += 1

        # compile class keyword
        self._tokenizer.advance()
        if self._tokenizer.current_token == "class":
            self._output_buffer.write(self._indent * self._tab_width)
            self._output_buffer.write(
                f"<keyword> {self._tokenizer.current_token} </keyword>\n"
            )
            self._tokenizer.advance()
        else:
            raise CompilationError(
                f"Invalid program. The first token should be 'class' but is {self._tokenizer.current_token}"
            )

        # compile class name
        if self._tokenizer.token_type == JackTokenizer.IDENTIFIER:
            self._output_buffer.write(self._indent * self._tab_width)
            self._output_buffer.write(
                f"<identifier> {self._tokenizer.current_token} </identifier>\n"
            )
            self._tokenizer.advance()
        else:
            raise CompilationError(
                f"Invalid program. Current token {self._tokenizer.current_token}"
            )

        while self._tokenizer.has_more_tokens():

            # compile "{"
            if self._tokenizer.token_type == JackTokenizer.SYMBOL:
                self._output_buffer.write(self._indent * self._tab_width)
                self._output_buffer.write(
                    f"<symbol> {self._tokenizer.current_token} </symbol>\n"
                )
                self._tokenizer.advance()
            else:
                raise CompilationError(
                    f"Invalid program. Current token {self._tokenizer.current_token}"
                )

            self.compile_class_var_dec()

            self.compile_subroutine_dec()

            # compile "{"
            self._output_buffer.write(self._indent * self._tab_width)
            self._output_buffer.write(
                f"<symbol> {self._tokenizer.current_token} </symbol>\n"
            )
            self._tokenizer.advance()

        self._output_buffer.write(f"</{self._stating_token}>")

    def compile_class_var_dec(self):

        while self._tokenizer.current_token in ["static", "field"]:
            self._output_buffer.write(self._indent * self._tab_width)
            self._output_buffer.write(f"<classVarDec>\n")
            self._indent += 1

            self._output_buffer.write(self._indent * self._tab_width)
            self._output_buffer.write(
                f"<keyword> {self._tokenizer.current_token} </keyword>\n"
            )
            self._tokenizer.advance()

            # type
            if self._tokenizer.current_token in ["int", "char", "boolean"]:
                self._output_buffer.write(self._indent * self._tab_width)
                self._output_buffer.write(
                    f"<keyword> {self._tokenizer.current_token} </keyword>\n"
                )
                self._tokenizer.advance()
            elif self._tokenizer.token_type == JackTokenizer.IDENTIFIER:
                self._output_buffer.write(self._indent * self._tab_width)
                self._output_buffer.write(
                    f"<identifier> {self._tokenizer.current_token} </identifier>\n"
                )
                self._tokenizer.advance()

            # var name
            if self._tokenizer.token_type == JackTokenizer.IDENTIFIER:
                self._output_buffer.write(self._indent * self._tab_width)
                self._output_buffer.write(
                    f"<identifier> {self._tokenizer.current_token} </identifier>\n"
                )
                self._tokenizer.advance()

            # ,
            if self._tokenizer.current_token == ",":
                while self._tokenizer.current_token != ";":
                    self._output_buffer.write(self._indent * self._tab_width)
                    self._output_buffer.write(
                        f"<symbol> {self._tokenizer.current_token} </symbol>\n"
                    )
                    self._tokenizer.advance()

                    self._output_buffer.write(self._indent * self._tab_width)
                    self._output_buffer.write(
                        f"<identifier> {self._tokenizer.current_token} </identifier>\n"
                    )
                    self._tokenizer.advance()

            # ;
            self._output_buffer.write(self._indent * self._tab_width)
            self._output_buffer.write(
                f"<symbol> {self._tokenizer.current_token} </symbol>\n"
            )
            self._tokenizer.advance()

            self._indent -= 1
            self._output_buffer.write(self._indent * self._tab_width)
            self._output_buffer.write(f"</classVarDec>\n")

    def compile_subroutine_dec(self):
        if self._tokenizer.current_token in ["constructor", "function", "method"]:

            while self._tokenizer.token_type == JackTokenizer.KEYWORD:
                self._output_buffer.write(self._indent * self._tab_width)
                self._output_buffer.write(f"<subroutineDec>\n")
                self._indent += 1

                self._output_buffer.write(self._indent * self._tab_width)
                self._output_buffer.write(
                    f"<keyword> {self._tokenizer.current_token} </keyword>\n"
                )
                self._tokenizer.advance()

                if self._tokenizer.token_type == JackTokenizer.IDENTIFIER:
                    self._output_buffer.write(self._indent * self._tab_width)
                    self._output_buffer.write(
                        f"<identifier> {self._tokenizer.current_token} </identifier>\n"
                    )
                    self._tokenizer.advance()
                elif self._tokenizer.current_token in [
                    "void"
                ] or self._tokenizer.token_type in ["int", "char", "boolean"]:
                    self._output_buffer.write(self._indent * self._tab_width)
                    self._output_buffer.write(
                        f"<keyword> {self._tokenizer.current_token} </keyword>\n"
                    )
                    self._tokenizer.advance()

                # subroutine name
                self._output_buffer.write(self._indent * self._tab_width)
                self._output_buffer.write(
                    f"<identifier> {self._tokenizer.current_token} </identifier>\n"
                )
                self._tokenizer.advance()

                self.compile_parameter_list()

                self.compile_subroutine_body()

                self._indent -= 1
                self._output_buffer.write(self._indent * self._tab_width)
                self._output_buffer.write(f"</subroutineDec>\n")
        else:
            raise CompilationError(
                f"Invalid program. Current token {self._tokenizer.current_token}"
            )

    def compile_parameter_list(self):
        # (
        self._output_buffer.write(self._indent * self._tab_width)
        self._output_buffer.write(
            f"<symbol> {self._tokenizer.current_token} </symbol>\n"
        )
        self._tokenizer.advance()

        self._output_buffer.write(self._indent * self._tab_width)
        self._output_buffer.write(f"<parameterList>\n")
        self._indent += 1

        if (
            self._tokenizer.current_token in ["int", "char", "boolean"]
            or self._tokenizer.token_type == JackTokenizer.KEYWORD
        ):
            # type
            if self._tokenizer.current_token in ["int", "char", "boolean"]:
                self._output_buffer.write(self._indent * self._tab_width)
                self._output_buffer.write(
                    f"<keyword> {self._tokenizer.current_token} </keyword>\n"
                )
                self._tokenizer.advance()
            elif self._tokenizer.token_type == JackTokenizer.KEYWORD:
                self._output_buffer.write(self._indent * self._tab_width)
                self._output_buffer.write(
                    f"<keyword> {self._tokenizer.current_token} </keyword>\n"
                )
                self._tokenizer.advance()

            # var name
            if self._tokenizer.token_type == JackTokenizer.IDENTIFIER:
                self._output_buffer.write(self._indent * self._tab_width)
                self._output_buffer.write(
                    f"<identifier> {self._tokenizer.current_token} </identifier>\n"
                )
                self._tokenizer.advance()

            # ,
            if self._tokenizer.current_token == ",":
                self._output_buffer.write(self._indent * self._tab_width)
                self._output_buffer.write(
                    f"<symbol> {self._tokenizer.current_token} </symbol>\n"
                )
                self._tokenizer.advance()
                while self._tokenizer.current_token != ")":
                    self._output_buffer.write(self._indent * self._tab_width)
                    self._output_buffer.write(
                        f"<{self._tokenizer.token_type}> {self._tokenizer.current_token} </{self._tokenizer.token_type}>\n"
                    )
                    self._tokenizer.advance()

        self._indent -= 1
        self._output_buffer.write(self._indent * self._tab_width)
        self._output_buffer.write(f"</parameterList>\n")

        # )
        self._output_buffer.write(self._indent * self._tab_width)
        self._output_buffer.write(
            f"<symbol> {self._tokenizer.current_token} </symbol>\n"
        )
        self._tokenizer.advance()

    def compile_subroutine_body(self):
        self._output_buffer.write(self._indent * self._tab_width)
        self._output_buffer.write(f"<subroutineBody>\n")
        self._indent += 1

        if self._tokenizer.current_token == "{":
            # {
            self._output_buffer.write(self._indent * self._tab_width)
            self._output_buffer.write(
                f"<symbol> {self._tokenizer.current_token} </symbol>\n"
            )
            self._tokenizer.advance()

            self.compile_var_dec()

            self.compile_statements()

            # }
            self._output_buffer.write(self._indent * self._tab_width)
            self._output_buffer.write(
                f"<symbol> {self._tokenizer.current_token} </symbol>\n"
            )
            self._tokenizer.advance()
        else:
            raise CompilationError(
                f"Invalid program. Current token {self._tokenizer.current_token}"
            )

        self._indent -= 1
        self._output_buffer.write(self._indent * self._tab_width)
        self._output_buffer.write(f"</subroutineBody>\n")

    def compile_var_dec(self):

        while self._tokenizer.current_token == "var":
            self._output_buffer.write(self._indent * self._tab_width)
            self._output_buffer.write(f"<varDec>\n")
            self._indent += 1

            # var
            self._output_buffer.write(self._indent * self._tab_width)
            self._output_buffer.write(
                f"<keyword> {self._tokenizer.current_token} </keyword>\n"
            )
            self._tokenizer.advance()

            # type
            if self._tokenizer.current_token in ["int", "char", "boolean"]:
                self._output_buffer.write(self._indent * self._tab_width)
                self._output_buffer.write(
                    f"<keyword> {self._tokenizer.current_token} </keyword>\n"
                )
                self._tokenizer.advance()
            elif self._tokenizer.token_type == JackTokenizer.IDENTIFIER:
                self._output_buffer.write(self._indent * self._tab_width)
                self._output_buffer.write(
                    f"<identifier> {self._tokenizer.current_token} </identifier>\n"
                )
                self._tokenizer.advance()

            # var name
            if self._tokenizer.token_type == JackTokenizer.IDENTIFIER:
                self._output_buffer.write(self._indent * self._tab_width)
                self._output_buffer.write(
                    f"<identifier> {self._tokenizer.current_token} </identifier>\n"
                )
                self._tokenizer.advance()

            # ,
            if self._tokenizer.current_token == ",":
                while self._tokenizer.current_token != ";":
                    self._output_buffer.write(self._indent * self._tab_width)
                    self._output_buffer.write(
                        f"<symbol> {self._tokenizer.current_token} </symbol>\n"
                    )
                    self._tokenizer.advance()

                    self._output_buffer.write(self._indent * self._tab_width)
                    self._output_buffer.write(
                        f"<identifier> {self._tokenizer.current_token} </identifier>\n"
                    )
                    self._tokenizer.advance()

            # ;
            if self._tokenizer.token_type == JackTokenizer.SYMBOL:
                self._output_buffer.write(self._indent * self._tab_width)
                self._output_buffer.write(
                    f"<symbol> {self._tokenizer.current_token} </symbol>\n"
                )
                self._tokenizer.advance()

            self._indent -= 1
            self._output_buffer.write(self._indent * self._tab_width)
            self._output_buffer.write(f"</varDec>\n")

    def compile_statements(self):
        self._output_buffer.write(self._indent * self._tab_width)
        self._output_buffer.write(f"<statements>\n")
        self._indent += 1

        if self._tokenizer.token_type == JackTokenizer.KEYWORD:
            while self._tokenizer.current_token != "}":
                if self._tokenizer.current_token == "let":
                    self.compile_let()
                elif self._tokenizer.current_token == "if":
                    self.compile_if()
                elif self._tokenizer.current_token == "while":
                    self.compile_while()
                elif self._tokenizer.current_token == "do":
                    self.compile_do()
                elif self._tokenizer.current_token == "return":
                    self.compile_return()

        self._indent -= 1
        self._output_buffer.write(self._indent * self._tab_width)
        self._output_buffer.write(f"</statements>\n")

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
        self._output_buffer.write(self._indent * self._tab_width)
        self._output_buffer.write(f"<doStatement>\n")
        self._indent += 1

        # do
        self._output_buffer.write(self._indent * self._tab_width)
        self._output_buffer.write(
            f"<keyword> {self._tokenizer.current_token} </keyword>\n"
        )
        self._tokenizer.advance()

        # subroutine call
        # check next token to determine format or subroutine call
        # method() or object.method()
        next_token, _ = self._tokenizer.peek()

        # subroutine name
        self._output_buffer.write(self._indent * self._tab_width)
        self._output_buffer.write(
            f"<identifier> {self._tokenizer.current_token} </identifier>\n"
        )
        self._tokenizer.advance()

        if next_token == ".":
            # .
            self._output_buffer.write(self._indent * self._tab_width)
            self._output_buffer.write(
                f"<symbol> {self._tokenizer.current_token} </symbol>\n"
            )
            self._tokenizer.advance()

            # subroutine name
            self._output_buffer.write(self._indent * self._tab_width)
            self._output_buffer.write(
                f"<identifier> {self._tokenizer.current_token} </identifier>\n"
            )
            self._tokenizer.advance()

        # (
        self._output_buffer.write(self._indent * self._tab_width)
        self._output_buffer.write(
            f"<symbol> {self._tokenizer.current_token} </symbol>\n"
        )
        self._tokenizer.advance()

        self.compile_expression_list()

        # )
        self._output_buffer.write(self._indent * self._tab_width)
        self._output_buffer.write(
            f"<symbol> {self._tokenizer.current_token} </symbol>\n"
        )
        self._tokenizer.advance()

        # ;
        self._output_buffer.write(self._indent * self._tab_width)
        self._output_buffer.write(
            f"<symbol> {self._tokenizer.current_token} </symbol>\n"
        )
        self._tokenizer.advance()

        self._indent -= 1
        self._output_buffer.write(self._indent * self._tab_width)
        self._output_buffer.write(f"</doStatement>\n")

    def compile_return(self):
        self._output_buffer.write(self._indent * self._tab_width)
        self._output_buffer.write(f"<returnStatement>\n")
        self._indent += 1

        # return
        self._output_buffer.write(self._indent * self._tab_width)
        self._output_buffer.write(
            f"<keyword> {self._tokenizer.current_token} </keyword>\n"
        )
        self._tokenizer.advance()

        if self._tokenizer.current_token != ";":
            while self._tokenizer.current_token != ";":
                # expression
                self.compile_expression()

            # ;
            self._output_buffer.write(self._indent * self._tab_width)
            self._output_buffer.write(
                f"<symbol> {self._tokenizer.current_token} </symbol>\n"
            )
            self._tokenizer.advance()
        else:
            # ;
            self._output_buffer.write(self._indent * self._tab_width)
            self._output_buffer.write(
                f"<symbol> {self._tokenizer.current_token} </symbol>\n"
            )
            self._tokenizer.advance()

        self._indent -= 1
        self._output_buffer.write(self._indent * self._tab_width)
        self._output_buffer.write(f"</returnStatement>\n")

    def compile_expression(self):
        self._output_buffer.write(self._indent * self._tab_width)
        self._output_buffer.write(f"<expression>\n")
        self._indent += 1

        self.compile_term()

        self._indent -= 1
        self._output_buffer.write(self._indent * self._tab_width)
        self._output_buffer.write(f"</expression>\n")

    def compile_term(self):

        if self._tokenizer.current_token in OP_LIST:
            # need custom logic here to handle the case where the
            # operator generates a new term tag and when it doesn't
            term_tag = False
            if self._tokenizer.previous_token == "(":
                self._output_buffer.write(self._indent * self._tab_width)
                self._output_buffer.write(f"<term>\n")
                self._indent += 1

                term_tag = True

            self._output_buffer.write(self._indent * self._tab_width)
            current_token = self._tokenizer.current_token
            mapping = {"<": "&lt;", ">": "&gt;", "&": "&amp;", '"': "&quot;"}

            if self._tokenizer.current_token in mapping:
                current_token = mapping[self._tokenizer.current_token]
            self._output_buffer.write(
                f"<{self._tokenizer.token_type}> {current_token} </{self._tokenizer.token_type}>\n"
            )
            self._tokenizer.advance()

            self.compile_term()

            if term_tag:
                self._indent -= 1
                self._output_buffer.write(self._indent * self._tab_width)
                self._output_buffer.write(f"</term>\n")

        # this is what supports nested expressions ((()))
        if self._tokenizer.current_token == "(":
            self._output_buffer.write(self._indent * self._tab_width)
            self._output_buffer.write(f"<term>\n")
            self._indent += 1

            # (
            self._output_buffer.write(self._indent * self._tab_width)
            self._output_buffer.write(
                f"<symbol> {self._tokenizer.current_token} </symbol>\n"
            )
            self._tokenizer.advance()

            self.compile_expression()

            # )
            if self._tokenizer.current_token == ")":
                self._output_buffer.write(self._indent * self._tab_width)
                self._output_buffer.write(
                    f"<symbol> {self._tokenizer.current_token} </symbol>\n"
                )
                self._tokenizer.advance()

                self._indent -= 1
                self._output_buffer.write(self._indent * self._tab_width)
                self._output_buffer.write(f"</term>\n")

                self.compile_term()
            else:
                self._output_buffer.write(self._indent * self._tab_width)
                self._output_buffer.write(
                    f"<symbol> {self._tokenizer.current_token} </symbol>\n"
                )
                self._tokenizer.advance()

                self._indent -= 1
                self._output_buffer.write(self._indent * self._tab_width)
                self._output_buffer.write(f"</term>\n")

        # check is constant or starts with -|~
        elif (
            self._tokenizer.token_type
            in [
                JackTokenizer.INTEGER_CONSTANT,
                JackTokenizer.STRING_CONST,
                JackTokenizer.IDENTIFIER,
                JackTokenizer.KEYWORD,
            ]
            or self._tokenizer.current_token in UNARY_OP_LIST
        ):
            self._output_buffer.write(self._indent * self._tab_width)
            self._output_buffer.write(f"<term>\n")
            self._indent += 1

            # maybe not needed
            next_token, _ = self._tokenizer.peek()
            if (
                self._tokenizer.current_token in UNARY_OP_LIST
                and next_token != JackTokenizer.INTEGER_CONSTANT
            ):
                self._output_buffer.write(self._indent * self._tab_width)
                self._output_buffer.write(
                    f"<{self._tokenizer.token_type}> {self._tokenizer.current_token} </{self._tokenizer.token_type}>\n"
                )
                self._tokenizer.advance()

                self.compile_term()

                self._indent -= 1
                self._output_buffer.write(self._indent * self._tab_width)
                self._output_buffer.write(f"</term>\n")

                return

            self._output_buffer.write(self._indent * self._tab_width)

            if self._tokenizer.token_type in JackTokenizer.STRING_CONST:
                self._output_buffer.write(
                    f"<stringConstant> {self._tokenizer.current_token} </stringConstant>\n"
                )
            elif self._tokenizer.token_type in JackTokenizer.INTEGER_CONSTANT:
                self._output_buffer.write(
                    f"<integerConstant> {self._tokenizer.current_token} </integerConstant>\n"
                )
            else:
                self._output_buffer.write(
                    f"<{self._tokenizer.token_type}> {self._tokenizer.current_token} </{self._tokenizer.token_type}>\n"
                )
            self._tokenizer.advance()

            if self._tokenizer.current_token not in ["[", "(", "."]:
                self._indent -= 1
                self._output_buffer.write(self._indent * self._tab_width)
                self._output_buffer.write(f"</term>\n")

            if self._tokenizer.current_token in OP_LIST:
                # op (operator)
                self._output_buffer.write(self._indent * self._tab_width)
                current_token = self._tokenizer.current_token
                mapping = {"<": "&lt;", ">": "&gt;", "&": "&amp;", '"': "&quot;"}

                if self._tokenizer.current_token in mapping:
                    current_token = mapping[self._tokenizer.current_token]
                self._output_buffer.write(
                    f"<{self._tokenizer.token_type}> {current_token} </{self._tokenizer.token_type}>\n"
                )
                self._tokenizer.advance()

                self.compile_term()

            if self._tokenizer.current_token == "[":
                # [
                self._output_buffer.write(self._indent * self._tab_width)
                self._output_buffer.write(
                    f"<{self._tokenizer.token_type}> {self._tokenizer.current_token} </{self._tokenizer.token_type}>\n"
                )
                self._tokenizer.advance()

                self.compile_expression()

                # ]
                self._output_buffer.write(self._indent * self._tab_width)
                self._output_buffer.write(
                    f"<{self._tokenizer.token_type}> {self._tokenizer.current_token} </{self._tokenizer.token_type}>\n"
                )
                self._tokenizer.advance()

                self._indent -= 1
                self._output_buffer.write(self._indent * self._tab_width)
                self._output_buffer.write(f"</term>\n")

            # this might not get used????
            # doesn't stop at breakpoint for Square.jack
            if self._tokenizer.current_token == "(":
                # "("
                self._output_buffer.write(self._indent * self._tab_width)
                self._output_buffer.write(
                    f"<symbol> {self._tokenizer.current_token} </symbol>\n"
                )
                self._tokenizer.advance()

                self.compile_expression_list()

                # ")"
                self._output_buffer.write(self._indent * self._tab_width)
                self._output_buffer.write(
                    f"<symbol> {self._tokenizer.current_token} </symbol>\n"
                )
                self._tokenizer.advance()

                self._indent -= 1
                self._output_buffer.write(self._indent * self._tab_width)
                self._output_buffer.write(f"</term>\n")

            # subroutine call
            elif self._tokenizer.current_token == ".":
                # "."
                self._output_buffer.write(self._indent * self._tab_width)
                self._output_buffer.write(
                    f"<symbol> {self._tokenizer.current_token} </symbol>\n"
                )
                self._tokenizer.advance()

                # subroutine name (identifier)
                self._output_buffer.write(self._indent * self._tab_width)
                self._output_buffer.write(
                    f"<identifier> {self._tokenizer.current_token} </identifier>\n"
                )
                self._tokenizer.advance()

                # "("
                self._output_buffer.write(self._indent * self._tab_width)
                self._output_buffer.write(
                    f"<symbol> {self._tokenizer.current_token} </symbol>\n"
                )
                self._tokenizer.advance()

                self.compile_expression_list()

                # ")"
                self._output_buffer.write(self._indent * self._tab_width)
                self._output_buffer.write(
                    f"<symbol> {self._tokenizer.current_token} </symbol>\n"
                )
                self._tokenizer.advance()

                self._indent -= 1
                self._output_buffer.write(self._indent * self._tab_width)
                self._output_buffer.write(f"</term>\n")

    def compile_expression_list(self):
        self._output_buffer.write(self._indent * self._tab_width)
        self._output_buffer.write(f"<expressionList>\n")
        self._indent += 1

        if self._tokenizer.current_token != ")":
            self.compile_expression()

            while self._tokenizer.current_token == ",":
                # ,
                self._output_buffer.write(self._indent * self._tab_width)
                self._output_buffer.write(
                    f"<symbol> {self._tokenizer.current_token} </symbol>\n"
                )
                self._tokenizer.advance()

                self.compile_expression()

        self._indent -= 1
        self._output_buffer.write(self._indent * self._tab_width)
        self._output_buffer.write(f"</expressionList>\n")


if __name__ == "__main__":
    file_path = Path("../Square/SquareGame.jack")
    jack_tokenizer = JackTokenizer(file_path)

    compilation_engine = CompilationEngine(
        input_path=file_path,
        tokenizer=jack_tokenizer,
        starting_token="class",
        output_suffix="-2",
    )

    compilation_engine.compile_class()
    compilation_engine.write_output()
