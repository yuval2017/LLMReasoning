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
        "*": {SYMOPKEY: "*", FUNCKEY: sympy.Mul, LLMSYMKEY: "×",SYMPYSTRFUNCKEY: lambda a,b: f"({a})*({b})", ADDSTRINGFUNCKEY: lambda a,b: f"({a})*({b})", RANGEKEY: (float("-inf"), float("inf")), RANDVALSGENKEY: lambda : random.randint(1,10)},
        "/": {SYMOPKEY: "/", FUNCKEY: lambda a,b: sympy.Mul(a,sympy.Pow(b,-1)), SYMPYSTRFUNCKEY: lambda a,b: f"({a})/({b})", LLMSYMKEY: "÷", ADDSTRINGFUNCKEY: lambda a,b: f"({a})/({b})", RANGEKEY: (float("-inf"), float("inf")), },
        "sqrt": {SYMOPKEY: "sqrt", FUNCKEY: sympy.sqrt, LLMSYMKEY: "√", SYMPYSTRFUNCKEY: lambda a: f"sqrt({a})", ADDSTRINGFUNCKEY: lambda a: f"sqrt({a})", RANGEKEY: (0, float("inf"))},
        "exp": {SYMOPKEY: "exp", FUNCKEY: sympy.exp, LLMSYMKEY: "exp", SYMPYSTRFUNCKEY: lambda a: f"exp({a})", ADDSTRINGFUNCKEY: lambda a: f"e^({a})", RANGEKEY: (float("-inf"), float("inf"))},
        "log": {SYMOPKEY: "log", FUNCKEY: sympy.log, LLMSYMKEY: "log", SYMPYSTRFUNCKEY: lambda a,b: f"log({a},{b})", ADDSTRINGFUNCKEY: lambda a,b: f"log_{b}({a})", RANGEKEY: (0, float("inf"))},
        "pow": {SYMOPKEY: "**", FUNCKEY: sympy.Pow, LLMSYMKEY: "^", SYMPYSTRFUNCKEY: lambda a,b: f"({a})**{b}", ADDSTRINGFUNCKEY: lambda a,b: f"({a})^{b}", RANGEKEY: (float("-inf"), float("inf"))},
        "sin": {SYMOPKEY: "sin", FUNCKEY: sympy.sin, LLMSYMKEY: "sin", SYMPYSTRFUNCKEY: lambda a: f"sin({a})", ADDSTRINGFUNCKEY: lambda a: f"sin({a})", RANGEKEY: (float("-inf"), float("inf"))},
        "cos": {SYMOPKEY: "cos", FUNCKEY: sympy.cos, LLMSYMKEY: "cos", SYMPYSTRFUNCKEY: lambda a: f"cos({a})", ADDSTRINGFUNCKEY: lambda a: f"cos({a})", RANGEKEY: (float("-inf"), float("inf"))},
        "tan": {SYMOPKEY: "tan", FUNCKEY: sympy.tan, LLMSYMKEY: "tan", SYMPYSTRFUNCKEY: lambda a: f"tan({a})", ADDSTRINGFUNCKEY: lambda a: f"tan({a})", RANGEKEY: (float("-inf"), float("inf"))},
        "asin": {SYMOPKEY: "asin", FUNCKEY: sympy.asin, LLMSYMKEY: "asin", SYMPYSTRFUNCKEY: lambda a: f"asin({a})", ADDSTRINGFUNCKEY: lambda a: f"asin({a})", RANGEKEY: (-1, 1)},
        "acos": {SYMOPKEY: "acos", FUNCKEY: sympy.acos, LLMSYMKEY: "acos", SYMPYSTRFUNCKEY: lambda a: f"acos({a})", ADDSTRINGFUNCKEY: lambda a: f"acos({a})", RANGEKEY: (-1, 1)},
        "atan": {SYMOPKEY: "atan", FUNCKEY: sympy.atan, LLMSYMKEY: "atan", SYMPYSTRFUNCKEY: lambda a: f"atan({a})", ADDSTRINGFUNCKEY: lambda a: f"atan({a})", RANGEKEY: (float("-inf"), float("inf"))},
        "sinh": {SYMOPKEY: "sinh", FUNCKEY: sympy.sinh, LLMSYMKEY: "sinh", SYMPYSTRFUNCKEY: lambda a: f"sinh({a})", ADDSTRINGFUNCKEY: lambda a: f"sinh({a})", RANGEKEY: (float("-inf"), float("inf"))},
        "cosh": {SYMOPKEY: "cosh", FUNCKEY: sympy.cosh, LLMSYMKEY: "cosh", SYMPYSTRFUNCKEY: lambda a: f"cosh({a})", ADDSTRINGFUNCKEY: lambda a: f"cosh({a})", RANGEKEY: (float("-inf"), float("inf"))},
        "tanh": {SYMOPKEY: "tanh", FUNCKEY: sympy.tanh, LLMSYMKEY: "tanh", SYMPYSTRFUNCKEY: lambda a: f"tanh({a})", ADDSTRINGFUNCKEY: lambda a: f"tanh({a})", RANGEKEY: (float("-inf"), float("inf"))},
        "acosh": {SYMOPKEY: "acosh", FUNCKEY: sympy.acosh, LLMSYMKEY: "acosh", SYMPYSTRFUNCKEY: lambda a: f"acosh({a})", ADDSTRINGFUNCKEY: lambda a: f"acosh({a})", RANGEKEY: (1, float("inf"))},
        "asinh": {SYMOPKEY: "asinh", FUNCKEY: sympy.asinh, LLMSYMKEY: "asinh", SYMPYSTRFUNCKEY: lambda a: f"asinh({a})", ADDSTRINGFUNCKEY: lambda a: f"asinh({a})", RANGEKEY: (float("-inf"), float("inf"))},
        "atanh": {SYMOPKEY: "atanh", FUNCKEY: sympy.atanh, LLMSYMKEY: "atanh", SYMPYSTRFUNCKEY: lambda a: f"atanh({a})", ADDSTRINGFUNCKEY: lambda a: f"atanh({a})", RANGEKEY: (-1, 1)},
        "zeta": {SYMOPKEY: "zeta", FUNCKEY: sympy.zeta, LLMSYMKEY: "ζ", SYMPYSTRFUNCKEY: lambda a: f"zeta({a})", ADDSTRINGFUNCKEY: lambda a: f"zeta({a})", RANGEKEY: (1, float("inf"))},
        # Add more operations and functions as needed
    }

    more_vars_op_dict = {"log": lambda _: random.randint(2,10), 
                         "*": lambda _: random.randint(50, 200),
                        "/": lambda _: random.randint(50, 200),
                         "pow": lambda _: random.randint(3,5)}

    def _get_all_possible_ops(self):
        curr_val = self.sym_expr.evalf()
        possible_ops = []
        for key,value in self.operation_dict.items():
            min_range, max_range = value[RANGEKEY]
            if min_range < curr_val < max_range:
                possible_ops.append(key)
        return possible_ops
    
    def __init__(self, expr_str: str, filter_ops=None):
        if filter_ops is not None:
            self.operation_dict = {k:v for k,v in self.operation_dict.items() if k in filter_ops}
        self._expr_str = expr_str
        self._expr_demo_str = expr_str  # more coherent expression
        self.sym_expr = sympy.sympify(expr_str)


    def __next__(self):

        # choose randomly from all ops
        op = random.choice(self._get_all_possible_ops())
        op_data = self.operation_dict[op]
        curr_val = self.sym_expr.evalf()
        if op in self.more_vars_op_dict:
            # get random value for more_vars_op_dict
            rand_val = self.more_vars_op_dict[op](curr_val)
            # update expr_demo_str
            self._expr_demo_str = op_data[ADDSTRINGFUNCKEY](self._expr_demo_str, rand_val)
            # update expr_str
            self._expr_str = op_data[SYMPYSTRFUNCKEY](self._expr_str, rand_val)
            # update sym_expr
            self.sym_expr = op_data[FUNCKEY](self.sym_expr, rand_val)


        else:
            # update expr_demo_str
            self._expr_demo_str = op_data[ADDSTRINGFUNCKEY](self._expr_demo_str)
            # update expr_str
            self._expr_str = op_data[SYMPYSTRFUNCKEY](self._expr_str)
            # update sym_expr
            self.sym_expr = op_data[FUNCKEY](self.sym_expr)


        return self._expr_str, op



    @property
    def expr_demo_str(self):
        return self._expr_demo_str
    
    @expr_demo_str.setter
    def expr_demo_str(self, value):
        self._expr_demo_str = value

    @property
    def expr_str(self):
        return self._expr_str

    @expr_str.setter
    def expr_str(self, value):
        if self._check_validity(value) is not None:
            raise ValueError(f"Error: Invalid expression: {value}")
        self._expr_str = value
        
    
    def __iter__(self):
        return self

    def _check_validity(self, value):
        """Check if the expression is valid."""
        try:
            sympy.sympify(value)
            return None
        except Exception as e:
            return f"Error: {e}"

















