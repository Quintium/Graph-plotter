import math, sympy
from sympy.parsing.sympy_parser import parse_expr
from functools import lru_cache

# class for functions
class Function:
    def __init__(self, string):
        self.string, self.function = self.parse_function(string)	

    # parse function
    def parse_function(self, function):
        # strip function of whitespace
        function = function.strip()

        # strip function of f(x)=, g(x)=, y= ...
        if "=" in function:
            function = function[function.index("=") + 1:]

        # separate characters from numbers and brackets by multiplication
        for i in range(len(function) - 1, -1, -1):
            if function[i].isalpha() and self.is_standalone(function, i) and self.char_equals(function, i + 1, "("):
                function = function[:i + 1] + "*" + function[i + 1:]
            if (function[i] == ")" or function[i].isdigit()) and self.char_exists(function, i + 1) and (function[i + 1].isalpha() or function[i + 1] == "("):
                function = function[:i + 1] + "*" + function[i + 1:]
            if (function[i] == ")" and self.char_exists(function, i + 1) and function[i + 1].isdigit()):
                function = function[:i + 1] + "*" + function[i + 1:]

        # replace ^ in the function with **
        function = function.replace("^", "**")

        # check function for missing closed brackets
        function = self.add_missing_brackets(function)

        # replace backwards standalone es with exp(1) and i with ((-1)**(1/2)) to avoid sympy confusing it with a variable
        for i in range(len(function) - 1, -1, -1):
            if function[i] == "e" and self.is_standalone(function, i):
                function = function[:i] + "exp(1)" + function[i + 1:]
            if function[i] == "i" and self.is_standalone(function, i):
                function = function[:i] + "((-1)**(1/2))" + function[i + 1:]

        # try to parse function with sympy
        try:
            functionExpr = parse_expr(function)
            return function, sympy.lambdify(sympy.symbols("x"), functionExpr)
        except:
            try:
                return function, sympy.lambdify(sympy.symbols("x"), function)
            except:
                return function, lambda x: None

    # function to add missing brackets
    def add_missing_brackets(self, function):
        # check if function has missing brackets
        brackets = function.count("(") - function.count(")")

        # if there are missing brackets, add them
        if brackets > 0:
            function += ")" * brackets

        return function

    # check if char in string is not part of a word
    def is_standalone(self, string, i):
        return (not self.char_exists(string, i - 1) or not string[i - 1].isalpha()) and (not self.char_exists(string, i + 1) or not string[i + 1].isalpha())

    # check if index is in range of the string
    def char_exists(self, string, index):
        return index >= 0 and index < len(string)

    # check if char in string exists and equals the given char
    def char_equals(self, string, index, char):
        return index >= 0 and index < len(string) and string[index] == char

    # function that returns the value of the function at a given x
    @lru_cache(maxsize=20000)
    def get_value(self, x):
        # eval functon
        try:
            # if value is a float or int, return it
            value = self.function(x)
            if isinstance(value, float) or isinstance(value, int):
                return value
            else:
                return None
        except:
            return None

    # return if function is empty
    def is_empty(self):
        return self.string == ""

    # print cache info
    def print_cache_info(self):
        print(self.get_value.cache_info())