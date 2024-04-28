from pathlib import Path
import re

# uses regex groups (...) to extract the appropriate token
# when the regex expression matches the string
# matches any number of whitespace characters after the group
# to advance to the start of the next token

# match lazily using ? to avoid matching " of next string in code
STRING_CONSTANT_PATTERN = re.compile(r'^\s*"(.*?)"\s*')
INTEGER_CONSTANT_PATTERN = re.compile(r"^\s*([0-9]+)\s*")
KEYWORD_PATTERN = re.compile(
    r"^\s*(class|constructor|function|method|static|field"
    r"|var|int|char|boolean|void|true|false|null|this|"
    r"let|do|if|else|while|return"
    r")\s*"
)
SYMBOL_PATTERN = re.compile(r"^\s*([{}()\[\].,;+\-*/&|<>=~])\s*")
IDENTIFIER_PATTERN = re.compile(r"^\s*([a-zA-Z_][a-zA-Z0-9_]*)\s*")
EMPTY_PATTERN = re.compile(r"\s*")


class JackTokenizer:

    KEYWORD = "keyword"
    SYMBOL = "symbol"
    INTEGER_CONSTANT = "integer_constant"
    STRING_CONST = "string_constant"
    IDENTIFIER = "identifier"

    def __init__(self, file_path: str):
        self.file_path = file_path
        self._read_and_tokenize_input()

        self.current_token = None
        self.previous_token = None
        self.token_type = None

    def advance(self):
        # match keyword
        match = KEYWORD_PATTERN.match(self._content)
        if match:
            self._update_token(match)
            self.token_type = JackTokenizer.KEYWORD
            return None

        # match identifier (variable)
        match = IDENTIFIER_PATTERN.match(self._content)
        if match:
            self._update_token(match)
            self.token_type = JackTokenizer.IDENTIFIER
            return None

        # match symbol
        match = SYMBOL_PATTERN.match(self._content)
        if match:
            self._update_token(match)
            self.token_type = JackTokenizer.SYMBOL
            return None

        # match integer constant
        match = INTEGER_CONSTANT_PATTERN.match(self._content)
        if match:
            self._update_token(match)
            self.token_type = JackTokenizer.INTEGER_CONSTANT
            return None

        # match string constant
        match = STRING_CONSTANT_PATTERN.match(self._content)
        if match:
            self._update_token(match)
            self.token_type = JackTokenizer.STRING_CONST
            return None

    def has_more_tokens(self):
        if EMPTY_PATTERN.fullmatch(self._content):
            return False
        return True

    # TODO: refactor to reduce duplication
    def peek(self):
        if self.has_more_tokens():
            # match keyword
            match = KEYWORD_PATTERN.match(self._content)
            if match:
                return match.group(1), JackTokenizer.KEYWORD

            # match identifier (variable)
            match = IDENTIFIER_PATTERN.match(self._content)
            if match:
                return match.group(1), JackTokenizer.IDENTIFIER

            # match symbol
            match = SYMBOL_PATTERN.match(self._content)
            if match:
                return match.group(1), JackTokenizer.SYMBOL

            # match integer constant
            match = INTEGER_CONSTANT_PATTERN.match(self._content)
            if match:
                return match.group(1), JackTokenizer.INTEGER_CONSTANT

            # match string constant
            match = STRING_CONSTANT_PATTERN.match(self._content)
            if match:
                return match.group(1), JackTokenizer.STRING_CONST

        # should this return something more informative???
        else:
            return False

    def _update_token(self, match) -> None:
        if self.current_token:
            self.previous_token = self.current_token
        self.current_token = match.group(1)
        self._content = self._content[match.end() :]

    def _read_and_tokenize_input(self):
        self._content = Path(self.file_path).open("r").read()
        self._content = self._content.split("\n")

        self._remove_comments()

    def _remove_comments(self):
        # remove comment lines remove inline comments
        # return one long string
        self._content = " ".join(
            [
                l.split("//")[0].strip()
                for l in self._content
                if not l.strip().startswith("/") and l != ""
            ]
        )


if __name__ == "__main__":

    file_path = "../ExpressionLessSquare/Main.jack"
    jack_tokenizer = JackTokenizer(file_path)

    while jack_tokenizer.has_more_tokens():
        jack_tokenizer.advance()
        print(f"Current token: {jack_tokenizer.current_token}")
        print(f"Token type: {jack_tokenizer.token_type}")
        print("\n")
