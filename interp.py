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

    match expr:
        case Lit(value):
            return value

        case Name(name):
            if name in env:
                return env[name]
            raise NameError(f"Undefined variable: {name}")

        case Let(name, value_expr, body):
            new_env = env.copy()
            new_env[name] = eval(value_expr, new_env)
            return eval(body, new_env)

        case Add(left, right):
            return eval(left, env) + eval(right, env)

        case Sub(left, right):
            return eval(left, env) - eval(right, env)

        case Mul(left, right):
            return eval(left, env) * eval(right, env)

        case Div(left, right):
            right_val = eval(right, env)
            if right_val == 0:
                raise ZeroDivisionError("Division by zero")
            return eval(left, env) // right_val

        case Neg(expr):
            return -eval(expr, env)

        case And(left, right):
            left_val = eval(left, env)
            right_val = eval(right, env)
            if not isinstance(left_val, bool) or not isinstance(right_val, bool):
                raise TypeError("Operands of '&&' must be boolean")
            return eval(left, env) and eval(right, env)

        case Or(left, right):
            left_val = eval(left, env)
            right_val = eval(right, env)
            if not isinstance(left_val, bool) or not isinstance(right_val, bool):
                raise TypeError("Operands of '||' must be boolean")
            return eval(left, env) or eval(right, env)

        case Not(expr):
            return not eval(expr, env)

        case Eq(left, right):
            return eval(left, env) == eval(right, env)

        case Lt(left, right):
            return eval(left, env) < eval(right, env)

        case If(cond, then, else_):
            return eval(then, env) if eval(cond, env) else eval(else_, env)

        case Concat(left, right):
            left_val, right_val = eval(left, env), eval(right, env)
            if isinstance(left_val, str) and isinstance(right_val, str):
                return left_val + right_val
            raise TypeError("Concatenation requires string operands")

        case Replace(string, target, replacement):
            str_val, target_val, replacement_val = eval(string, env), eval(target, env), eval(replacement, env)
            if isinstance(str_val, str) and isinstance(target_val, str) and isinstance(replacement_val, str):
                return str_val.replace(target_val, replacement_val)
            raise TypeError("Replace requires string operands")

        case ReverseStr(string_expr):
            str_val = eval(string_expr, env)
            if isinstance(str_val, str):
                return str_val[::-1]
            raise TypeError("Reverse requires a string operand")

        case LengthStr(string_expr):
            str_val = eval(string_expr, env)
            if isinstance(str_val, str):
                return len(str_val)
            raise TypeError("Length requires a string operand")

        case Letfun(name, param, body, in_expr):
            new_env = env.copy()
            new_env[name] = FunDef(param, body, new_env)            
            return eval(in_expr, new_env)

        case App(fun_expr, arg_expr):
            func = eval(fun_expr, env)
            if not isinstance(func, FunDef):
                raise TypeError(f"'{func}' is not a function")
            arg = eval(arg_expr, env)
            new_env = func.env.copy()
            new_env[func.param] = arg
            return eval(func.body, new_env)

        case Assign(name, value_expr):
            if name not in env:
                raise NameError(f"Variable '{name}' is not defined")
            env[name] = eval(value_expr, env)
            return env[name]

        case Seq(first, second):
            eval(first, env)
            return eval(second, env)

        case Show(expr):
            result = eval(expr, env)
            print(result)
            return result

        case Read():
            user_input = input().strip()
            try:
                return int(user_input)
            except ValueError:
                raise ValueError("Invalid input, expected an integer")

        case _:
            raise TypeError(f"Unknown expression type: {expr}")

if __name__ == "__main__":
    print(eval(Concat(Lit("hello"), Lit(" world"))))  # Expected: "hello world"
    print(eval(Replace(Lit("hello world"), Lit("world"), Lit("Python"))))  # Expected: "hello Python"

    fun_expr = Letfun(
        name="addOne",
        param="x",
        body=Add(Name("x"), Lit(1)),
        in_expr=App(Name("addOne"), Lit(41))
    )
    print(eval(fun_expr))  # Expected: 42