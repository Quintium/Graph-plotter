# Pygame graph plotter that plots a function given by the user
# There's an option to animate the graph, the zoom can be controlled by the mouse wheel and the screen can be dragged around.
# The function is given as a string and can contain any mathematical function with x as a variable.
# Python expressions as well as integrals and derivatives are supported via integrate() and diff() functions.
# The grid is drawn every 2 units of x and y.
# The graph can be animated by pressing the spacebar.
# The function can be changed in the bar at the bottom.

import pygame, pygame.gfxdraw, string
from math import *
from numpy import *
from sympy import *
from sympy.parsing.sympy_parser import parse_expr
from functools import lru_cache
from time import time

# class for graph plotter
class GraphPlotter:
    # clean function up upon initialization
    def __init__(self, screen, width, height, font):
        # set screen
        self.screen = screen
        self.width = width
        self.height = height

        # set zoom
        self.min_x = -self.width / 50 / 2
        self.max_x = self.width / 50 / 2
        self.min_y = -self.height / 50 / 2
        self.max_y = self.height / 50 / 2
        self.zoom_speed = 0.08

        # set animation state
        self.animation_speed = 0
        self.animation_x = self.max_x
        self.reset_timer = None

        self.functions = []
        self.function_strs = []

        # define colors list as red, blue, green, orange, cyan, magenta, brown, yellow, purple, gold
        self.colors = [(255, 0, 0), (0, 0, 255), (0, 255, 0), (255, 165, 0), (0, 255, 255), (255, 0, 255), (165, 42, 42), (255, 255, 0), (128, 0, 128), (255, 215, 0)]

        # set font
        self.font = font

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
            return function, lambdify(symbols("x"), functionExpr)
        except:
            try:
                return function, lambdify(symbols("x"), function)
            except:
                return function, lambda x: None

    # add function to list
    def add_function(self, function):
        function_str, function_lambda = self.parse_function(function)
        self.functions.append(function_lambda)
        self.function_strs.append(function_str)

    # replace function in list
    def replace_function(self, function, index):
        function_str, function_lambda = self.parse_function(function)
        self.functions[index] = function_lambda
        self.function_strs[index] = function_str

    # function to add missing brackets
    def add_missing_brackets(self, function):
        # check if function has missing brackets
        brackets = 0
        for char in function:
            if char == "(":
                brackets += 1
            elif char == ")":
                brackets -= 1

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

    def map_value(self, value, low1, high1, low2, high2):
        return low2 + (value - low1) * (high2 - low2) / (high1 - low1)

    # function that returns the value of the function at a given x
    @lru_cache(maxsize=100000)
    def get_value(self, x, string):
        # eval functon
        try:
            # if value is a float or int, return it
            value = self.functions[self.function_strs.index(string)](x)
            if isinstance(value, float) or isinstance(value, int):
                return value
            # if value is a complex number, return the real part
            elif isinstance(value, complex):
                return value.real
            else:
                return None
        except:
            return None

    # function to zoom in
    def zoom_in(self, pos):
        # if zoom limit of 0.00000001 is reached, return
        if (self.max_x - self.min_x) < 0.00000001 or (self.max_y - self.min_y) < 0.00000001:
            return

        self.zoom(pos, -self.zoom_speed * (self.max_x - self.min_x), -self.zoom_speed * (self.max_y - self.min_y))

    # function to zoom out
    def zoom_out(self, pos):
        # if zoom limit of 100000000 is reached, return
        if (self.max_x - self.min_x) > 100000000 or (self.max_y - self.min_y) > 100000000:
            return

        self.zoom(pos, self.zoom_speed * (self.max_x - self.min_x), self.zoom_speed * (self.max_y - self.min_y))

    # function to zoom based on mouse position and total change
    def zoom(self, pos, change_x, change_y):
        # convert mouse position to units
        pos_x = self.map_value(pos[0], 0, self.width, self.min_x, self.max_x)
        pos_y = self.map_value(pos[1], 0, self.height, self.max_y, self.min_y)

        # equation: map_value(pos) in previous zoom = map_value(pos) in new zoom => equation was solved for change in x and y
        min_x_change = (pos_x - self.min_x) * (1 - (self.max_x - self.min_x + change_x) / (self.max_x - self.min_x))
        max_x_change = min_x_change + change_x
        min_y_change = (pos_y - self.min_y) * (1 - (self.max_y - self.min_y + change_y) / (self.max_y - self.min_y))
        max_y_change = min_y_change + change_y

        # zooming
        self.min_x += min_x_change
        self.max_x += max_x_change
        self.min_y += min_y_change
        self.max_y += max_y_change

    # move screen
    def move(self, rel):
        # calculate dragged distance to units
        change_x = -self.map_value(rel[0], 0, self.width, 0, (self.max_x - self.min_x))
        change_y = self.map_value(rel[1], 0, self.height, 0, (self.max_y - self.min_y))

        self.min_x += change_x
        self.max_x += change_x
        self.min_y += change_y
        self.max_y += change_y

    # resize screen
    def resize(self, size):
        # convert one pixel to units
        pixel = self.map_value(1, 0, self.width, 0, self.max_x - self.min_x)

        # calculate change in width and height
        change_x = (size[0] - self.width) * pixel
        change_y = (size[1] - self.height) * pixel

        # resize coordinates
        self.min_x -= change_x / 2
        self.max_x += change_x / 2
        self.min_y -= change_y / 2
        self.max_y += change_y / 2

        # change width and height
        self.width = size[0]
        self.height = size[1]

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

        small_grid_unit = grid_unit / 5

        # draw light grey grid with distance grid_unit / 5
        for x in arange(ceil(self.min_x / small_grid_unit) * small_grid_unit, self.max_x + limit * 2, small_grid_unit):
            # calculate x value in pixels
            x_pixels = self.map_value(x, self.min_x, self.max_x, 0, self.width)
            pygame.draw.line(self.screen, (245, 245, 245), (x_pixels, 0), (x_pixels, self.height))

        for y in arange(ceil(self.min_y / small_grid_unit) * small_grid_unit, self.max_y + limit * 2, small_grid_unit):
            # calculate y value in pixels
            y_pixels = self.map_value(y, self.min_y, self.max_y, self.height, 0)
            pygame.draw.line(self.screen, (245, 245, 245), (0, y_pixels), (self.width, y_pixels))

        # draw grey grid with distance grid_unit
        for x in arange(ceil(self.min_x / grid_unit) * grid_unit, self.max_x + limit * 2, grid_unit):
            # calculate x value in pixels
            x_pixels = self.map_value(x, self.min_x, self.max_x, 0, self.width)
            pygame.draw.line(self.screen, (200, 200, 200), (x_pixels, 0), (x_pixels, self.height))

        for y in arange(ceil(self.min_y / grid_unit) * grid_unit, self.max_y + limit * 2, grid_unit):
            # calculate y value in pixels
            y_pixels = self.map_value(y, self.min_y, self.max_y, self.height, 0)
            pygame.draw.line(self.screen, (200, 200, 200), (0, y_pixels), (self.width, y_pixels))

        # draw numbers along the axes
        for x in arange(ceil(self.min_x / grid_unit) * grid_unit, self.max_x + limit * 2, grid_unit):
            if abs(x) > grid_unit / 2:
                text = self.font.render(str(int(x)) if power >= 0 else str(round(x, -power)), True, (0, 0, 0))
                text_y = y0_pixels + 1

                # limit text_y to screen
                text_y = max(1, min(text_y, self.height - text.get_height() - 1))
                self.screen.blit(text, (self.map_value(x, self.min_x, self.max_x, 0, self.width) - text.get_width() - 1, text_y))

        for y in arange(ceil(self.min_y / grid_unit) * grid_unit, self.max_y + limit * 2, grid_unit):
            if abs(y) > grid_unit / 2:
                text = self.font.render(str(int(y)) if power >= 0 else str(round(y, -power)), True, (0, 0, 0))
                text_x = x0_pixels + 3

                # limit text_x to screen
                text_x = max(1, min(text_x, self.width - text.get_width() - 1))
                self.screen.blit(text, (text_x, self.map_value(y, self.min_y, self.max_y, self.height, 0) - text.get_height() + 1))

        # draw x and y axis
        pygame.draw.line(self.screen, (0, 0, 0), (x0_pixels, 0), (x0_pixels, self.height))
        pygame.draw.line(self.screen, (0, 0, 0), (0, y0_pixels), (self.width, y0_pixels))

    # function that draws the graph
    def draw_function(self, index):
        previousX = None
        previousY = None

        # convert animation x to pixels
        animation_pixels = self.map_value(self.animation_x, self.min_x, self.max_x, 0, self.width)

        # draw the graph
        for pixel in arange(0, animation_pixels, 3):
            # convert pixel to x
            x = self.map_value(pixel, 0, self.width, self.min_x, self.max_x)

            # evaluate the function
            y = self.get_value(x, self.function_strs[index])

            if y is not None:
                # map x from -10 to 10 to 0 to screen width
                x = self.map_value(x, self.min_x, self.max_x, 0, self.width)

                # map y from -10 to 10 to 0 to screen height
                y = self.map_value(y, self.max_y, self.min_y, 0, self.height)

                if previousX is not None:
                    # draw line from previous point to current point
                    pygame.draw.line(screen, self.colors[index], (previousX, previousY), (x, y))

                # save previous x and y
                previousX = x
                previousY = y
            else:
                previousX = None
                previousY = None

    # function that draws all graphs
    def draw_graphs(self):
        # draw grid
        self.draw_grid()

        # draw function
        for i in range(len(self.functions)):
            # draw function if the string is not empty
            if self.function_strs[i] != "":
                self.draw_function(i)

        # function that handles the animation state
        if self.animation_speed == 0:
            self.animation_x = self.max_x
        else:
            if self.reset_timer is not None:
                self.animation_x = self.max_x
                if time() - self.reset_timer > 1:
                    self.animation_x = self.min_x
                    self.reset_timer = None
            elif self.animation_x > self.max_x:
                self.reset_timer = time()
            elif self.animation_x < self.min_x:
                self.animation_x = self.min_x
            else:
                # increase x of animation by animation speed converted to units
                self.animation_x += self.map_value(self.animation_speed * width / 1000, 0, self.width, 0, (self.max_x - self.min_x))

    # start animation
    def start_animation(self):
        self.animation_speed = 3
        self.animation_x = self.min_x
        self.reset_timer = None
    
    # stop animation
    def stop_animation(self):
        self.animation_speed = 0
        self.animation_x = self.max_x

