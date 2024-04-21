from io import StringIO
from jack_tokenizer import JackTokenizer
from pathlib import Path


class CompilationError(Exception):
    pass

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
class CompilationEngine:
    def __init__(
        self,
        input_path,
        tokenizer: JackTokenizer,
        output_buffer=StringIO(),
        starting_token="tokens",
    ):
        self._input_path = input_path
        self._tokenizer = tokenizer
        self._output_buffer = output_buffer
        self._indent = 0
        self._tab_width = " " * 2
        self._stating_token = starting_token
        self._output_path = Path("../ExpressionLessSquare/Main-2.xml")

    def write_output(self):
        with self._output_path.open("w") as f:
            print(self._output_buffer.getvalue(), file=f)

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

            # self.compile_statements()

            # compile "{"
            self._output_buffer.write(self._indent * self._tab_width)
            self._output_buffer.write(
                f"<symbol> {self._tokenizer.current_token} </symbol>\n"
            )
            self._tokenizer.advance()

        self._output_buffer.write(f"</{self._stating_token}>\n")

    def compile_class_var_dec(self):
        if self._tokenizer.current_token in ["static", "field"]:
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
            self._output_buffer.write(f"</classVarDec>\n")
        else:
            raise CompilationError(
                f"Invalid program. Current token {self._tokenizer.current_token}"
            )

    def compile_subroutine_dec(self):
        # self._tokenizer.advance()
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

                # void or type
                # TODO: tag might be wrong if the current token is an identifier
                # same for classVarDec
                if (
                    self._tokenizer.token_type == JackTokenizer.IDENTIFIER
                    or self._tokenizer.token_type in ["int", "char", "boolean"]
                ):
                    self._output_buffer.write(self._indent * self._tab_width)
                    self._output_buffer.write(
                        f"<keyword> {self._tokenizer.current_token} </keyword>\n"
                    )
                    self._tokenizer.advance()
                elif self._tokenizer.current_token in ["void"]:
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
                        f"<{self._tokenizer.token_type}> {self._tokenizer.current_token} <\{self._tokenizer.token_type}>\n"
                    )
                    self._tokenizer.advance()

                # )
                self._output_buffer.write(self._indent * self._tab_width)
                self._output_buffer.write(
                    f"<symbol> {self._tokenizer.current_token} </symbol>\n"
                )
                self._tokenizer.advance()
        else:
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
        self._output_buffer.write(self._indent * self._tab_width)
        self._output_buffer.write(f"<varDec>\n")
        self._indent += 1

        if self._tokenizer.current_token == "var":
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
                # else:
                #     # handle empty else condition
                #     # }
                #     self._output_buffer.write(f"<symbol> {self._tokenizer.current_token} <\symbol>\n")
                #     self._tokenizer.advance()

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
        # THIS IS THE PART THAT NEEDS FIXING
        self._output_buffer.write(self._indent * self._tab_width)
        self._output_buffer.write(
            f"<identifier> {self._tokenizer.current_token} </identifier>\n"
        )
        self._tokenizer.advance()

        # =
        self._output_buffer.write(self._indent * self._tab_width)
        self._output_buffer.write(
            f"<symbol> {self._tokenizer.current_token} </symbol>\n"
        )
        self._tokenizer.advance()

        # var name
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

        # var name
        self._output_buffer.write(self._indent * self._tab_width)
        self._output_buffer.write(
            f"<identifier> {self._tokenizer.current_token} </identifier>\n"
        )
        self._tokenizer.advance()

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

        # # var name
        # self._output_buffer.write(f"<identifier> {self._tokenizer.current_token} <\identifier>\n")
        # self._tokenizer.advance()
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

        # var name
        self._output_buffer.write(self._indent * self._tab_width)
        self._output_buffer.write(
            f"<identifier> {self._tokenizer.current_token} </identifier>\n"
        )
        self._tokenizer.advance()

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

        # var name
        self._output_buffer.write(self._indent * self._tab_width)
        self._output_buffer.write(
            f"<identifier> {self._tokenizer.current_token} </identifier>\n"
        )
        self._tokenizer.advance()

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
        # subroutine name
        self._output_buffer.write(self._indent * self._tab_width)
        self._output_buffer.write(
            f"<identifier> {self._tokenizer.current_token} </identifier>\n"
        )
        self._tokenizer.advance()

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
                # var name
                self._output_buffer.write(self._indent * self._tab_width)
                self._output_buffer.write(
                    f"<identifier> {self._tokenizer.current_token} </identifier>\n"
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
        self._output_buffer.write(self._indent * self._tab_width)
        self._output_buffer.write(f"<term>\n")
        self._indent += 1

        if self._tokenizer.current_token == "(":
            pass
        # check is constant
        elif self._tokenizer.current_token in [
            JackTokenizer.INTEGER_CONSTANT,
            JackTokenizer.STRING_CONST,
            JackTokenizer.IDENTIFIER,
        ] or self._tokenizer.current_token in OP_LIST:
            if self._tokenizer.current_token in OP_LIST:
                self._output_buffer.write(self._indent * self._tab_width)
                self._output_buffer.write(
                    f"<{self._tokenizer.token_type}> {self._tokenizer.current_token} </{self._tokenizer.token_type}>\n"
                )
                self._tokenizer.advance()

            self._output_buffer.write(self._indent * self._tab_width)
            self._output_buffer.write(
                f"<{self._tokenizer.token_type}> {self._tokenizer.current_token} </{self._tokenizer.token_type}>\n"
            )
            self._tokenizer.advance()

            next_token, next_type = self._tokenizer.peek()
            if next_token == "[":
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

    def compile_expression_list(self):
        self._output_buffer.write(self._indent * self._tab_width)
        self._output_buffer.write(f"<expressionList>\n")

        if self._tokenizer.current_token != ")":
            self.compile_expression()

            while self._tokenizer.current_token == ",":
                self.compile_expression()

        self._output_buffer.write(self._indent * self._tab_width)
        self._output_buffer.write(f"</expressionList>\n")


if __name__ == "__main__":
    file_path = "../ExpressionLessSquare/Main.jack"
    jack_tokenizer = JackTokenizer(file_path)

    compilation_engine = CompilationEngine(
        input_path=file_path, tokenizer=jack_tokenizer, starting_token="class"
    )
    compilation_engine.compile_class()
    compilation_engine.write_output()
