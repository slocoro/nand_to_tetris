from io import StringIO


class VMWriter:
    ARITHMETIC_OPS = {
        "+": "add",
        "-": "sub",
        "=": "eq",
        ">": "gt",
        "<": "lt",
        "&": "and",
        "|": "or",
        "*": "call Math.multiply 2",
        "/": "call Math.divide 2",
        "~": "not",
        # might be missing "-"
    }
    UNARY_OPS = {"-": "neg", "~": "not"}

    TERMS_MAP = {
        "true": "push constant 0\nnot\n",
        "false": "push constant 0\n",
        "null": "push constant 0\n",
        "this": "push pointer 0\n",
    }

    def write_push(self, segment: str, index: int):
        return f"push {segment} {index}\n"

    def write_pop(self, segment: str, index: int):
        return f"pop {segment} {index}\n"

    def write_arithmetic(self, command: str):
        return f"{self.ARITHMETIC_OPS[command]}\n"

    def write_unary(self, command: str):
        return f"{self.UNARY_OPS[command]}\n"

    def write_string(self, string: str):
        code = f"push constant {str(len(string))}\n"
        code += "call String.new 1\n"

        for char in string:
            code += f"push constant {str(ord(char))}\n"
            code += "call String.appendChar 2\n"

        return code

    def write_label(self, label: str):
        return f"label {label}\n"

    def write_if_goto(self, label: str):
        return f"if-goto {label}\n"

    def write_goto(self, label: str):
        return f"goto {label}\n"

    def write_call(self, class_name: str, function_name: str, n_args: int):
        return f"call {class_name}.{function_name} {n_args}\n"

    def write_function(self, class_name: str, funcion_name: str, n_locals: int):
        return f"function {class_name}.{funcion_name} {n_locals}\n"

    def write_return(self):
        return "return\n"

    def write_term(self, term):
        """
        Writes simple terms: true, false, null, this
        """
        code = self.TERMS_MAP[term]
        return code
