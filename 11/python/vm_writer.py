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
    }
    UNARY_OPS = {"-": "neg", "~": "not"}

    TERMS_MAP = {
        "true": "push constant 0\nnot\n",
        "false": "push constant 0\n",
        "null": "push constant 0\n",
        "this": "push pointer 0\n",
    }
    # def __init__(self):
    # self._output_buffer = StringIO()

    def write_push(self, segment: str, index: int):
        # self._output_buffer.write(f"push {segment} {index}\n")
        return f"push {segment} {index}\n"

    def write_pop(self, segment: str, index: int):
        # self._output_buffer.write(f"pop {segment} {index}\n")
        return f"pop {segment} {index}\n"

    def write_arithmetic(self, command: str):
        # self._output_buffer.write(f"{self.ARITHMETIC_OPS[command]}\n")
        return f"{self.ARITHMETIC_OPS[command]}\n"

    def write_unary(self, command: str):
        # self._output_buffer.write(f"{self.UNARY_OPS[command]}\n")
        return f"{self.UNARY_OPS[command]}\n"

    def write_label(self, label: str):
        # self._output_buffer.write(f"label {label}\n")
        return f"label {label}\n"

    def write_if_goto(self, label: str):
        # self._output_buffer.write(f"if-goto {label}\n")
        return f"if-goto {label}\n"

    def write_goto(self, label: str):
        # self._output_buffer.write(f"goto {label}\n")
        return f"goto {label}\n"

    def write_call(self, class_name: str, function_name: str, n_args: int):
        # self._output_buffer.write(f"call {name} {n_args}\n")
        return f"call {class_name}.{function_name} {n_args}\n"

    def write_function(self, class_name: str, funcion_name: str, n_locals: int):
        # self._output_buffer.write(f"function {name} {n_locals}\n")
        return f"function {class_name}.{funcion_name} {n_locals}\n"

    def write_return(self):
        # self._output_buffer.write("return\n")
        return "return\n"

    def write_term(self, term):
        """
        Writes simple terms: true, false, null, this
        """

        code = self.TERMS_MAP[term]
        return code

    # def close(self, output_path: str):
    # pass
