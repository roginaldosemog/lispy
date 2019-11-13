import math
import operator as op
from collections import ChainMap
from types import MappingProxyType

from .symbol import Symbol


def eval(x, env=None):
    """
    Avalia expressão no ambiente de execução dado.
    """
    
    # Cria ambiente padrão, caso o usuário não passe o argumento opcional "env"
    if env is None:
        env = ChainMap({}, global_env)
    
    # Avalia tipos atômicos
    if isinstance(x, Symbol):
        return env[x]
    elif isinstance(x, (int, float, bool, str)):
        return x

    # Avalia formas especiais e listas
    head, *args = x
    
    # Comando (if <test> <then> <other>)
    # Ex: (if (even? x) (quotient x 2) x)
    if head == Symbol.IF:
        (condition, then, alternative) = args
        expression = (then if eval(condition, env) else alternative)
        return eval(expression, env)

    # Comando (define <symbol> <expression>)
    # Ex: (define x (+ 40 2))
    elif head == Symbol.DEFINE:
        variable, value_or_expression = args
        new_thing = eval(value_or_expression, env)
        env[Symbol(variable)] = new_thing
        return None

    # Comando (quote <expression>)
    # (quote (1 2 3))
    elif head == Symbol.QUOTE:
        result = []
        arguments = args[0]
        if isinstance(arguments,list) :
            for x in args[0]:
                if isinstance(x, (int, float, bool, str)):
                    result.append(eval(x,env))
                else:
                    result.append(Symbol(x))
        else:
            return arguments
        return result

    # Comando (let <expression> <expression>)
    # (let ((x 1) (y 2)) (+ x y))
    elif head == Symbol.LET:
        sub_env = ChainMap({}, global_env)# pegar as funções sem ter que copiar todo o env
        declarations,expr = args
        for declaration in declarations:
            eval([Symbol.DEFINE, declaration[0], declaration[1]], sub_env)

        result = eval(expr, sub_env)
        return result

    # Comando (lambda <vars> <body>)
    # (lambda (x) (+ x 1))
    elif head == Symbol.LAMBDA:
        if len(args) == 1:
            print(args[0])
            parameters,expr = args[0]
        else:
            parameters,expr = args
        result = None
        print("parameters: ", parameters)
        if any(isinstance(parameter, (float, int, bool)) for parameter in parameters):
            raise TypeError
        local_ctx = ChainMap({}, global_env)
        def new_fun(*arguments):
            arguments = list(arguments)
            for parameter_number in range(len(parameters)):
                if len(arguments) > 0:
                    local_ctx[parameters[parameter_number]] = arguments[parameter_number]
                else :
                    local_ctx[parameters[parameter_number]] = arguments
            return eval(expr, local_ctx)
        return new_fun

    # Lista/chamada de funções
    # (sqrt 4)
    elif head == Symbol.ADD:
        x, y = args
        return eval(x, env) + eval(y, env)

    elif head == Symbol.SUB:
        x, y = args
        return eval(x, env) - eval(y, env)
    else:
        env_function = eval(head, env)
        arguments = (eval(arg,env) for arg in x[1:])
        return env_function(*arguments)


#
# Cria ambiente de execução.
#
def env(*args, **kwargs):
    """
    Retorna um ambiente de execução que pode ser aproveitado pela função
    eval().

    Aceita um dicionário como argumento posicional opcional. Argumentos nomeados
    são salvos como atribuições de variáveis.

    Ambiente padrão
    >>> env()
    {...}
        
    Acrescenta algumas variáveis explicitamente
    >>> env(x=1, y=2)
    {x: 1, y: 2, ...}
        
    Passa um dicionário com variáveis adicionais
    >>> d = {Symbol('x'): 1, Symbol('y'): 2}
    >>> env(d)
    {x: 1, y: 2, ...}
    """

    kwargs = {Symbol(k): v for k, v in kwargs.items()}
    if len(args) > 1:
        raise TypeError('accepts zero or one positional arguments')
    elif len(args):
        if any(not isinstance(x, Symbol) for x in args[0]):
            raise ValueError('keys in a environment must be Symbols')
        args[0].update(kwargs)
        return ChainMap(args[0], global_env)
    return ChainMap(kwargs, global_env)


def _make_global_env():
    """
    Retorna dicionário fechado para escrita relacionando o nome das variáveis aos
    respectivos valores.
    """

    dic = {
        **vars(math), # sin, cos, sqrt, pi, ...
        '+':op.add, '-':op.sub, '*':op.mul, '/':op.truediv, 
        '>':op.gt, '<':op.lt, '>=':op.ge, '<=':op.le, '=':op.eq, 
        'abs':     abs,
        'append':  op.add,  
        'apply':   lambda proc, args: proc(*args),
        'begin':   lambda *x: x[-1],
        'car':     lambda x: head,
        'cdr':     lambda x: x[1:], 
        'cons':    lambda x,y: [x] + y,
        'eq?':     op.is_, 
        'expt':    pow,
        'equal?':  op.eq,
        'even?':   lambda x: x % 2 == 0,
        'length':  len, 
        'list':    lambda *x: list(x), 
        'list?':   lambda x: isinstance(x, list), 
        'map':     map,
        'max':     max,
        'min':     min,
        'not':     op.not_,
        'null?':   lambda x: x == [], 
        'number?': lambda x: isinstance(x, (float, int)),  
		'odd?':   lambda x: x % 2 == 1,
        'print':   print,
        'procedure?': callable,
        'quotient': op.floordiv,
        'round':   round,
        'symbol?': lambda x: isinstance(x, Symbol),
    }
    return MappingProxyType({Symbol(k): v for k, v in dic.items()})

global_env = _make_global_env() 

