# 1. Stopped using Python closures and explicitly passed environments in function evaluation.
# 2. Allowed function applications on expressions instead of just names.

from dataclasses import dataclass
from typing import Union, Dict, Any
from lark import Tree
import sys

Literal = Union[int, bool, str]

@dataclass
class Lit:
    value: Literal

@dataclass
class Add:
    left: 'Expr'
    right: 'Expr'

@dataclass
class Sub:
    left: 'Expr'
    right: 'Expr'

@dataclass
class Mul:
    left: 'Expr'
    right: 'Expr'

@dataclass
class Div:
    left: 'Expr'
    right: 'Expr'

@dataclass
class Neg:
    expr: 'Expr'

@dataclass
class And:
    left: 'Expr'
    right: 'Expr'

@dataclass
class Or:
    left: 'Expr'
    right: 'Expr'

@dataclass
class Not:
    expr: 'Expr'

@dataclass
class Let:
    name: str
    value_expr: 'Expr'
    body: 'Expr'

@dataclass
class Name:
    name: str

@dataclass
class Eq:
    left: 'Expr'
    right: 'Expr'

@dataclass
class Lt:
    left: 'Expr'
    right: 'Expr'

@dataclass
class If:
    cond: 'Expr'
    then: 'Expr'
    else_: 'Expr'

@dataclass
class Concat:
    left: 'Expr'
    right: 'Expr'

@dataclass
class Replace:
    string: 'Expr'
    target: 'Expr'
    replacement: 'Expr'

@dataclass
class Letfun:
    name: str
    param: str
    body: 'Expr'
    in_expr: 'Expr'

@dataclass
class FunDef:
    param: str
    body: 'Expr'
    env: Dict[str, Any]

@dataclass
class App:
    fun_expr: 'Expr'
    arg_expr: 'Expr'

@dataclass
class Assign:
    name: str
    value_expr: 'Expr'

@dataclass
class Seq:
    first: 'Expr'
    second: 'Expr'

@dataclass
class ReverseStr:
    string_expr: 'Expr'

@dataclass
class LengthStr:
    string_expr: 'Expr'

@dataclass
class Show:
    expr: 'Expr'

@dataclass
class Read:
    pass

Expr = Union[Lit, Add, Sub, Mul, Div, Neg, And, Or, Not, Let, Name, Eq, Lt, If, Concat, Replace, Letfun, App, Assign, Seq, Show, Read]
Env = Dict[str, Any]

def eval(expr: Expr, env: Env = None, store: Dict[str, Any] = None) -> Any:
    if env is None:
        env = {}
    if store is None:
        store = {}

    if isinstance(expr, Lit):
        return expr.value

    elif isinstance(expr, Name):
        if expr.name in env:
            return env[expr.name]
        raise NameError(f"Undefined variable: {expr.name}")

    elif isinstance(expr, Let):
        new_env = env.copy()
        new_env[expr.name] = eval(expr.value_expr, new_env)
        return eval(expr.body, new_env)

    elif isinstance(expr, Letfun):
        env[expr.name] = FunDef(param=expr.param, body=expr.body, env=env.copy())
        return eval(expr.in_expr, env)

    elif isinstance(expr, App):
        func = eval(expr.fun_expr, env)
        if not isinstance(func, FunDef):
            raise TypeError(f"'{func}' is not a function")
        arg = eval(expr.arg_expr, env)
        new_env = func.env.copy()
        new_env[func.param] = arg
        return eval(func.body, new_env)

    elif isinstance(expr, Assign):
        if expr.name not in env:
            raise NameError(f"Variable '{expr.name}' is not defined")
        env[expr.name] = eval(expr.value_expr, env)
        return env[expr.name]

    elif isinstance(expr, Seq):
        eval(expr.first, env)
        return eval(expr.second, env)

    elif isinstance(expr, Show):
        result = eval(expr.expr, env)
        print(result)
        return result

    elif isinstance(expr, Read):
        user_input = input().strip()
        try:
            return int(user_input)
        except ValueError:
            raise ValueError("Invalid input, expected an integer")

    elif isinstance(expr, ReverseStr):
        str_val = eval(expr.string_expr, env)
        if isinstance(str_val, str):
            return str_val[::-1]
        raise TypeError("Reverse requires a string operand")

    elif isinstance(expr, LengthStr):
        str_val = eval(expr.string_expr, env)
        if isinstance(str_val, str):
            return len(str_val)
        raise TypeError("Length requires a string operand")

    elif isinstance(expr, Concat):
        left_val, right_val = eval(expr.left, env), eval(expr.right, env)
        if isinstance(left_val, str) and isinstance(right_val, str):
            return left_val + right_val
        raise TypeError("Concatenation requires string operands")

    elif isinstance(expr, Replace):
        str_val = eval(expr.string, env)
        target_val = eval(expr.target, env)
        replacement_val = eval(expr.replacement, env)
        if isinstance(str_val, str) and isinstance(target_val, str) and isinstance(replacement_val, str):
            return str_val.replace(target_val, replacement_val)
        raise TypeError("Replace requires string operands")

    elif isinstance(expr, Div):
        left_val = eval(expr.left, env)
        right_val = eval(expr.right, env)
        if right_val == 0:
            raise ZeroDivisionError("Division by zero")
        return left_val // right_val

    elif isinstance(expr, Eq):
        return eval(expr.left, env) == eval(expr.right, env)

    elif isinstance(expr, Lt):
        return eval(expr.left, env) < eval(expr.right, env)

    elif isinstance(expr, If):
        cond_val = eval(expr.cond, env)
        if not isinstance(cond_val, bool):
            raise TypeError("Condition must be boolean")
        return eval(expr.then, env) if cond_val else eval(expr.else_, env)

    else:
        raise TypeError(f"Unknown expression type: {expr}")

if __name__ == "__main__":
    print(eval(Concat(Lit("hello"), Lit(" world"))))
    print(eval(Replace(Lit("hello world"), Lit("world"), Lit("Python"))))

    fun_expr = Letfun(
        name="addOne",
        param="x",
        body=Add(Name("x"), Lit(1)),
        in_expr=App(Name("addOne"), Lit(41))
    )
    print(eval(fun_expr))  # Expected: 42