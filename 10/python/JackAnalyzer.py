import compilation_engine as ce
import jack_tokenizer as jt
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
        compilation_engine = ce.CompilationEngine(
            input_path=file,
            tokenizer=jack_tokenizer,
            starting_token="class",
            output_suffix="",
        )
        compilation_engine.compile_class()
        compilation_engine.write_output()


if __name__ == "__main__":
    main()
