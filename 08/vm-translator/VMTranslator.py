from dataclasses import dataclass
from io import StringIO
import textwrap
import uuid
import sys
import re
from typing import Optional


@dataclass
class Commands:
    C_ARITHMETIC = "C_ARITHMETIC"
    C_PUSH = "C_PUSH"
    C_POP = "C_POP"
    C_LABEL = "C_LABEL"
    C_GOTO = "C_GOTO"
    C_IF_GOTO = "C_IF_GOTO"
    C_FUNCTION = "C_FUNCTION"
    C_RETURN = "C_RETURN"
    C_CALL = "C_CALL"

class Parser:

    def __init__(self, file_path: str):
        self.file_path = file_path
        self.current_command: Optional[str] = None
        self.file = self._read_file_line_by_line()
        self.file_name = self._get_file_name()

    def has_more_commands(self):
        try:
            while True:
                line = next(self.file)
                line = line.strip(" ")
                if line.startswith("//") or len(line) == 0:
                    continue
                else:
                    self._pending_command = line
                    return True
        except StopIteration:
            print("No more commands")
            return False

    def advance(self):
        self.current_command = self._pending_command
        print(f"Current command: {self.current_command}")
        self._get_command_type()
        self._get_arg_1()
        self._get_arg_2()

    def _get_file_name(self):
        return self.file_path.split("/")[-1].split(".")[0]

    def _get_command_type(self):
        if self.current_command is not None:
            if self.current_command.startswith("push"):
                self.command_type = Commands.C_PUSH
            if self.current_command.startswith("pop"):
                self.command_type = Commands.C_POP
            if self.current_command.startswith(tuple(["add", "sub", "eq", "neg", "lt", "gt", "and", "or", "not"])):
                self.command_type = Commands.C_ARITHMETIC
            if self.current_command.startswith("call"):
                self.command_type = Commands.C_CALL
            if self.current_command.startswith("if"):
                self.command_type = Commands.C_IF_GOTO
            if self.current_command.startswith("goto"):
                self.command_type = Commands.C_GOTO
            if self.current_command.startswith("label"):
                self.command_type = Commands.C_LABEL
            if self.current_command.startswith("return"):
                self.command_type = Commands.C_RETURN
            if self.current_command.startswith("function"):
                self.command_type = Commands.C_FUNCTION
        else:
            print("current_command is not set.")
            self.current_command = None

    def _get_arg_1(self):
        if self.command_type == Commands.C_ARITHMETIC:
            self.arg_1 == self.current_command
        elif self.command_type == Commands.C_RETURN:
            self.arg_1 = None
        else:
            self.arg_1 = self.current_command.split(" ")[1]
        # return self.arg_1

    def _get_arg_2(self):
        if self.command_type in [Commands.C_PUSH, Commands.C_POP, Commands.C_FUNCTION, Commands.C_CALL]:
            self.arg_2 = int(re.sub("\s+(.*)", "", self.current_command.split(" ")[2]))
        else:
            self.arg_2 = None

    def _read_file_line_by_line(self):
        with open(self.file_path, 'r') as file:
            for line in file:
                yield line.strip()


