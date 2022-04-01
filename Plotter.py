# Pygame graph plotter that plots a function given by the user
# There's an option to animate the graph, the zoom can be controlled by the mouse wheel and the screen can be dragged around.
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

        # separate characters from numbers and brackets by multiplication
        for i in range(len(function) - 1, -1, -1):
            if function[i].isalpha() and self.is_standalone(function, i) and self.char_equals(function, i + 1, "("):
                function = function[:i + 1] + "*" + function[i + 1:]
            if (function[i] == ")" or function[i].isdigit()) and self.char_exists(function, i + 1) and (function[i + 1].isalpha() or function[i + 1] == "("):
                function = function[:i + 1] + "*" + function[i + 1:]
            if (function[i] == ")" and self.char_exists(function, i + 1) and function[i + 1].isdigit()):
                function = function[:i + 1] + "*" + function[i + 1:]

        # replace backwards standalone es with exp(1) to avoid sympy convusing it with a variable
        for i in range(len(function) - 1, -1, -1):
            if function[i] == "e" and self.is_standalone(function, i):
                function = function[:i] + "exp(1)" + function[i + 1:]

        # strip function of whitespace
        function = function.strip()

        # strip function of f(x)=, g(x)=, y= ...
        if "=" in function:
            function = function[function.index("=") + 1:]

        self.functionStr = function

        # try to parse function with sympy
        try:
            functionExpr = parse_expr(function)
            self.function = lambdify(symbols("x"), functionExpr)
        except:
            try:
                self.function = lambdify(symbols("x"), function)
            except:
                self.function = None

        # set screen
        self.screen = screen
        self.width = self.screen.get_width()
        self.height = self.screen.get_height()

        # set font
        self.small_font = pygame.font.SysFont("arial", 12)

        # set zoom
        self.min_x = -10
        self.max_x = 10
        self.min_y = -10
        self.max_y = 10
        self.zoom_speed = 0.05

    # check if char in string is not part of a word
    def is_standalone(self, string, i):
        return (not self.char_exists(string, i - 1) or not string[i - 1].isalpha()) and (not self.char_exists(string, i + 1) or not string[i + 1].isalpha())

    # check if index is in range of the string
    def char_exists(self, string, index):
        return index >= 0 and index < len(string)

    # check if char in string exists and equals the given char
    def char_equals(self, string, index, char):
        return index >= 0 and index < len(string) and string[index] == char

    def map_value(self, value, low1, high1, low2, high2):
        return low2 + (value - low1) * (high2 - low2) / (high1 - low1)

    # function that returns the value of the function at a given x
    def get_value(self, x):
        # eval functon
        try:
            value = self.function(x)
            if isinstance(value, Expr):
                # if there's a "variable" in the expression, return None
                return None
            else:
                return value
        except:
            return None

    # function to zoom in
    def zoom_in(self):
        # if zoom limit of 0.00000001 is reached, return
        if (self.max_x - self.min_x) < 0.00000001 or (self.max_y - self.min_y) < 0.00000001:
            return

        change_x = (self.max_x - self.min_x) * self.zoom_speed
        change_y = (self.max_y - self.min_y) * self.zoom_speed

        self.min_x += change_x
        self.max_x -= change_x
        self.min_y += change_y
        self.max_y -= change_y

    # function to zoom out
    def zoom_out(self):
        # if zoom limit of 100000000 is reached, return
        if (self.max_x - self.min_x) > 100000000 or (self.max_y - self.min_y) > 100000000:
            return

        change_x = (self.max_x - self.min_x) * self.zoom_speed
        change_y = (self.max_y - self.min_y) * self.zoom_speed

        self.min_x -= change_x
        self.max_x += change_x
        self.min_y -= change_y
        self.max_y += change_y

    # move screen
    def move(self, rel):
        # calculate dragged distance to units
        change_x = -self.map_value(rel[0], 0, self.width, 0, (self.max_x - self.min_x))
        change_y = self.map_value(rel[1], 0, self.height, 0, (self.max_y - self.min_y))

        self.min_x += change_x
        self.max_x += change_x
        self.min_y += change_y
        self.max_y += change_y

    # function that draws the grid
    def draw_grid(self):
        # fill screen white
        self.screen.fill((255, 255, 255))

        # get biggest grid unit that starts with 1, 2, 5, that is smaller than 100 pixels
        limit = self.map_value(100, 0, self.width, 0, self.max_x - self.min_x)
        grid_unit = 1
        power = 0
        if grid_unit < limit:
            while grid_unit * 10 < limit:
                grid_unit *= 10
                power += 1
        else:
            while grid_unit > limit:
                grid_unit /= 10
                power -= 1
        first_digit = limit / grid_unit
        if first_digit < 2:
            grid_unit *= 1
        elif first_digit < 5:
            grid_unit *= 2
        else:
            grid_unit *= 5

        # calculate axis positions
        x0_pixels = self.map_value(0, self.min_x, self.max_x, 0, self.width)
        y0_pixels = self.map_value(0, self.min_y, self.max_y, self.height, 0)

        # draw a grid with the calculated grid unit
        for x in arange(ceil(self.min_x / grid_unit) * grid_unit, self.max_x + limit * 2, grid_unit):
            # calculate x value in pixels
            x_pixels = self.map_value(x, self.min_x, self.max_x, 0, self.width)
            pygame.draw.line(self.screen, (200, 200, 200), (x_pixels, 0), (x_pixels, self.height))

            # draw number along axes
            if x != 0:
                text = self.small_font.render(str(int(x)) if power >= 0 else str(round(x, -power)), True, (0, 0, 0))
                text_y = y0_pixels + 1

                # limit text_y to screen
                text_y = max(0, min(text_y, self.height - text.get_height()))
                self.screen.blit(text, (x_pixels - text.get_width() - 1, text_y))

        for y in arange(ceil(self.min_y / grid_unit) * grid_unit, self.max_y + limit * 2, grid_unit):
            # calculate y value in pixels
            y_pixels = self.map_value(y, self.min_y, self.max_y, self.height, 0)
            pygame.draw.line(self.screen, (200, 200, 200), (0, y_pixels), (self.width, y_pixels))

            # draw number along axes
            if y != 0:
                text = self.small_font.render(str(int(y)) if power >= 0 else str(round(y, -power)), True, (0, 0, 0))
                text_x = x0_pixels + 3

                # limit text_x to screen
                text_x = max(0, min(text_x, self.width - text.get_width()))
                self.screen.blit(text, (text_x, y_pixels - text.get_height() + 1))

        # draw x and y axis
        pygame.draw.line(self.screen, (0, 0, 0), (x0_pixels, 0), (x0_pixels, self.height))
        pygame.draw.line(self.screen, (0, 0, 0), (0, y0_pixels), (self.width, y0_pixels))

    # function that draws the graph
    def draw_function(self):
        previousX = None
        previousY = None

        # draw the graph
        for pixel in arange(0, self.width):
            # convert pixel to x
            x = self.map_value(pixel, 0, self.width, self.min_x, self.max_x)

            # evaluate the function
            y = self.get_value(x)

            if y is not None:
                # map x from -10 to 10 to 0 to screen width
                x = self.map_value(x, self.min_x, self.max_x, 0, self.width)

                # map y from -10 to 10 to 0 to screen height
                y = self.map_value(y, self.max_y, self.min_y, 0, self.height)

                if previousX is not None:
                    pygame.draw.line(screen, (255, 0, 0), (previousX, previousY), (x, y))

                # save previous x and y
                previousX = x
                previousY = y
            else:
                previousX = None
                previousY = None

        pygame.display.flip()

# initialize pygame with 800x800 screen and caption "Graph plotter"
pygame.init()
width = 800
height = 800
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
    rect.center = (width / 2, height / 2)
    pygame.draw.rect(screen, (255, 255, 255), rect)
    screen.blit(text, (width / 2 - text.get_width() / 2, rect.y))
    screen.blit(input_text, (width / 2 - input_text.get_width() / 2, rect.y + text.get_height()))

    pygame.display.update()

# create graph plotter for function
graph_plotter = GraphPlotter(function, screen)

# main loop
while True:
    graph_plotter.draw_grid()
    graph_plotter.draw_function()

    for event in pygame.event.get():
        # check for mouse wheel event
        if event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 4:
                graph_plotter.zoom_in()
            elif event.button == 5:
                graph_plotter.zoom_out()

        # check for mouse drag event
        elif event.type == pygame.MOUSEMOTION:
            if event.buttons[0] == 1:
                graph_plotter.move(event.rel)

        if event.type == pygame.QUIT:
            pygame.quit()
            quit()