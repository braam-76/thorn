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
    GET = auto()
    COMMENT = auto()

    EQ = auto()
    NEQ = auto()
    GT = auto()
    GTE = auto()
    LT = auto()
    LTE = auto()
    OR = auto()
    AND = auto()

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
        if self.value in [
            Type.STRING,
            Type.FLOAT,
            Type.INT,
            Type.BOOL,
        ]:
            return self.name
        return "BUILTIN"


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
            # hardenned functions
            case "dup":
                return Token(Type.DUP, None, lineno, col)
            case "swp":
                return Token(Type.SWP, None, lineno, col)
            case "put":
                return Token(Type.PUT, None, lineno, col)
            case "set":
                return Token(Type.SET, None, lineno, col)
            case "get":
                return Token(Type.GET, None, lineno, col)

            # conditionals
            case "=":
                return Token(Type.EQ, None, lineno, col)
            case "!":
                return Token(Type.NEQ, None, lineno, col)
            case ">":
                return Token(Type.GT, None, lineno, col)
            case ">=":
                return Token(Type.GTE, None, lineno, col)
            case "<":
                return Token(Type.LT, None, lineno, col)
            case "<=":
                return Token(Type.LTE, None, lineno, col)
            case "|":
                return Token(Type.OR, None, lineno, col)
            case "&":
                return Token(Type.AND, None, lineno, col)

            # arithmetics
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

    def __parse_nested(self, line: str, open: str, close: str) -> tuple[str, int]:
        depth = 0
        for i, ch in enumerate(line.strip()):
            if ch == open:
                depth += 1
            elif ch == close:
                depth -= 1
                if depth == 0:
                    return (line[1:i], i + 1)
        return ("", -1)

    def lex(self) -> list[Token]:
        for line in self.src:
            self.col = 1
            while line:
                line = line.lstrip()
                self.col += len(line) - len(line.lstrip())
                if not line:
                    break

                print(line)

                if line.startswith("["):
                    string_content, length = self.__parse_nested(line, "[", "]")
                    if length == -1:
                        self.raise_error(f"Unmatched [")
                    self.tokens.append(
                        Token(Type.STRING, string_content, self.lineno, self.col)
                    )
                    line = line[length:]
                    self.col += length
                    continue
                if line.startswith("("):
                    comment, length = self.__parse_nested(line, "(", ")")
                    if length == -1:
                        self.raise_error(f"Unmatched (")
                    self.tokens.append(
                        Token(Type.COMMENT, comment, self.lineno, self.col)
                    )
                    line = line[length:]
                    self.col += length
                    continue
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