class CodeWriter:
    stack_base_address=256
    temp_base_address=5

    segment_mapping = {
        "local": "LCL",
        "argument": "ARG",
        "this": "THIS",
        "that": "THAT",
        "temp": "TEMP",
        "pointer": "POINTER",
        "static": "STATIC"
    }
    pointer_mapping = {
        0: "THIS",
        1: "THAT"
    }

    def __init__(self, output_path: str, output_buffer=StringIO()):
        self._output_buffer = output_buffer
        self._output_path = output_path

    def write_label(self, command: str, label_name: str):

        hack_command = self._translate_label(command, label_name)

        self._write_to_buffer(hack_command)

    def write_goto(self, command:str, label_name: str):

        hack_command = self._translate_goto(command, label_name)

        self._write_to_buffer(hack_command)

    def write_if_goto(self, command: str, label_name: str):

        hack_command = self._translate_if_goto(command, label_name)

        self._write_to_buffer(hack_command)

    def write_return(self, command:str):

        hack_command = self._translate_return(command)

        self._write_to_buffer(hack_command)

    def write_call(self, command: str, function_name: str, num_args: int):

        hack_command = self._translate_call(command, function_name, num_args)

        self._write_to_buffer(hack_command)

    def write_function(self, command: str, function_name: str, num_local_vars: int):

        hack_command = self._translate_function(command, function_name, num_local_vars)

        self._write_to_buffer(hack_command)

    def write_arithmetic(self, command: str):

        hack_command = self._translate_arithmetic(command)

        self._write_to_buffer(hack_command)

    def write_push_pop(self, command: str, command_type: str, segment: str, index: int, file_name: str):

        hack_command = None
        if command_type == Commands.C_PUSH:
            hack_command = self._translate_push(command, segment, index, file_name)
        if command_type == Commands.C_POP:
            hack_command = self._translate_pop(command, segment, index, file_name)

        self._write_to_buffer(hack_command)

    def close(self):
        with open(self._output_path, mode='w') as f:
            print(self._output_buffer.getvalue(), file=f)

    def _write_to_buffer(self, hack_command):
        print(hack_command)
        self._output_buffer.write(hack_command)

    def _translate_return(self, command):
        frame = "R13"
        ret = "R14"

        return textwrap.dedent(f"""
            // {command}
            @LCL            // FRAME=LCL
            D=M
            @{frame}
            M=D
            @{frame}        // RET = *(FRAME-5)
            D=M
            @5
            D=D-A
            A=D
            D=M
            @{ret}
            M=D
            @SP             // *ARG = pop(), pop to D
            M=M-1
            A=M
            D=M
            @ARG
            A=M
            M=D
            @ARG            // SP = ARG + 1
            D=M
            @SP
            M=D+1
            @{frame}        // THAT = *(FRAME-1)
            D=M
            @1              // offest
            D=D-A
            A=D
            D=M
            @THAT
            M=D
            @{frame}        // THIS = *(FRAME-2)
            D=M
            @2              // offest
            D=D-A
            A=D
            D=M
            @THIS
            M=D
            @{frame}        // ARG = *(FRAME-3)
            D=M
            @3              // offest
            D=D-A
            A=D
            D=M
            @ARG
            M=D
            @{frame}        // LCL = *(FRAME-4)
            D=M
            @4              // offest
            D=D-A
            A=D
            D=M
            @LCL
            M=D
            @{ret}          // goto RET
            A=M
            0;JMP
        """)

    def _translate_call(self, command: str, function_name:str , num_args: int):
        return_address = str(uuid.uuid4())

        return textwrap.dedent(f"""
            // {command}
            @{return_address}        // push return_address
            D=A
            @SP
            A=M
            M=D
            @SP         // SP++
            M=M+1
            @LCL        // push LCL
            D=M
            @SP
            A=M
            M=D
            @SP         // SP++
            M=M+1
            @ARG        // push ARG
            D=M
            @SP
            A=M
            M=D
            @SP         // SP++
            M=M+1
            @THIS       // push THIS
            D=M
            @SP
            A=M
            M=D
            @SP         // SP++
            M=M+1
            @THAT       // push THAT
            D=M
            @SP
            A=M
            M=D
            @SP         // SP++
            M=M+1
            @SP         // ARG = SP-num_args-5
            D=M
            @{num_args + 5}
            D=D-A
            @ARG
            M=D
            @SP         // LCL = SP
            D=M
            @LCL
            M=D
            @{function_name}    // goto function start
            0;JMP
            ({return_address})
        """)


    def _translate_function(self, command: str, function_name: str, num_local_vars: int):
        local_vars = """
            D=0
            @SP
            A=M
            M=D
            @SP
            M=M+1
        """ * num_local_vars

        return textwrap.dedent(f"""
            // {command}
            ({function_name})
            {local_vars}
        """)

    def _translate_goto(self, command, label_name):
        return textwrap.dedent(f"""
            // {command}
            @{label_name}
            0;JEQ
        """)

    def _translate_if_goto(self, command, label_name):
        # SP needs to be decremented after the comparison
        return textwrap.dedent(f"""
            // {command}
            @SP
            M=M-1
            A=M
            D=M
            @{label_name}
            D;JGT
        """)

    def _translate_label(self, command, label_name):
        return textwrap.dedent(f"""
            // {command}
            ({label_name})
        """)

    def _translate_pop(self, command, segment, index, file_name):
        hack_command = None
        index_ = f"{file_name}.{index}" if segment == "static" else index

        if segment in ["local", "this", "that", "argument", "static"]:
            hack_command = textwrap.dedent(f"""
            // {command}
            @{index_}
            D=A
            @{self.segment_mapping[segment]}
            D=D+M
            @SP
            A=M
            M=D
            @SP
            M=M-1
            A=M
            D=M
            A=A+1
            A=M
            M=D
            """)

        if segment in ["temp"]:
            hack_command = textwrap.dedent(f"""
            // {command}
            @{index_}
            D=A
            @{self.temp_base_address}
            D=D+A
            @SP
            A=M
            M=D
            @SP
            M=M-1
            A=M
            D=M
            A=A+1
            A=M
            M=D
            """)

        if segment in ["pointer"]:
            # decrement stack pointer
            # select memory that is pointed to by SP
            # put that value in this or that
            hack_command = textwrap.dedent(f"""
            // {command}
            @SP
            M=M-1
            A=M
            D=M
            @{self.pointer_mapping[index_]}
            M=D
            """)

        return hack_command

    def _translate_arithmetic(self, command: str):
        hack_command = None
        label_suffix = str(uuid.uuid4())

        if command.startswith("add"):
            hack_command = textwrap.dedent(f"""
            // {command}
            @SP
            M=M-1
            @SP
            A=M
            D=M
            @SP
            M=M-1
            @SP
            A=M
            M=M+D
            @SP
            M=M+1
            """)
        if command.startswith("sub"):
            hack_command = textwrap.dedent(f"""
            // {command}
            @SP
            M=M-1
            @SP
            A=M
            D=M
            @SP
            M=M-1
            @SP
            A=M
            M=M-D
            @SP
            M=M+1
            """)
        if command.startswith("neg"):
            hack_command = textwrap.dedent(f"""
            // {command}
            @SP
            M=M-1
            @SP
            A=M
            M=-M
            @SP
            M=M+1
            """)
        if command.startswith("not"):
            hack_command = textwrap.dedent(f"""
            // {command}
            @SP
            M=M-1
            @SP
            A=M
            M=!M
            @SP
            M=M+1
            """)
        if command.startswith("eq"):
            # wrong!! this needs revision
            hack_command = textwrap.dedent(f"""
            // {command}
            @SP
            M=M-1
            A=M
            D=M
            A=A-1
            D=D-M // y - x (diff)
            M=-1 // truth value
            @end_{label_suffix}
            D;JEQ // jump if diff = 0
            @SP
            A=M
            A=A-1
            M=M+1 // false value
            (end_{label_suffix})
            """)
        if command.startswith("lt"):
            hack_command = textwrap.dedent(f"""
            // {command}
            @SP
            M=M-1
            A=M
            D=M
            A=A-1
            D=D-M // y - x (diff)
            M=-1 // truth value
            @end_{label_suffix}
            D;JGT // jump if diff > 0
            @SP
            A=M
            A=A-1
            M=M+1 // false value
            (end_{label_suffix})
            """)
        if command.startswith("gt"):
            hack_command = textwrap.dedent(f"""
            // {command}
            @SP
            M=M-1
            A=M
            D=M
            A=A-1
            D=D-M // y - x (diff)
            M=-1 // truth value
            @end_{label_suffix}
            D;JLT // jump if diff < 0
            @SP
            A=M
            A=A-1
            M=M+1 // false value
            (end_{label_suffix})
            """)
        if command.startswith("and"):
            hack_command = textwrap.dedent(f"""
            // {command}
            @SP
            M=M-1
            @SP
            A=M
            D=M
            @SP
            M=M-1
            @SP
            A=M
            M=D&M
            @SP
            M=M+1
            """)
        if command.startswith("or"):
            hack_command = textwrap.dedent(f"""
            // {command}
            @SP
            M=M-1
            @SP
            A=M
            D=M
            @SP
            M=M-1
            @SP
            A=M
            M=D|M
            @SP
            M=M+1
            """)

        return hack_command

    def _translate_push(self, command: str, segment:str, index: int, file_name: str):
        index_ = f"{file_name}.{index}" if segment == "static" else index
        hack_command = None

        if segment == "constant":
            hack_command = textwrap.dedent(f"""
            // {command}
            @{index_}
            D=A
            @SP
            A=M
            M=D
            @SP
            M=M+1
            """)
        elif segment in ["local", "this", "that", "argument", "static"]:
            hack_command = textwrap.dedent(f"""
            //// {command}
            @{index_}
            D=A
            @{self.segment_mapping[segment]}
            D=M+D
            A=D
            D=M
            @SP
            A=M
            M=D
            @SP
            M=M+1
            """)
        elif segment == "temp":
            hack_command = textwrap.dedent(f"""
            //// {command}
            @{index_}
            D=A
            @{self.temp_base_address}
            D=D+A
            A=D
            D=M
            @SP
            A=M
            M=D
            @SP
            M=M+1
            """)
        elif segment == "pointer":
            hack_command = textwrap.dedent(f"""
            //// {command}
            @{self.pointer_mapping[index]}
            D=M
            @SP
            A=M
            M=D
            @SP
            M=M+1
            """)
        return hack_command

    def _write_output_buffer(self):
        pass

