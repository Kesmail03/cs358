# 1. Stopped using Python closures and explicitly passed environments in function evaluation.
# 2. Allowed function applications on expressions instead of just names.

from dataclasses import dataclass
from typing import Union, Dict, Callable
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
    env: Dict[str, Literal]

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

    def eval(self, env):
        str_val = self.string_expr.eval(env)
        if isinstance(str_val, str):
            return str_val[::-1]  # Reverse string
        raise TypeError("Invalid operand for reverse function, expected string")


@dataclass
class LengthStr:
    string_expr: 'Expr'

    def eval(self, env):
        str_val = self.string_expr.eval(env)
        if isinstance(str_val, str):
            return len(str_val)  # Return string length
        raise TypeError("Invalid operand for length function, expected string")

@dataclass
class Show:
    expr: 'Expr'

@dataclass
class Read:
    pass

Expr = Union[Lit, Add, Sub, Mul, Div, Neg, And, Or, Not, Let, Name, Eq, Lt, If, Concat, Replace, Letfun, App, Assign, Seq, Show, Read]
Env = Dict[str, Literal]
Store = Dict[str, Literal]

def eval(expr: Expr, env: Env = None, store: Dict[str, Literal] = None) -> Literal:
    if env is None:
        env = {}
    if store is None:
        store = {}

    match expr:
        case Lit(value=value):
            return value

        case Add(left=left, right=right):
            return eval(left, env) + eval(right, env)

        case Sub(left=left, right=right):
            return eval(left, env) - eval(right, env)

        case Mul(left=left, right=right):
            return eval(left, env) * eval(right, env)

        case Div(left=left, right=right):
            right_val = eval(right, env)
            if right_val == 0:
                raise ZeroDivisionError("Division by zero")
            return eval(left, env) // right_val

        case Neg(expr=subexpr):
            return -eval(subexpr, env)

        case And(left=left, right=right):
            left_val = eval(left, env, store)
            right_val = eval(right, env, store)
            if not isinstance(left_val, bool) or not isinstance(right_val, bool):
                raise TypeError("Operands of '&&' must be boolean") # Changed
            return left_val and right_val

        case Or(left=left, right=right):
            left_val = eval(left, env, store)
            right_val = eval(right, env, store)
            if not isinstance(left_val, bool) or not isinstance(right_val, bool):
                raise TypeError("Operands of '||' must be boolean") # Changed
            return left_val or right_val
        
        case Not(expr=subexpr):
            val = eval(subexpr, env, store)
            if not isinstance(val, bool):
                raise TypeError("Operand of '!' must be boolean") 
            return not val

        case Let(name=name, value_expr=value_expr, body=body):
            new_env = env.copy()
            new_env[name] = eval(value_expr, new_env)
            return eval(body, new_env)

        case Name(name=name):
            if name not in env:
                raise NameError(f"Variable '{name}' is not defined")
            return env[name]

        case Eq(left=left, right=right):
            if isinstance(left, Eq) or isinstance(left, Lt):
                raise SyntaxError("Chained comparisons are not allowed")
            return eval(left, env) == eval(right, env)
        case Lt(left=left, right=right):
            return eval(left, env) < eval(right, env)
        
        case If(cond=cond, then=then_branch, else_=else_branch):
            cond_val = eval(cond, env, store)
            if not isinstance(cond_val, bool):
                raise TypeError("Condition of 'if' must be boolean") # Changed
            return eval(then_branch, env, store) if cond_val else eval(else_branch, env, store)
        
        case Concat(left=left, right=right):
            left_val, right_val = eval(left, env), eval(right, env)
            if isinstance(left_val, str) and isinstance(right_val, str):
                return left_val + right_val
            raise TypeError("Concatenation requires string operands")

        case Replace(string=string, target=target, replacement=replacement):
            str_val = eval(string, env)
            target_val = eval(target, env)
            replacement_val = eval(replacement, env)

            if isinstance(str_val, str) and isinstance(target_val, str) and isinstance(replacement_val, str):
                return str_val.replace(target_val, replacement_val)
            else:
                raise TypeError("Replace requires string operands")

        #explicitly passing environment
        case Letfun(name=name, param=param, body=body, in_expr=in_expr):
            new_env = env.copy()
            new_env[name] = FunDef(param=param, body=body, env=new_env)   
            return eval(in_expr, new_env)

        #allows function applications on expressions
        case App(fun_expr=fun_expr, arg_expr=arg_expr):
            func = eval(fun_expr, env)  # Should return a FunDef
            arg = eval(arg_expr, env)

            if isinstance(func, FunDef):
                new_env = func.env.copy()
                new_env[func.param] = arg
                return eval(func.body, new_env)
            else:
                raise TypeError(f"'{fun_expr}' is not a function")

        case Assign(name=name, value_expr=value_expr):
            if name in env and name not in store:
                store[name] = env[name]
            if name not in store:
                raise NameError(f"Cannot assign to undeclared variable '{name}'")
            store[name] = eval(value_expr, env, store)
            return store[name]

        case Seq(first=first, second=second):
            eval(first, env, store)
            return eval(second, env, store)

        case Show(expr=expr):
            result = eval(expr, env, store)
            print("Show:", result)
            return result

        case Read():
            if not sys.stdin.isatty():  
                return 42
            user_input = input("Enter an integer: ")
            try:
                return int(user_input)
            except ValueError:
                raise ValueError("Invalid input, expected an integer")
            
        case ReverseStr(string_expr):
            str_val = eval(string_expr, env)
            if isinstance(str_val, str):
                return str_val[::-1]  # Reverse the string
            raise TypeError("Invalid operand for reverse function, expected string")

        case LengthStr(string_expr):
            str_val = eval(string_expr, env)
            if isinstance(str_val, str):
                return len(str_val)  # Get string length
            raise TypeError("Invalid operand for length function, expected string")
            
        case Tree(data='parens', children=[inner_expr]):
            return eval(inner_expr, env, store)  

        case Tree(data='_ambig', children=options):
            for option in options:
                try:
                    return eval(option, env, store)  
                except Exception:
                    pass  
            raise BaseException(f"Ambiguous parse: No valid interpretation found for {options}")
        case _:
            print(f"Evaluating expression: {expr}")
            raise BaseException(f"Unknown expression type: {expr}")

if __name__ == "__main__":
    print(eval(Concat(Lit("hello"), Lit(" world"))))  
    print(eval(Replace(Lit("hello world"), Lit("world"), Lit("Python"))))  
    
    fun_expr = Letfun(
        name="addOne",
        param="x",
        body=Add(Name("x"), Lit(1)),
        in_expr=App(Name("addOne"), Lit(41))
    )
    print(eval(fun_expr))  # 42

'''
For my project I decided to go with the string domain. The other ones were more interesting but I thought they would be much harder so,
I wanted to go with strings. The intended use of this domain is to allow creation of personalized messages or constructing file paths.
Another use case would be to able to replace substrings or combine multiple strings into one. 
'''