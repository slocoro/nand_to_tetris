# TODO:
# figure out how to do a pop operation
# figure out how to implement eq, gt, lt arithmetic (done)

from typing import Optional
from dataclasses import dataclass
from io import StringIO 
import textwrap
import uuid
import sys


@dataclass
class Commands:
    C_ARITHMETIC = "C_ARITHMETIC"
    C_PUSH = "C_PUSH"
    C_POP = "C_POP"
    C_LABEL = "C_LABEL"
    C_GOTO = "C_GOTO"
    C_IF = "C_IF"
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
            if self.current_command in ["add", "sub", "eq", "neg", "lt", "gt", "and", "or", "not"]:
                self.command_type = Commands.C_ARITHMETIC
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
            self.arg_2 = int(self.current_command.split(" ")[2])
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

        if command == "add":
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
        if command == "sub":
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
        if command == "neg":
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
        if command == "not":
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
        if command == "eq":
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
        if command == "lt":
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
        if command == "gt":
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
        if command == "and":
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
        if command == "or":
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

    # input_path = "../StackArithmetic/SimpleAdd/SimpleAdd.vm"
    # output_path = "../StackArithmetic/SimpleAdd/SimpleAdd.asm"
    # input_path = "../StackArithmetic/StackTest/StackTest.vm"
    # output_path = "../StackArithmetic/StackTest/StackTest.asm"
    # input_path = "../MemoryAccess/BasicTest/BasicTest.vm"
    # output_path = "../MemoryAccess/BasicTest/BasicTest.asm"
    # input_path = "../MemoryAccess/PointerTest/PointerTest.vm"
    # output_path = "../MemoryAccess/PointerTest/PointerTest.asm"
    # input_path = "../MemoryAccess/StaticTest/StaticTest.vm"
    # output_path = "../MemoryAccess/StaticTest/StaticTest.asm"
    # input_path = "../MemoryAccess/StaticTest/Simple.vm"
    # output_path = "../MemoryAccess/StaticTest/Simple.asm"

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

    code_writer.close()


if __name__ == "__main__":

    main()
