import sys

import lexer
import runner
from environment import Environment


def repl():
    print("Thorn Programming Language (0.0.1)")
    print("To exit, use '!exit'. To get help about REPL, use '!help'")
    prompt = "thorn > "
    src: list[str] = []
    env = Environment()
    while True:
        expr = input(prompt)
        if expr == "!exit":
            print("Exiting...")
            break
        elif expr == "!help":
            repl_help()
        elif expr == "!flush-stack":
            env.stack = []
        elif expr.endswith("\\"):
            prompt = ">> "
            src.append(expr[:-1])
            continue
        else:
            prompt = "thorn > "
            src.append(expr)
            try:
                tokens = lexer.Lexer("<thorn-repl>", src).lex()
                r = runner.Runner("<thorn-repl>", tokens)
                r.run(env)
            except Exception as e:
                print(e)

        src = []


def repl_help():
    print("REPL specific commands:")
    print("    !exit:\t\t Exit the REPL")
    print("    !help:\t\t Print this help message")
    print("    !flush-stack:\t Flushes/Cleans the stack")


def main():
    if len(sys.argv) <= 1:
        repl()

    else:
        with open(sys.argv[1], "r") as f:
            l = lexer.Lexer(sys.argv[1], f.readlines())
            print(l.lex())


if __name__ == "__main__":
    main()