# class for a pygame rect area
class RectArea:
    def __init__(self, x, y, width, height):
        self.x = x
        self.y = y
        self.width = width
        self.height = height

    def contains(self, pos):
        return self.x <= pos[0] <= self.x + self.width and self.y <= pos[1] <= self.y + self.height

# class for a pygame textbox
class Textbox:
    def __init__(self, x, y, width, height, default_text, text, font, color):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.area = RectArea(x, y, width, height)
        self.default_text = default_text
        self.text = text
        self.font = font
        self.color = color
        self.active = True
        self.cursor_pos = len(text)

    # resize textbox
    def resize(self, x, y, width, height):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.area = RectArea(x, y, width, height)

    # function that handles the textbox
    def handle_event(self, event):
        if event.type == pygame.KEYDOWN and self.active:
            if event.key == pygame.K_BACKSPACE:
                # remove last character
                if self.cursor_pos > 0:
                    self.text = self.text[:self.cursor_pos - 1] + self.text[self.cursor_pos:]
                    self.cursor_pos -= 1
            elif event.key == pygame.K_RETURN:
                self.active = False
            elif event.key == pygame.K_LEFT:
                # move cursor left if cursor is not at the beginning
                if self.cursor_pos > 0:
                    self.cursor_pos -= 1
            elif event.key == pygame.K_RIGHT:
                # move cursor right if cursor is not at the end
                if self.cursor_pos < len(self.text):
                    self.cursor_pos += 1
            else:
                # check if character is a letter, number, space or symbol
                if event.unicode != "" and (event.unicode in string.ascii_letters or event.unicode in string.digits or event.unicode in string.punctuation or event.unicode in string.whitespace):
                    # add character to text
                    self.text = self.text[:self.cursor_pos] + event.unicode + self.text[self.cursor_pos:]
                    self.cursor_pos += 1

        if event.type == pygame.MOUSEBUTTONDOWN:
            self.active = self.area.contains(event.pos)

            # set cursor position to the position of the mouse
            text1 = self.font.render(self.default_text, True, (0, 0, 0))
            rect1 = text1.get_rect()
            rect1.x = self.x + 30
            rect1.centery = self.y + self.height / 2

            # get how far in the text the mouse is
            self.cursor_pos = len(self.text)
            pos = rect1.right
            for i in range(len(self.text)):
                charSize = self.font.size(self.text[i])[0]
                pos = pos + charSize
                if pos > event.pos[0]:
                    if pos - charSize / 2 > event.pos[0]:
                        self.cursor_pos = i
                    else:
                        self.cursor_pos = i + 1
                    break

        return None

    # function that draws the textbox
    def draw(self, screen):
        # draw grey line under textbox
        pygame.draw.line(screen, (220, 220, 220), (self.x, self.y + self.height), (self.x + self.width, self.y + self.height))

        # draw a circle filled in with self.color before text
        pygame.gfxdraw.filled_circle(screen, int(self.x + 10), int(self.y + self.height / 2), 8, self.color)
        pygame.gfxdraw.aacircle(screen, int(self.x + 10), int(self.y + self.height / 2), 8, (0, 0, 0))

        # draw the text
        text = self.font.render(self.default_text + self.text, True, (0, 0, 0))
        rect = text.get_rect()
        rect.x = self.x + 30
        rect.centery = self.y + self.height / 2
        screen.blit(text, rect)

        # draw cursor at right position if it's active
        text1 = self.font.render(self.default_text + self.text[:self.cursor_pos], True, (0, 0, 0))
        rect1 = text1.get_rect()
        rect1.x = self.x + 30
        rect1.centery = self.y + self.height / 2

        if self.active and time() % 1 < 0.5:
            pygame.draw.line(screen, (0, 0, 0), (rect1.right, rect1.y + 1), (rect1.right, rect1.bottom - 1))

        # draw white rectangle at the end of the text
        pygame.draw.rect(screen, (255, 255, 255), (self.x + self.width, rect.y, 1000, rect.height))

