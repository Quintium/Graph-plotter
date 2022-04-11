# module for function string utilities

# function to add missing brackets
def add_missing_brackets(function):
    # check if function has missing brackets
    brackets = function.count("(") - function.count(")")

    # if there are missing brackets, add them
    if brackets > 0:
        function += ")" * brackets

    return function

# check if char in string is not part of a word
def is_standalone(string, i):
    return (not char_exists(string, i - 1) or not string[i - 1].isalpha()) and (not char_exists(string, i + 1) or not string[i + 1].isalpha())

# check if index is in range of the string
def char_exists(string, index):
    return index >= 0 and index < len(string)

# check if char in string exists and equals the given char
def char_equals(string, index, char):
    return char_exists(string, index) and string[index] == char
