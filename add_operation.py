import random
import sympy

SYMOPKEY = "sympy_op"
FUNCKEY = "func"
LLMSYMKEY = "llm_symbol"
ADDSTRINGFUNCKEY = "add_string_func"
RANGEKEY = "valid_range"
SYMPYSTRFUNCKEY = "sympy_str"
RANDVALSGENKEY = "rand_vals_gen_func"

def base_rand_func():
    return random.randint(1,10)

class ExpressionGenerator:
    operation_dict = {
        "*": {SYMOPKEY: "*", FUNCKEY: sympy.Mul, LLMSYMKEY: "×",
              SYMPYSTRFUNCKEY: lambda a,b: f"({a})*({b})",
              ADDSTRINGFUNCKEY: lambda a,b: f"({a})*({b})",
              RANGEKEY: (float("-inf"), float("inf")),
              RANDVALSGENKEY: lambda : random.randint(1,10)},
        "/": {SYMOPKEY: "/", FUNCKEY: lambda a,b: sympy.Mul(a,sympy.Pow(b,-1)),
              SYMPYSTRFUNCKEY: lambda a,b: f"({a})/({b})",
              LLMSYMKEY: "÷", ADDSTRINGFUNCKEY: lambda a,b: f"({a})/({b})",
              RANGEKEY: (float("-inf"), float("inf"))},
        "sqrt": {SYMOPKEY: "sqrt", FUNCKEY: sympy.sqrt, LLMSYMKEY: "√",
                 SYMPYSTRFUNCKEY: lambda a: f"sqrt({a})",
                 ADDSTRINGFUNCKEY: lambda a: f"sqrt({a})",
                 RANGEKEY: (0, float("inf"))},
        "exp": {SYMOPKEY: "exp", FUNCKEY: sympy.exp, LLMSYMKEY: "exp",
                SYMPYSTRFUNCKEY: lambda a: f"exp({a})",
                ADDSTRINGFUNCKEY: lambda a: f"e^({a})",
                RANGEKEY: (float("-inf"), float("inf"))},
        "log": {SYMOPKEY: "log", FUNCKEY: sympy.log, LLMSYMKEY: "log",
                SYMPYSTRFUNCKEY: lambda a,b: f"log({a},{b})",
                ADDSTRINGFUNCKEY: lambda a,b: f"log_{b}({a})",
                RANGEKEY: (0, float("inf"))},
        "pow": {SYMOPKEY: "**", FUNCKEY: sympy.Pow, LLMSYMKEY: "^",
                SYMPYSTRFUNCKEY: lambda a,b: f"({a})**{b}",
                ADDSTRINGFUNCKEY: lambda a,b: f"({a})^{b}",
                RANGEKEY: (float("-inf"), float("inf"))},
        "sin": {SYMOPKEY: "sin", FUNCKEY: sympy.sin, LLMSYMKEY: "sin",
                SYMPYSTRFUNCKEY: lambda a: f"sin({a})",
                ADDSTRINGFUNCKEY: lambda a: f"sin({a})",
                RANGEKEY: (float("-inf"), float("inf"))},
        "cos": {SYMOPKEY: "cos", FUNCKEY: sympy.cos, LLMSYMKEY: "cos",
                SYMPYSTRFUNCKEY: lambda a: f"cos({a})",
                ADDSTRINGFUNCKEY: lambda a: f"cos({a})",
                RANGEKEY: (float("-inf"), float("inf"))},
        "tan": {SYMOPKEY: "tan", FUNCKEY: sympy.tan, LLMSYMKEY: "tan",
                SYMPYSTRFUNCKEY: lambda a: f"tan({a})",
                ADDSTRINGFUNCKEY: lambda a: f"tan({a})",
                RANGEKEY: (float("-inf"), float("inf"))},
        "asin": {SYMOPKEY: "asin", FUNCKEY: sympy.asin, LLMSYMKEY: "asin",
                 SYMPYSTRFUNCKEY: lambda a: f"asin({a})",
                 ADDSTRINGFUNCKEY: lambda a: f"asin({a})",
                 RANGEKEY: (-1, 1)},
        "acos": {SYMOPKEY: "acos", FUNCKEY: sympy.acos, LLMSYMKEY: "acos",
                 SYMPYSTRFUNCKEY: lambda a: f"acos({a})",
                 ADDSTRINGFUNCKEY: lambda a: f"acos({a})",
                 RANGEKEY: (-1, 1)},
        "atan": {SYMOPKEY: "atan", FUNCKEY: sympy.atan, LLMSYMKEY: "atan",
                 SYMPYSTRFUNCKEY: lambda a: f"atan({a})",
                 ADDSTRINGFUNCKEY: lambda a: f"atan({a})",
                 RANGEKEY: (float("-inf"), float("inf"))},
        # Add more functions as needed
    }

    more_vars_op_dict = {"log": lambda _: random.randint(2,10),
                         "*": lambda _: random.randint(2,10),
                         "/": lambda _: random.randint(1,10),  # avoid 0
                         "pow": lambda _: random.randint(2,5)}
    
    def __init__(self, expr_str: str, filter_ops=None, valid_range=(-1e6, 1e6)):
        if filter_ops:
            self.operation_dict = {k:v for k,v in self.operation_dict.items() if k in filter_ops}
        self._expr_str = expr_str
        self._expr_demo_str = expr_str
        self.sym_expr = sympy.sympify(expr_str)
        self.min_val, self.max_val = valid_range  # r

    def _get_all_possible_ops(self):
            curr_val = self.sym_expr.evalf()
            possible_ops = []
            for key, value in self.operation_dict.items():
                min_range, max_range = value[RANGEKEY]
                if min_range < curr_val < max_range:
                    possible_ops.append(key)
            return possible_ops

    def __next__(self):
        while True:
            op = random.choice(self._get_all_possible_ops())
            op_data = self.operation_dict[op]
            curr_val = self.sym_expr.evalf()
            try:
                if op in self.more_vars_op_dict:
                    rand_val = self.more_vars_op_dict[op](curr_val)
                    if op == "/" and rand_val == 0: continue
                    if op == "log" and rand_val <= 0: continue
                    new_expr = op_data[FUNCKEY](self.sym_expr, rand_val)
                    new_demo = op_data[ADDSTRINGFUNCKEY](self._expr_demo_str, rand_val)
                    new_str = op_data[SYMPYSTRFUNCKEY](self._expr_str, rand_val)
                else:
                    if op in ["asin","acos"] and not (-1 <= curr_val <= 1):
                        continue
                    new_expr = op_data[FUNCKEY](self.sym_expr)
                    new_demo = op_data[ADDSTRINGFUNCKEY](self._expr_demo_str)
                    new_str = op_data[SYMPYSTRFUNCKEY](self._expr_str)
                # check if new_expr is within valid range
                val = new_expr.evalf()
                if not (self.min_val <= val <= self.max_val):
                    continue  # not in the range try again

                # Everything is fine, update expressions
                self.sym_expr = new_expr
                self._expr_demo_str = new_demo
                self._expr_str = new_str
                return self._expr_str, op
            except Exception:
                continue
    def __iter__(self):
        return self

    @property
    def expr_demo_str(self):
        return self._expr_demo_str

    @property
    def expr_str(self):
        return self._expr_str

    @expr_str.setter
    def expr_str(self, value):
        if self._check_validity(value) is not None:
            raise ValueError(f"Invalid expression: {value}")
        self._expr_str = value

    def _check_validity(self, value):
        try:
            sympy.sympify(value)
            return None
        except Exception as e:
            return f"Error: {e}"
