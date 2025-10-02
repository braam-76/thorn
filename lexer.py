import re
from enum import IntEnum, auto
from typing import Any, NoReturn


class Type(IntEnum):
    EOF = 0
    DUP = auto()
    SWP = auto()
    POP = auto()
    PUT = auto()
    SET = auto()
    COMMENT = auto()

    ADD = auto()
    SUB = auto()
    MUL = auto()
    DIV = auto()
    REM = auto()

    INT = auto()
    FLOAT = auto()
    STRING = auto()
    BOOL = auto()
    KEY = auto()
    ID = auto()

    def __str__(self) -> str:
        return self.name


class Token:
    def __init__(self, type: Type, value: Any, lineno: int, col: int) -> None:
        self.type = type
        self.value = value
        self.lineno = lineno
        self.col = col

    def __repr__(self) -> str:
        if self.value is not None:
            return f"{self.lineno}:{self.col}: {self.type}({self.value})"
        else:
            return f"{self.lineno}:{self.col}: {self.type}"


class Lexer:
    def __init__(self, filename: str, src: list[str]) -> None:
        self.filename = filename
        self.src = src
        self.tokens: list[Token] = []

        self.lineno = 1
        self.col = 1

    def raise_error(self, message: str) -> NoReturn:
        raise SyntaxError(f"{self.filename}:{self.lineno}:{self.col}: {message}")

    def __single_word(self, word: str, lineno: int, col: int) -> Token:
        match word:
            case "dup":
                return Token(Type.DUP, None, lineno, col)
            case "swp":
                return Token(Type.SWP, None, lineno, col)
            case "put":
                return Token(Type.PUT, None, lineno, col)
            case "set":
                return Token(Type.SET, None, lineno, col)
            case "+":
                return Token(Type.ADD, None, lineno, col)
            case "-":
                return Token(Type.SUB, None, lineno, col)
            case "*":
                return Token(Type.MUL, None, lineno, col)
            case "/":
                return Token(Type.DIV, None, lineno, col)
            case "%":
                return Token(Type.REM, None, lineno, col)

        if re.match(r"^[+-]?[0-9]+$", word):
            return Token(Type.INT, int(word), lineno, col)
        elif re.match(r"^[+-]?[0-9]+\.[0-9]+$", word):
            return Token(Type.FLOAT, float(word), lineno, col)
        elif re.match(r"true|false", word):
            return Token(Type.BOOL, word == "true", lineno, col)
        elif re.match(r":[A-Za-z0-9_-]+", word):
            return Token(Type.KEY, word, lineno, col)
        elif re.match(r"[A-Za-z][A-Za-z0-9_-]+", word):
            return Token(Type.ID, word, lineno, col)

        self.raise_error(f"Unknown word '{word}'")

    def lex(self) -> list[Token]:
        for line in self.src:
            self.col = 1
            while line:
                line = line.lstrip()
                self.col += len(line) - len(line.lstrip())
                if not line:
                    break

                if line.startswith("[["):
                    match = re.match(r"\[\[(.*?)\]\]", line)
                    if match:
                        string_content = match.group(1)
                        length = match.end()
                        self.tokens.append(
                            Token(Type.STRING, string_content, self.lineno, self.col)
                        )
                        line = line[length:]
                        self.col += length
                    else:
                        raise SyntaxError(
                            f"{self.filename}:{self.lineno}:{self.col}: Unmatched [["
                        )
                elif line.startswith("("):
                    match = re.match(r"\((.*?)\)", line)
                    if match:
                        string_content = match.group(1)
                        length = match.end()
                        self.tokens.append(
                            Token(Type.COMMENT, string_content, self.lineno, self.col)
                        )
                        line = line[length:]
                        self.col += length
                    else:
                        raise SyntaxError(
                            f"{self.filename}:{self.lineno}:{self.col}: Unmatched [["
                        )
                else:
                    m = re.match(r"(\S+)", line)
                    if m:
                        word = m.group(1)
                        self.tokens.append(
                            self.__single_word(word, self.lineno, self.col)
                        )
                        length = len(word)
                        line = line[length:]
                        self.col += length
                    else:
                        break
                self.col += 1  # for space
            self.col = 1
            self.lineno += 1

        self.tokens.append(Token(Type.EOF, None, self.lineno - 1, self.col))
        return self.tokens
