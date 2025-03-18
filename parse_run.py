from lark import Lark, Transformer
from pathlib import Path
from interp import *  

parser = Lark(
    Path('expr.lark').read_text(),
    start='expr',
    parser='earley',
    lexer='dynamic',
    propagate_positions=True,
    maybe_placeholders=True,
    ambiguity='explicit',
    cache=False
)

class ExprTransformer(Transformer):
    def number(self, n):
        return Lit(int(n[0]))

    def string(self, s):
        return Lit(s[0][1:-1])  # Remove quotes

    def name(self, n):
        return Name(str(n[0]))

    def assign(self, args):
        return Assign(args[0], args[1])

    def seq(self, args):
        if len(args) == 2:
            return Seq(args[0], args[1])
        return args[0]  

    def letfun(self, args):
        return Letfun(name=str(args[0]), param=str(args[1]), body=args[2], in_expr=args[3])

    def let(self, args):
        return Let(name=str(args[0]), value_expr=args[1], body=args[2])

    def app(self, args):
        return App(args[0], args[1])

    def reverse_str(self, args):
        return ReverseStr(args[0])

    def if_(self, args):
        return If(cond=args[0], then=args[1], else_=args[2])

    def add(self, args):
        return Add(args[0], args[1])

    def sub(self, args):
        return Sub(args[0], args[1])

    def mul(self, args):
        return Mul(args[0], args[1])

    def div(self, args):
        return Div(args[0], args[1])

    def neg(self, args):
        return Neg(args[0])

    def eq(self, args):
        return Eq(args[0], args[1])

    def lt(self, args):
        return Lt(args[0], args[1])

    def and_(self, args):
        return And(args[0], args[1])

    def or_(self, args):
        return Or(args[0], args[1])

    def not_(self, args):
        return Not(args[0])
    
    def not_not(self, args):
        return Not(Not(args[0]))
    
    def not_eq(self, args):
        raise SyntaxError("Unexpected '!=' operator")

    def read(self, _):
        return Read()

    def show(self, args):
        return Show(args[0])

    def parens(self, args):
        return args[0]
    
    def or_expr(self, args):
        return Or(args[0], args[1])

    def and_expr(self, args):
        return And(args[0], args[1])
    
    def true(self, _):
        return Lit(True)

    def false(self, _):
        return Lit(False)
    
    def not_not(self, args):
        return Not(Not(args[0]))

def just_parse(expr_str):
    tree = parser.parse(expr_str)
    return ExprTransformer().transform(tree)

def parse_and_run(expr_str):
    tree = parser.parse(expr_str)
    print(tree.pretty())  
    ast = ExprTransformer().transform(tree)
    print("AST:", ast)
    result = eval(ast)
    print("Result:", result)

if __name__ == "__main__":
    parse_and_run("5 + 3 * 2")  
    parse_and_run("10 / 2 + 3")  
    parse_and_run("10 - 2 * 3")  
    parse_and_run("true && false || true")  
    parse_and_run("!false")  
    parse_and_run("!!true")  
    parse_and_run('"Hello" ++ " World"')  
    parse_and_run('replace("Hello World", "World", "Python")')  
    parse_and_run("let x = 10 in x + 5 end")  
    parse_and_run("let x = 2 in let y = 3 in x * y end end")  
    parse_and_run("letfun addOne(x) = x + 1 in addOne(5) end")  
    parse_and_run("letfun square(x) = x * x in square(4) end")  
    parse_and_run("if true then 5 else 10")  
    parse_and_run("if false then 5 else 10")  
    parse_and_run("true || false && false")  

    try:
        parse_and_run("x == y == z")  
    except SyntaxError as e:
        print(f"Expected Error: {e}")

    try:
        parse_and_run("10 / 0")  
    except ZeroDivisionError as e:
        print(f"Expected Error: {e}")

    try:
        parse_and_run("x + 5")  
    except NameError as e:
        print(f"Expected Error: {e}")

    try:
        parse_and_run("5(10)")  
    except TypeError as e:
        print(f"Expected Error: {e}")