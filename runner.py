from typing import NoReturn

from environment import Environment
from lexer import Token, Type


class Runner:
    def __init__(self, filename: str, tokens: list[Token]) -> None:
        self.filename = filename
        self.tokens = tokens
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
        if len(self.env.stack) == 0:
            self.raise_error(f"(DUP) stack is empty at this point")
        self.env.stack.append(self.env.stack[-1])

    def __swp(self):
        if len(self.env.stack) <= 1:
            self.raise_error(
                f"(SWP) stack is empty or has only 1 element at this point"
            )
        self.env.stack[-1], self.env.stack[-2] = self.env.stack[-2], self.env.stack[-1]

    def __put(self):
        if len(self.env.stack) == 0:
            self.raise_error(f"(PUT) stack is empty at this point")
        print(self.env.stack.pop()["value"])

    def __get(self):
        if len(self.env.stack) == 0:
            self.raise_error(f"(GET) stack is empty at this point")

        id = self.env.stack.pop()
        if id["type"] != Type.ID:
            self.raise_error(
                f"(GET) word '{id['value']}' is not ID, but '{id['type']}'"
            )

        value = self.env.variables.get(id["value"])
        if value is None:
            self.raise_error(f"(GET) variable '{id['value']}' is not set")

        self.env.stack.append(value)

    def __set(self):
        if len(self.env.stack) <= 1:
            self.raise_error(
                f"(SET) stack is empty or dont have enought arguments for this instruction"
            )

        id = self.env.stack.pop()
        if id["type"] != Type.ID:
            self.raise_error(
                f"(SET) can't assign value to '{id['value']}' of type '{id['type']}'"
            )

        value = self.env.stack.pop()

        self.env.variables[id["value"]] = value

    def __arithmetics(self, op_type: Type):
        if len(self.env.stack) <= 1:
            self.raise_error(
                f"({op_type}) stack is empty or has only 1 element at this point"
            )

        second = self.env.stack.pop()
        if second[type] not in [Type.INT, Type.FLOAT]:
            self.raise_error(
                f"({op_type}) Value '{second['value']}' is not numeric (int or float)"
            )

        first = self.env.stack.pop()
        if first["type"] not in [Type.INT, Type.FLOAT]:
            self.raise_error(
                f"({op_type}) Value '{first['value']}' is not numeric (int or float)"
            )

        result_type = Type.FLOAT if first["type"] == Type.FLOAT else second["type"]

        match op_type:
            case Type.ADD:
                self.env.stack.append(
                    {"type": result_type, "value": first["value"] + second["value"]}
                )
            case Type.SUB:
                self.env.stack.append(
                    {"type": result_type, "value": first["value"] - second["value"]}
                )
            case Type.MUL:
                self.env.stack.append(
                    {"type": result_type, "value": first["value"] * second["value"]}
                )
            case Type.DIV:
                self.env.stack.append(
                    {"type": result_type, "value": first["value"] / second["value"]}
                )
            case Type.REM:
                self.env.stack.append(
                    {"type": result_type, "value": first["value"] % second["value"]}
                )

    def run(self, env: Environment):
        self.env = env
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
                    self.__set()
                case Type.GET:
                    self.__get()
                case (
                    Type.INT | Type.FLOAT | Type.STRING | Type.BOOL | Type.ID | Type.KEY
                ):
                    self.env.stack.append({"type": token.type, "value": token.value})
                case Type.ADD | Type.SUB | Type.MUL | Type.DIV | Type.REM:
                    self.__arithmetics(token.type)
            token = self.__curr_token()
