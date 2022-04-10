# Pygame graph plotter that plots a function given by the user
# There's an option to animate the graph, the zoom can be controlled by the mouse wheel and the screen can be dragged around.
# The function is given as a string and can contain any mathematical function with x as a variable.
# Python expressions as well as integrals and derivatives are supported via integrate() and diff() functions.
# The grid is drawn every 2 units of x and y.
# The graph can be animated by pressing the spacebar.
# The function can be changed in the bar at the bottom.

import pygame
from time import time
from RectArea import RectArea
from Textbox import Textbox
from GraphPlotter import GraphPlotter

# function to add missing brackets
def add_missing_brackets(function):
    # check if function has missing brackets
    brackets = function.count("(") - function.count(")")

    # if there are missing brackets, add them
    if brackets > 0:
        function += ")" * brackets

    return function

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
middle_font = pygame.font.SysFont("Roboto", 26)

# create graph plotter for function
graph_plotter = GraphPlotter(screen, width, height - 80)

# define graph area and the function textbox
graph_area = RectArea(0, 0, width, height - 80)
textbox = Textbox(20, height - 57, width - 40, 34, "f(x) = ", "", middle_font, graph_plotter.colors[0])
graph_plotter.add_function("")
function_index = 0
function_strs = [""]

# main loop
frames = 0
last_time = time()
last_analysis = time()
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
                    function = add_missing_brackets(function_strs[function_index])
                    textbox = Textbox(20, height - 57, width - 40, 34, chr(ord('f') + function_index) + "(x) = ", function, middle_font, graph_plotter.colors[function_index])

            # if up button is pressed, load the previous function
            elif event.key == pygame.K_UP:
                # only load the previous function if limit of functions hasn't been reached
                if function_index > 0:
                    function_index -= 1

                    # get function name based on index, starting at f, g, h, ...
                    function = add_missing_brackets(function_strs[function_index])
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

        # let the textbox handle the event and refresh functions if changed
        if textbox.handle_event(event):
            graph_plotter.replace_function(textbox.text, function_index)
            function_strs[function_index] = textbox.text
            graph_plotter.analyse_graphs()

    # if the mouse is over the graph area, change the cursor to hand, if it's over the textbox, change the cursor to ibeam, else to arrow
    if graph_area.contains(pygame.mouse.get_pos()):
        pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_HAND)
    elif textbox.area.contains(pygame.mouse.get_pos()):
        pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_IBEAM)
    else:
        pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_ARROW)

    # update the frames and time, output log
    frames += 1
    if time() - last_time > 1:
        graph_plotter.print_cache_info()
        print(f"FPS: {int(frames / (time() - last_time))}")
        print()
        last_time = time()
        frames = 0

    # analyse graphs if enough time has passed
    if time() - last_analysis > 0.5:
        graph_plotter.analyse_graphs()
        last_analysis = time()

    clock.tick(75)