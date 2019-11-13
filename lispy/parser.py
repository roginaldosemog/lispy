from lark import Lark, InlineTransformer
from pathlib import Path

from .runtime import Symbol


class LispTransformer(InlineTransformer):
    def binop(self, op, var1, var2):
        return [(Symbol(op), var1, var2)]

    def list(self, *args):
        return list(args)

    def quote(self, quote):
        return [Symbol.QUOTE, quote]

    def let(self, decl, expr):
        return [(Symbol('let'), decl, expr)]

    def lambda1(self, params, expr):
        return [Symbol('lambda'), (params, expr)]

    def symbol(self, symbol):
        return Symbol(symbol)

    def string(self, string):
        string = string.replace('\\t', '\t')
        string = string.replace('\\"', '\"')
        string = string.replace('\\n', '\n')[1:-1]
        return string

    def number(self, number):
        number = float(number)
        return number

    def bool(self, bool):
        if bool == '#t':
            return True
        else:
            return False


def parse(src: str):
    """
    Compila string de entrada e retorna a S-expression equivalente.
    """
    return parser.parse(src)


def _make_grammar():
    """
    Retorna uma gramática do Lark inicializada.
    """

    path = Path(__file__).parent / 'grammar.lark'
    with open(path) as fd:
        grammar = Lark(fd, parser='lalr', transformer=LispTransformer())
    return grammar


parser = _make_grammar()
