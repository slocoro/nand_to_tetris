import compilation_engine as ce
import jack_tokenizer as jt
import symbol_table as st
import vm_writer as vm

import sys
from pathlib import Path


def main():

    input_path = Path(sys.argv[1])

    if input_path.is_dir():
        files_to_process = input_path.glob("*.jack")
    else:
        files_to_process = [input_path]

    for file in files_to_process:
        jack_tokenizer = jt.JackTokenizer(file)
        symbol_table = st.SymbolTable()
        vm_writer = vm.VMWriter()
        compilation_engine = ce.CompilationEngine(
            input_path=file,
            tokenizer=jack_tokenizer,
            symbol_table=symbol_table,
            vm_writer=vm_writer,
        )
        compilation_engine.compile_class()
        compilation_engine.write_output()


if __name__ == "__main__":
    main()