# the main is essentially the VM translator
# could be made it's own class to make cleaner
def main():

    input_path = sys.argv[1]
    output_path = input_path.replace(".vm", ".asm")

    parser = Parser(input_path)

    code_writer = CodeWriter(output_path)

    while parser.has_more_commands():
        parser.advance()
        if parser.command_type in [Commands.C_PUSH, Commands.C_POP]:
            code_writer.write_push_pop(parser.current_command, parser.command_type, parser.arg_1, parser.arg_2, parser.file_name)
        if parser.command_type == Commands.C_ARITHMETIC:
            code_writer.write_arithmetic(parser.current_command)
        if parser.command_type == Commands.C_LABEL:
            code_writer.write_label(parser.current_command, parser.arg_1)
        if parser.command_type == Commands.C_GOTO:
            code_writer.write_goto(parser.current_command, parser.arg_1)
        if parser.command_type == Commands.C_IF_GOTO:
            code_writer.write_if_goto(parser.current_command, parser.arg_1)
        if parser.command_type == Commands.C_FUNCTION:
            code_writer.write_function(parser.current_command, parser.arg_1, parser.arg_2)
        if parser.command_type == Commands.C_CALL:
            code_writer.write_call(parser.current_command, parser.arg_1, parser.arg_2)
        if parser.command_type == Commands.C_RETURN:
            code_writer.write_return(parser.current_command)

    code_writer.close()

if __name__ == "__main__":

    main()
