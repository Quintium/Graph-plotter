# Pygame graph plotter that plots a function given by the user from x = -10 to x = 10 and y = -10 to y = 10 and an increment of 0.005.
# There's an option to animate the graph and the zoom can be controlled by the mouse wheel.
# The function is given as a string and can contain any mathematical function with x as a variable.
# Python expressiosn as well as integrals and derivatives are supported via integrate() and diff() functions.
# The grid is drawn every 2 units of x and y.
# At the bottom is a bar with sliders for zoom and animation speed.

import pygame
from math import *
from numpy import *
from sympy import *
from sympy.parsing.sympy_parser import parse_expr

# class for graph plotter
class GraphPlotter:
    # clean function up upon initialization
    def __init__(self, function, screen):
        # replace ^ in the function with **
        function = function.replace("^", "**")

        # replace backwards standalone es with exp(1) to avoid sympy convusing it with a variable
        for i in range(len(function) - 1, -1, -1):
            if function[i] == "e" and self.is_standalone(function, i):
                function = function[:i] + "exp(1)" + function[i + 1:]

        # strip function of whitespace
        function = function.strip()

        # strip function of f(x)=, g(x)=, y= ...
        if "=" in function:
            function = function[function.index("=") + 1:]

        # loop through function backwards
        self.indices = []
        for i in range(len(function) - 1, -1, -1):
            # check if the character is a x between two non letters
            if function[i] == "x" and (self.is_standalone(function, i)):
                # if so, add the index to the list
                self.indices.append(i)

        self.functionStr = function

        # try to parse function with sympy
        try:
            functionExpr = parse_expr(function)
            self.function = lambdify(symbols("x"), functionExpr)
        except:
            self.function = lambdify(symbols("x"), function)

        # set screen
        self.screen = screen
        self.screen_width = self.screen.get_width()
        self.screen_height = self.screen.get_height()

        # set font
        self.small_font = pygame.font.SysFont("arial", 12)

    # check if char in string is not part of a word
    def is_standalone(self, string, i):
        return (i - 1 < 0 or not string[i - 1].isalpha()) and (i + 1 > len(string) - 1 or not string[i + 1].isalpha())

    def map_value(self, value, low1, high1, low2, high2):
        return low2 + (value - low1) * (high2 - low2) / (high1 - low1)

    # function that returns the value of the function at a given x
    def get_value(self, x):
        # eval functon
        try:
            value = self.function(x)
            if isinstance(value, Expr):
                value = value.evalf()
            else:
                value = float(value)
            return value
        except:
            return None

            """
            # replace x with the given x
            expression = self.functionStr
            for i in self.indices:
                expression = expression[:i] + "(" + str(x) + ")" + expression[i + 1:]

            # return the value of the function
            try:
                return eval(expression)
            except:
                return None"""

    # function that draws the grid
    def draw_grid(self):
        # fill screen white
        self.screen.fill((255, 255, 255))

        # draw a grid  with distance of 50 pixels
        for x in arange(0, self.screen_width, self.screen_width / 10):
            pygame.draw.line(self.screen, (200, 200, 200), (x, 0), (x, self.screen_height))
        for y in arange(0, self.screen_height, self.screen_height / 10):
            pygame.draw.line(self.screen, (200, 200, 200), (0, y), (self.screen_width, y))

        # draw numbers along the axes
        for i in range(-10, 10, 2):
            x = self.map_value(i, -10, 10, 0, self.screen_width)
            y = self.map_value(i, -10, 10, self.screen_height, 0)

            text = self.small_font.render(str(i), True, (0, 0, 0))
            self.screen.blit(text, (x - text.get_width() - 1, self.screen_height / 2 + 1))
            self.screen.blit(text, (self.screen_width / 2 + text.get_width() - 2, y - text.get_height() + 1))

        # draw x and y axis
        pygame.draw.line(self.screen, (0, 0, 0), (0, self.screen_height / 2), (self.screen_width, self.screen_height / 2))
        pygame.draw.line(self.screen, (0, 0, 0), (self.screen_width / 2, 0), (self.screen_width / 2, self.screen_height))

    def draw_function(self):
        previousX = None
        previousY = None

        # draw the graph
        for x in arange(-10, 10, 0.005):
            # evaluate the function
            y = self.get_value(x)

            if y is not None:
                # map x from -10 to 10 to 0 to screen_width
                x = self.map_value(x, -10, 10, 0, screen_width)

                # map y from -10 to 10 to 0 to screen_height
                y = self.map_value(y, 10, -10, 0, screen_height)

                if previousX is not None:
                    pygame.draw.line(screen, (255, 0, 0), (previousX, previousY), (x, y))

                # save previous x and y
                previousX = x
                previousY = y
            else:
                previousX = None
                previousY = None

            pygame.display.update()

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    quit()

# initialize pygame with 800x800 screen and caption "Graph plotter"
pygame.init()
screen_width = 800
screen_height = 800
screen = pygame.display.set_mode((800, 800))
pygame.display.set_caption("Graph plotter")

# set the icon to the icon.png file
icon = pygame.image.load("icon.png")
pygame.display.set_icon(icon)

# create an arial font
small_font = pygame.font.SysFont("arial", 12)
middle_font = pygame.font.SysFont("arial", 28)
big_font = pygame.font.SysFont("arial", 58)

# create a text box for the user to type in a function
function = ""
formula_entered = False

while not formula_entered:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            quit()

        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_BACKSPACE:
                function = function[:-1]
            elif event.key == pygame.K_RETURN:
                formula_entered = True
            else:
                function += event.unicode

    # print a big black "Choose a function" in the middle of the screen
    GraphPlotter("", screen).draw_grid()
    text = big_font.render("Choose a function:", True, (0, 0, 0))
    input_text = middle_font.render(function, True, (0, 0, 0))

    # draw a white rectangle with the text in the middle
    rect = pygame.Rect(0, 0, max(text.get_width(), input_text.get_width()), text.get_height() + input_text.get_height())
    rect.center = (screen_width / 2, screen_height / 2)
    pygame.draw.rect(screen, (255, 255, 255), rect)
    screen.blit(text, (screen_width / 2 - text.get_width() / 2, rect.y))
    screen.blit(input_text, (screen_width / 2 - input_text.get_width() / 2, rect.y + text.get_height()))

    pygame.display.update()

# create graph plotter for function
graph_plotter = GraphPlotter(function, screen)

# main loop
while True:
    graph_plotter.draw_grid()
    graph_plotter.draw_function()