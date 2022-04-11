import math, sympy
from sympy.parsing.sympy_parser import parse_expr
from functools import lru_cache
from StringUtilities import add_missing_brackets, is_standalone, char_exists, char_equals

# class for functions
class Function:
    def __init__(self, string):
        if string == "Error":
            self.string, self.value, self.function = "Error", None, None
        else:
            self.string, self.value, self.function = self.parse_function(string)

    # parse function, returns function string, function constant (if possible), and function
    def parse_function(self, function):
        # strip function of whitespace
        function = function.strip()

        # separate characters from numbers and brackets by multiplication
        for i in range(len(function) - 1, -1, -1):
            if function[i].isalpha() and is_standalone(function, i) and char_equals(function, i + 1, "("):
                function = function[:i + 1] + "*" + function[i + 1:]
            if (function[i] == ")" or function[i].isdigit()) and char_exists(function, i + 1) and (function[i + 1].isalpha() or function[i + 1] == "("):
                function = function[:i + 1] + "*" + function[i + 1:]
            if (function[i] == ")" and char_exists(function, i + 1) and function[i + 1].isdigit()):
                function = function[:i + 1] + "*" + function[i + 1:]

        # replace ^ in the function with **
        function = function.replace("^", "**")

        # replace backwards standalone es with exp(1) and i with ((-1)**(1/2)) to avoid sympy confusing it with a variable
        for i in range(len(function) - 1, -1, -1):
            if function[i] == "e" and is_standalone(function, i):
                function = function[:i] + "exp(1)" + function[i + 1:]
            if function[i] == "i" and is_standalone(function, i):
                function = function[:i] + "((-1)**(1/2))" + function[i + 1:]

        try:
            # try to parse function with sympy, works for math operations
            functionExpr = parse_expr(function)
        	
            # check if function is a constant
            try:
                functionValue = float(functionExpr)
                return function, functionValue, lambda x: functionValue
            except:
                # check if function contains an unknown symbol
                if len(functionExpr.free_symbols) > 1 or len(functionExpr.free_symbols) == 1 and sympy.symbols("x") not in functionExpr.free_symbols:
                    return function, None, None
                else:
                    # check if function is not an expression
                    if not isinstance(functionExpr, sympy.Expr):
                        return function, None, None
                    else:
                        return function, None, sympy.lambdify(sympy.symbols("x"), functionExpr)
        except:
            # try to parse function with lambdify, works for python expressions
            try:
                f = sympy.lambdify(sympy.symbols("x"), function)
                
                # check if function is a constant
                if "x" not in function:
                    try:
                        value = eval(function)
                        if isinstance(value, (int, float)):
                            return function, value, lambda x: value
                        else:
                            return function, None, None
                    except:
                        return function, None, None
                else:
                    return function, None, f
            except:
                return function, None, None

    # function that returns the value of the function at a given x
    @lru_cache(maxsize=20000)
    def get_value(self, x):
        # if the function is a constant, return the constant
        if self.value != None:
            return self.value
        else:
            # eval function
            try:
                # if value is a float or int, return it
                value = self.function(x)
                if isinstance(value, float) or isinstance(value, int):
                    return value
                else:
                    return None
            except:
                return None

    # return if function is valid
    def is_valid(self):
        return self.function is not None

    # print cache info
    def print_cache_info(self):
        print(self.get_value.cache_info()) 