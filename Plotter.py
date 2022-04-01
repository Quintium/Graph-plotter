# Pygame graph plotter that plots a function given by the user from x = -10 to x = 10 and y = -10 to y = 10 and an increment of 0.005.
# The function is given as a string and can contain any mathematical expression with x as a variable.
# The grid is drawn every 2 units of x and y.

import pygame, numpy
from math import *

def map_value(value, low1, high1, low2, high2):
    return low2 + (value - low1) * (high2 - low2) / (high1 - low1)

def draw_grid():
    # fill screen white
    screen.fill((255, 255, 255))

    # draw a grid  with distance of 50 pixels
    for x in numpy.arange(0, screen_width, screen_width / 10):
        pygame.draw.line(screen, (200, 200, 200), (x, 0), (x, screen_height))
    for y in numpy.arange(0, screen_height, screen_height / 10):
        pygame.draw.line(screen, (200, 200, 200), (0, y), (screen_width, y))

    # draw numbers along the axes
    for i in range(-10, 10, 2):
        x = map_value(i, -10, 10, 0, screen_width)
        y = map_value(i, -10, 10, screen_height, 0)

        text = small_font.render(str(i), True, (0, 0, 0))
        screen.blit(text, (x - text.get_width() - 1, screen_height / 2 + 1))
        screen.blit(text, (screen_width / 2 + text.get_width() - 2, y - text.get_height() + 1))

    # draw x and y axis
    pygame.draw.line(screen, (0, 0, 0), (0, screen_height / 2), (screen_width, screen_height / 2))
    pygame.draw.line(screen, (0, 0, 0), (screen_width / 2, 0), (screen_width / 2, screen_height))


def draw_function():
    previousX = None
    previousY = None

    # draw the graph
    for x in numpy.arange(-10, 10, 0.005):
        expression = function

        # replace all indices in the expression backwards with the x-value
        for i in indices:
            expression = expression[:i] + "(" + str(x) + ")" + expression[i + 1:]

        # evaluate the function
        try:
            y = eval(expression)

            # map x from -10 to 10 to 0 to screen_width
            x = map_value(x, -10, 10, 0, screen_width)

            # map y from -10 to 10 to 0 to screen_height
            y = map_value(y, 10, -10, 0, screen_height)

            if previousX is not None:
                pygame.draw.line(screen, (255, 0, 0), (previousX, previousY), (x, y))

            # save previous x and y
            previousX = x
            previousY = y
        except:
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
    draw_grid()
    text = big_font.render("Choose a function:", True, (0, 0, 0))
    input_text = middle_font.render(function, True, (0, 0, 0))

    # draw a white rectangle with the text in the middle
    rect = pygame.Rect(0, 0, max(text.get_width(), input_text.get_width()), text.get_height() + input_text.get_height())
    rect.center = (screen_width / 2, screen_height / 2)
    pygame.draw.rect(screen, (255, 255, 255), rect)
    screen.blit(text, (screen_width / 2 - text.get_width() / 2, rect.y))
    screen.blit(input_text, (screen_width / 2 - input_text.get_width() / 2, rect.y + text.get_height()))

    pygame.display.update()

# replace ^ in the function with **
function = function.replace("^", "**")

# strip function of whitespace
function = function.strip()

# strip function of f(x)=, g(x)= ...
if ("=" in function):
    function = function[function.index("=") + 1:]

indices = []
# loop through function backwards
for i in range(len(function) - 1, -1, -1):
    # check if the character is a x between two non letters
    if function[i] == "x" and (i - 1 < 0 or not function[i - 1].isalpha()) and (i + 1 > len(function) - 1 or not function[i+1].isalpha()):
        # if so, add the index to the list
        indices.append(i)

# main loop
while True:
    draw_grid()
    draw_function()