from typing import NoReturn

from environment import Environment
from lexer import Token, Type


class Runner:
    def __init__(self, filename: str, tokens: list[Token]) -> None:
        self.filename = filename
        self.tokens = tokens
        self.env: Environment
        self.lineno = 1
        self.col = 1

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
                    Type.EQ
                    | Type.NEQ
                    | Type.GT
                    | Type.GTE
                    | Type.LT
                    | Type.LTE
                    | Type.OR
                    | Type.AND
                ):
                    self.__conditionals(token.type)
                case (
                    Type.INT | Type.FLOAT | Type.STRING | Type.BOOL | Type.ID | Type.KEY
                ):
                    self.env.stack.append({"type": token.type, "value": token.value})
                case Type.ADD | Type.SUB | Type.MUL | Type.DIV | Type.REM:
                    self.__arithmetics(token.type)
            token = self.__curr_token()

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
        val = self.env.stack.pop()
        if val["type"] not in [Type.INT, Type.FLOAT, Type.STRING, Type.BOOL]:
            self.raise_error(f"(PUT) cant print anything but primitive types")
        print(val["value"])

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
        if second["type"] not in [Type.INT, Type.FLOAT]:
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

    def __conditionals(self, cond_type: Type):
        if cond_type == Type.NEQ:
            if len(self.env.stack) == 0:
                self.raise_error(f"({cond_type}) stack is empty")

            value = self.env.stack.pop()

            if value["type"] != Type.BOOL:
                self.raise_error(
                    f"({cond_type}) cant use logical NOT ('!') on anything but boolean values (current value's type is '{value['type']}')"
                )
            value["value"] = not value["value"]
            self.env.stack.append(value)

        else:
            if len(self.env.stack) <= 1:
                self.raise_error(
                    f"({cond_type}) stack is empty or has only 1 value at this point"
                )

            second = self.env.stack.pop()
            if second["type"] not in [Type.STRING, Type.INT, Type.FLOAT, Type.BOOL]:
                self.raise_error(
                    f"({cond_type}) second value cannot be used for comparison, as it has type '{second['type']}'"
                )

            first = self.env.stack.pop()
            if first["type"] not in [Type.STRING, Type.INT, Type.FLOAT, Type.BOOL]:
                self.raise_error(
                    f"({cond_type}) first value cannot be used for comparison, as it has type '{first['type']}'"
                )

            # Numeric comparisons require both types to be INT or FLOAT
            if cond_type in [Type.GT, Type.GTE, Type.LT, Type.LTE]:
                if first["type"] not in [Type.INT, Type.FLOAT] or second[
                    "type"
                ] not in [Type.INT, Type.FLOAT]:
                    self.raise_error(
                        f"({cond_type}) comparison requires numeric types (INT or FLOAT), got '{first['type']}' and '{second['type']}'"
                    )

            first_val = first["value"]
            second_val = second["value"]

            result = None
            if cond_type == Type.EQ:
                result = first_val == second_val
            elif cond_type == Type.GT:
                result = first_val > second_val
            elif cond_type == Type.GTE:
                result = first_val >= second_val
            elif cond_type == Type.LT:
                result = first_val < second_val
            elif cond_type == Type.LTE:
                result = first_val <= second_val
            elif cond_type == Type.OR:
                if first["type"] != Type.BOOL or second["type"] != Type.BOOL:
                    self.raise_error(
                        f"({cond_type}) OR operation requires boolean operands"
                    )
                result = first_val or second_val
            elif cond_type == Type.AND:
                if first["type"] != Type.BOOL or second["type"] != Type.BOOL:
                    self.raise_error(
                        f"({cond_type}) AND operation requires boolean operands"
                    )
                result = first_val and second_val
            else:
                self.raise_error(f"Unsupported conditional operation: {cond_type}")

            self.env.stack.append({"type": Type.BOOL, "value": result})
