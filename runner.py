from typing import Any, NoReturn

from lexer import Token, Type


class Runner:
    def __init__(self, filename: str, tokens: list[Token]) -> None:
        self.filename = filename
        self.tokens = tokens
        self.stack = []
        self.variables: dict[str, Any] = {}
        self.lineno = 1
        self.col = 1

    def __curr_token(self) -> Token:
        token = self.tokens.pop(0)
        self.lineno = token.lineno
        self.col = token.col
        return token

    def raise_error(self, message: str) -> NoReturn:
        raise SyntaxError(f"{self.filename}:{self.lineno}:{self.col}: {message}")

    def __dup(self):
        if len(self.stack) == 0:
            self.raise_error(f"(DUP) stack is empty at this point")
        self.stack.append(self.stack[-1])

    def __swp(self):
        if len(self.stack) <= 1:
            self.raise_error(
                f"(SWP) stack is empty or has only 1 element at this point"
            )
        self.stack[-1], self.stack[-2] = self.stack[-2], self.stack[-1]

    def __put(self):
        if len(self.stack) == 0:
            self.raise_error(f"(PUT) stack is empty at this point")
        print(self.stack.pop())

    def __set(self):
        if len(self.stack) <= 1:
            self.raise_error(
                f"(SET) stack is empty or dont have enought arguments for this instruction"
            )

        id = self.stack.pop()
        if id["type"] != Type.ID:
            self.raise_error(f"(SET) can't assign value to '{id['value']}' of type '{id["type"]}'")

        value = self.stack.pop()

        self.variables[id["value"]] = value

    def __arithmetics(self, op_type: Type):
        if len(self.stack) <= 1:
            self.raise_error(
                f"({op_type}) stack is empty or has only 1 element at this point"
            )

        second = self.stack.pop()
        if second[type] not in [Type.INT, Type.FLOAT]:
            self.raise_error(
                f"({op_type}) Value '{second['value']}' is not numeric (int or float)"
            )

        first = self.stack.pop()
        if first["type"] not in [Type.INT, Type.FLOAT]:
            self.raise_error(
                f"({op_type}) Value '{first['value']}' is not numeric (int or float)"
            )

        result_type = Type.FLOAT if first["type"] == Type.FLOAT else second["type"]

        match op_type:
            case Type.ADD:
                self.stack.append(
                    {"type": result_type, "value": first["value"] + second["value"]}
                )
            case Type.SUB:
                self.stack.append(
                    {"type": result_type, "value": first["value"] - second["value"]}
                )
            case Type.MUL:
                self.stack.append(
                    {"type": result_type, "value": first["value"] * second["value"]}
                )
            case Type.DIV:
                self.stack.append(
                    {"type": result_type, "value": first["value"] / second["value"]}
                )
            case Type.REM:
                self.stack.append(
                    {"type": result_type, "value": first["value"] % second["value"]}
                )

    def run(self):
        token = self.__curr_token()
        while True:
            match token.type:
                case Type.EOF:
                    return
                case Type.DUP:
                    self.__dup()
                case Type.SWP:
                    self.__swp()
                case Type.PUT:
                    self.__put()
                case Type.SET:
                    print("variables before:", self.variables)
                    self.__set()
                    print("variables after:", self.variables)
                case (
                    Type.INT | Type.FLOAT | Type.STRING | Type.BOOL | Type.ID | Type.KEY
                ):
                    self.stack.append({"type": token.type, "value": token.value})
                case Type.ADD | Type.SUB | Type.MUL | Type.DIV | Type.REM:
                    self.__arithmetics(token.type)
            token = self.__curr_token()
