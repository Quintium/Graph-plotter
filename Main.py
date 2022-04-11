# Pygame graph plotter that plots a function given by the user
# There's an option to animate the graph, the zoom can be controlled by the mouse wheel and the screen can be dragged around.
# The function is given as a string and can contain any mathematical function with x as a variable.
# Python expressions as well as integrals and derivatives are supported via integrate() and diff() functions.
# The grid is drawn every 2 units of x and y.
# The graph can be animated by pressing the spacebar.
# The function can be changed in the bar at the bottom.
# Function can reference other functions.
# The graphs are analysed: intersections, zeros, y-intersects, minimums and maximums.
# The graph can be saved as a file using the s key.

import pygame
import datetime
from time import time
from RectArea import RectArea
from Textbox import Textbox
from GraphPlotter import GraphPlotter
from StringUtilities import add_missing_brackets, is_standalone, char_exists, char_equals

# function that updates a function
def update_function(index, text):
    function = add_missing_brackets(text)

    # replace references to other functions with their values1
    for i in range(len(function) - 1, -1, -1):
        function_no = ord(function[i]) - ord('f')
        if 0 <= function_no < 10 and is_standalone(function, i) and char_equals(function, i + 1, "("):
            # check for recursion (if the function is dependent on itself in some way)
            paths = dependency_paths(index, function_no)
            for p in paths:
                for f in p:
                    graph_plotter.replace_function("Error", f)
            if len(paths) > 0:
                return

            # get the text inside the function brackets
            num_brackets = 1
            for j in range(i + 2, len(function)):
                if function[j] == "(":
                    num_brackets += 1
                elif function[j] == ")":
                    num_brackets -= 1
                    if num_brackets == 0:
                        break

            if num_brackets == 0 and j != i + 2:
                # save the dependency
                if index not in depending_functions[function_no]:
                    depending_functions[function_no].append(index)

                if not graph_plotter.is_valid_function(function_no):
                    # if invalid function, replace with error message
                    function = "Error"
                else:
                    # pass the input inside the referenced function
                    function_input = "(" + function[i + 2: j] + ")"
                    inserted_function = graph_plotter.get_simplified_function(
                        function_no)
                    for k in range(len(inserted_function) - 1, -1, -1):
                        if inserted_function[k] == "x" and is_standalone(inserted_function, k):
                            inserted_function = inserted_function[:k] + \
                                function_input + inserted_function[k + 1:]

                    # replace the function with the new one
                    function = function[:i] + \
                        "(" + inserted_function + ")" + function[j + 1:]

    graph_plotter.replace_function(function, index)

    # update the depending functions
    for f in depending_functions[index]:
        update_function(f, function_strs[f])

# function that checks if there's a dependency path from function a to function b, returns all possible paths
def dependency_paths(a, b, avoid_functions=[]):
    if a == b:
        # trivial case of recursive function
        return [[a]]
    else:
        # check if there's a dependency path from any depending functions to b
        paths = []
        for f in depending_functions[a]:
            if f not in avoid_functions:
                new_paths = dependency_paths(f, b, avoid_functions + [a])
                for p in new_paths:
                    paths.append([a] + p)
            else:
                if f == b:
                    paths.append([a, f])
        return paths


# initialize pygame and the screen with caption "Graph plotter"
pygame.init()
width = 1000
height = 800
screen = pygame.display.set_mode((width, height), pygame.RESIZABLE)
pygame.display.set_caption("Graph plotter")

# set the icon to the icon.png file
icon = pygame.image.load("icon.png")
pygame.display.set_icon(icon)

# create graph plotter for function
graph_plotter = GraphPlotter(screen, width, height - 80)

# define graph area and the function textbox
graph_area = RectArea(0, 0, width, height - 80)
textbox = Textbox(20, height - 57, width - 40, 34, "f(x) = ",
                  "", "", graph_plotter.colors[0], False)
function_index = 0
function_strs = ["" for x in range(10)]

# define functions that are referenced by each other
depending_functions = [[] for x in range(10)]

# main loop
frames = 0
last_time = time()
clock = pygame.time.Clock()
while True:
    graph_plotter.draw_graphs()

    # draw bar at the bottom of the screen separated by a thin grey line
    pygame.draw.rect(screen, (255, 255, 255), (0, height - 80, width, 80))
    pygame.draw.line(screen, (180, 180, 180),
                     (0, height - 80), (width, height - 80), 1)

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

            # if s is pressed, save the current graph to a file
            elif event.key == pygame.K_s and not textbox.active:
                pygame.image.save(screen, "Screenshots/Screenshot_" +
                                  datetime.datetime.now().strftime(r"%d_%m_%Y_%H_%M_%S") + ".png")

            # if down button is pressed, load the next function
            elif event.key == pygame.K_DOWN:
                # only load the next function if limit of functions hasn't been reached
                if function_index < 9:
                    function_index += 1

                    # get function name based on index, starting at f, g, h, ...
                    function = add_missing_brackets(
                        function_strs[function_index])
                    textbox = Textbox(20, height - 57, width - 40, 34, chr(ord('f') + function_index) + "(x) = ", function, graph_plotter.evaluate_function_as_string(
                        function_index), graph_plotter.colors[function_index], graph_plotter.is_valid_function(function_index))

            # if up button is pressed, load the previous function
            elif event.key == pygame.K_UP:
                # only load the previous function if limit of functions hasn't been reached
                if function_index > 0:
                    function_index -= 1

                    # get function name based on index, starting at f, g, h, ...
                    function = add_missing_brackets(
                        function_strs[function_index])
                    textbox = Textbox(20, height - 57, width - 40, 34, chr(ord('f') + function_index) + "(x) = ", function, graph_plotter.evaluate_function_as_string(
                        function_index), graph_plotter.colors[function_index], graph_plotter.is_valid_function(function_index))

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
            update_function(function_index, textbox.text)

            function_strs[function_index] = textbox.text
            graph_plotter.analyse_graphs()

            # if function is a constant, pass it to textbox
            textbox.added_text = graph_plotter.evaluate_function_as_string(
                function_index)

            # pass validness of function to textbox
            textbox.is_valid = graph_plotter.is_valid_function(function_index)

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

    clock.tick(75)