# initialize pygame and the screen with caption "Graph plotter"
pygame.init()
width = 1000
height = 800
screen = pygame.display.set_mode((width, height), pygame.RESIZABLE)
pygame.display.set_caption("Graph plotter")

# set the icon to the icon.png file
icon = pygame.image.load("icon.png")
pygame.display.set_icon(icon)

# create an arial font
small_font = pygame.font.SysFont("Arial", 12)
middle_font = pygame.font.SysFont("Roboto", 26)
big_font = pygame.font.SysFont("Roboto", 58)

# create graph plotter for function
graph_plotter = GraphPlotter(screen, width, height - 80, small_font)

# define graph area and the function textbox
graph_area = RectArea(0, 0, width, height - 80)
textbox = Textbox(20, height - 57, width - 40, 34, "f(x) = ", "", middle_font, graph_plotter.colors[0])
graph_plotter.add_function("")
function_index = 0
function_strs = [""]

# main loop
frames = 0
last_time = time()
clock = pygame.time.Clock()
while True:
    graph_plotter.draw_graphs()

    # draw bar at the bottom of the screen separated by a thin grey line
    pygame.draw.rect(screen, (255, 255, 255), (0, height - 80, width, 80))
    pygame.draw.line(screen, (180, 180, 180), (0, height - 80), (width, height - 80), 1)

    # draw function box and name
    textbox.draw(screen)

    pygame.display.flip()

    for event in pygame.event.get():
        if event.type == pygame.MOUSEBUTTONDOWN:
            # check for mouse wheel event and zoom in or out
            if event.button == 4:
                graph_plotter.zoom_in(event.pos)
            elif event.button == 5:
                graph_plotter.zoom_out(event.pos)

        # if left mouse button is released, set cursor to arrow
        elif event.type == pygame.MOUSEBUTTONUP:
            if event.button == 1:
                pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_ARROW)

        # check for mouse drag event
        elif event.type == pygame.MOUSEMOTION:
            # only drag if mouse is on the graph area
            if event.buttons[0] == 1 and graph_area.contains(event.pos):
                graph_plotter.move(event.rel)

        # if space bar is pressed, start or stop animation
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE and not textbox.active:
                if graph_plotter.animation_speed == 0:
                    graph_plotter.start_animation()
                else:
                    graph_plotter.stop_animation()

            # if down button is pressed, load the next function
            elif event.key == pygame.K_DOWN:
                # only load the next function if limit of functions hasn't been reached
                if function_index < 9:
                    function_index += 1
                    if function_index >= len(graph_plotter.functions):
                        graph_plotter.add_function("")
                        function_strs.append("")

                    # get function name based on index, starting at f, g, h, ...
                    function = graph_plotter.add_missing_brackets(function_strs[function_index])
                    textbox = Textbox(20, height - 57, width - 40, 34, chr(ord('f') + function_index) + "(x) = ", function, middle_font, graph_plotter.colors[function_index])

            # if up button is pressed, load the previous function
            elif event.key == pygame.K_UP:
                # only load the previous function if limit of functions hasn't been reached
                if function_index > 0:
                    function_index -= 1

                    # get function name based on index, starting at f, g, h, ...
                    function = graph_plotter.add_missing_brackets(function_strs[function_index])
                    textbox = Textbox(20, height - 57, width - 40, 34, chr(ord('f') + function_index) + "(x) = ", function, middle_font, graph_plotter.colors[function_index])

        # resize the graph plotter if the window is resized
        elif event.type == pygame.VIDEORESIZE:
            # change screen size
            width, height = event.size
            screen = pygame.display.set_mode((width, height), pygame.RESIZABLE)

            # change graph plotter size
            graph_plotter.resize((width, height - 80))

            # change graph area
            graph_area = RectArea(0, 0, width, height - 80)

            # change textbox position
            textbox.resize(20, height - 57, width - 40, 34)

        if event.type == pygame.QUIT:
            pygame.quit()
            quit()

        # let the textbox handle the event
        textbox.handle_event(event)

    if frames % 10 == 0:
        graph_plotter.replace_function(textbox.text, function_index)
        function_strs[function_index] = textbox.text

    # if the mouse is over the graph area, change the cursor to hand, if it's over the textbox, change the cursor to ibeam, else to arrow
    if graph_area.contains(pygame.mouse.get_pos()):
        pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_HAND)
    elif textbox.area.contains(pygame.mouse.get_pos()):
        pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_IBEAM)
    else:
        pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_ARROW)

    frames += 1
    if time() - last_time > 1:
        print(GraphPlotter.get_value.cache_info())
        print(f"FPS: {int(frames / (time() - last_time))}")
        last_time = time()
        frames = 0

    clock.tick(75)