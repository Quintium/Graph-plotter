import pygame
import pygame.gfxdraw
import math
import numpy
from time import time
from Function import Function
from StringUtilities import *

# class for graph plotter
class GraphPlotter:
    # clean function up upon initialization
    def __init__(self, screen, width, height):
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

        # save borders of analysed graph
        self.analysed_min_x = self.min_x
        self.analysed_max_x = self.max_x

        # set animation state
        self.animation_speed = 0
        self.animation_x = self.max_x
        self.last_animation_time = None
        self.reset_timer = None

        self.functions = [Function("") for i in range(10)]

        # define colors list as red, blue, green, orange, cyan, magenta, brown, yellow, purple, gold
        self.colors = [(255, 0, 0), (0, 0, 255), (0, 255, 0), (255, 165, 0), (0, 255, 255),
                       (255, 0, 255), (165, 42, 42), (255, 255, 0), (128, 0, 128), (255, 215, 0)]

        # set font
        self.small_font = pygame.font.SysFont("Arial", 12)
        self.large_font = pygame.font.SysFont("Arial", 16)

        self.special_points = []

    # replace function in list
    def replace_function(self, string, index):
        self.functions[index] = Function(string)

    def map_value(self, value, low1, high1, low2, high2):
        return low2 + (value - low1) * (high2 - low2) / (high1 - low1)

    # function to zoom in
    def zoom_in(self, pos):
        # if zoom limit of 0.00000001 is reached, return
        if (self.max_x - self.min_x) < 0.00000001 or (self.max_y - self.min_y) < 0.00000001:
            return

        self.zoom(pos, -self.zoom_speed * (self.max_x - self.min_x), -
                  self.zoom_speed * (self.max_y - self.min_y))

    # function to zoom out
    def zoom_out(self, pos):
        # if zoom limit of 100000000 is reached, return
        if (self.max_x - self.min_x) > 100000000 or (self.max_y - self.min_y) > 100000000:
            return

        self.zoom(pos, self.zoom_speed * (self.max_x - self.min_x),
                  self.zoom_speed * (self.max_y - self.min_y))

    # function to zoom based on mouse position and total change
    def zoom(self, pos, change_x, change_y):
        # save borders before zoom
        old_min_x = self.min_x
        old_max_x = self.max_x

        # convert mouse position to units
        pos_x = self.map_value(pos[0], 0, self.width, self.min_x, self.max_x)
        pos_y = self.map_value(pos[1], 0, self.height, self.max_y, self.min_y)

        # equation: map_value(pos) in previous zoom = map_value(pos) in new zoom => equation was solved for change in x and y
        min_x_change = (pos_x - self.min_x) * (1 - (self.max_x -
                                                    self.min_x + change_x) / (self.max_x - self.min_x))
        max_x_change = min_x_change + change_x
        min_y_change = (pos_y - self.min_y) * (1 - (self.max_y -
                                                    self.min_y + change_y) / (self.max_y - self.min_y))
        max_y_change = min_y_change + change_y

        # zooming
        self.min_x += min_x_change
        self.max_x += max_x_change
        self.min_y += min_y_change
        self.max_y += max_y_change

        if (self.max_x - self.min_x) * 10 < self.analysed_max_x - self.analysed_min_x or self.max_x - self.min_x > (self.analysed_max_x - self.analysed_min_x) * 10:
            # analyse if a digit of precision was added/removed
            self.analyse_graphs()
        elif change_x > 0:
            # analyse the parts of the graph that were outside the screen
            self.analyse_graphs(self.min_x, old_min_x)
            self.analyse_graphs(old_max_x, self.max_x)

    # move screen
    def move(self, rel):
        # calculate dragged distance to units
        change_x = -self.map_value(rel[0], 0,
                                   self.width, 0, (self.max_x - self.min_x))
        change_y = self.map_value(
            rel[1], 0, self.height, 0, (self.max_y - self.min_y))

        self.min_x += change_x
        self.max_x += change_x
        self.min_y += change_y
        self.max_y += change_y

        # analyse new borders
        if change_x > 0:
            self.analyse_graphs(self.max_x - change_x, self.max_x)
        else:
            self.analyse_graphs(self.min_x, self.min_x - change_x)

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
        for x in numpy.arange(math.ceil(self.min_x / small_grid_unit) * small_grid_unit, self.max_x + limit * 2, small_grid_unit):
            # calculate x value in pixels
            x_pixels = self.map_value(x, self.min_x, self.max_x, 0, self.width)
            pygame.draw.line(self.screen, (245, 245, 245),
                             (x_pixels, 0), (x_pixels, self.height))

        for y in numpy.arange(math.ceil(self.min_y / small_grid_unit) * small_grid_unit, self.max_y + limit * 2, small_grid_unit):
            # calculate y value in pixels
            y_pixels = self.map_value(
                y, self.min_y, self.max_y, self.height, 0)
            pygame.draw.line(self.screen, (245, 245, 245),
                             (0, y_pixels), (self.width, y_pixels))

        # draw grey grid with distance grid_unit
        for x in numpy.arange(math.ceil(self.min_x / grid_unit) * grid_unit, self.max_x + limit * 2, grid_unit):
            # calculate x value in pixels
            x_pixels = self.map_value(x, self.min_x, self.max_x, 0, self.width)
            pygame.draw.line(self.screen, (200, 200, 200),
                             (x_pixels, 0), (x_pixels, self.height))

        for y in numpy.arange(math.ceil(self.min_y / grid_unit) * grid_unit, self.max_y + limit * 2, grid_unit):
            # calculate y value in pixels
            y_pixels = self.map_value(
                y, self.min_y, self.max_y, self.height, 0)
            pygame.draw.line(self.screen, (200, 200, 200),
                             (0, y_pixels), (self.width, y_pixels))

        # draw numbers along the axes
        for x in numpy.arange(math.ceil(self.min_x / grid_unit) * grid_unit, self.max_x + limit * 2, grid_unit):
            if abs(x) > grid_unit / 2:
                text = self.small_font.render(
                    str(int(x)) if power >= 0 else str(round(x, -power)), True, (0, 0, 0))
                text_y = y0_pixels + 1

                # limit text_y to screen
                text_y = max(
                    1, min(text_y, self.height - text.get_height() - 1))
                self.screen.blit(text, (self.map_value(
                    x, self.min_x, self.max_x, 0, self.width) - text.get_width() - 1, text_y))

        for y in numpy.arange(math.ceil(self.min_y / grid_unit) * grid_unit, self.max_y + limit * 2, grid_unit):
            if abs(y) > grid_unit / 2:
                text = self.small_font.render(
                    str(int(y)) if power >= 0 else str(round(y, -power)), True, (0, 0, 0))
                text_x = x0_pixels + 3

                # limit text_x to screen
                text_x = max(1, min(text_x, self.width - text.get_width() - 1))
                self.screen.blit(text, (text_x, self.map_value(
                    y, self.min_y, self.max_y, self.height, 0) - text.get_height() + 1))

        # draw x and y axis
        pygame.draw.line(self.screen, (0, 0, 0),
                         (x0_pixels, 0), (x0_pixels, self.height))
        pygame.draw.line(self.screen, (0, 0, 0),
                         (0, y0_pixels), (self.width, y0_pixels))

    # function that draws the graph
    def draw_function(self, index):
        previousX = None
        previousY = None

        # convert animation x to pixels
        animation_pixels = self.map_value(
            self.animation_x, self.min_x, self.max_x, 0, self.width)

        # draw the graph
        for pixel in numpy.arange(0, animation_pixels, 3):
            # convert pixel to x
            x = self.map_value(pixel, 0, self.width, self.min_x, self.max_x)

            # evaluate the function
            y = self.functions[index].get_value(x)

            if y is not None:
                # map x from -10 to 10 to 0 to screen width
                x = self.map_value(x, self.min_x, self.max_x, 0, self.width)

                # map y from -10 to 10 to 0 to screen height
                y = self.map_value(y, self.max_y, self.min_y, 0, self.height)

                if previousX is not None:
                    # draw line from previous point to current point
                    pygame.draw.line(
                        self.screen, self.colors[index], (previousX, previousY), (x, y), 1)

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
            # draw function if it's valid
            if self.functions[i].is_valid():
                self.draw_function(i)

        # draw special point with most descriptions
        hovered_point = None
        for p in self.special_points:
            # draw point if mouse is hovered close to it
            x = self.map_value(p.x, self.min_x, self.max_x, 0, self.width)
            y = self.map_value(p.y, self.min_y, self.max_y, self.height, 0)
            if abs(x - pygame.mouse.get_pos()[0]) < 12 and abs(y - pygame.mouse.get_pos()[1]) < 12:
                if hovered_point is None:
                    hovered_point = p
                else:
                    if len(p.descriptions) > len(hovered_point.descriptions):
                        hovered_point = p

        if hovered_point is not None:
            # map x and y of point to screen
            x = self.map_value(hovered_point.x, self.min_x,
                               self.max_x, 0, self.width)
            y = self.map_value(hovered_point.y, self.min_y,
                               self.max_y, self.height, 0)

            # draw circle with inside color of function
            pygame.draw.circle(
                self.screen, self.colors[hovered_point.index], (x, y), 7)
            pygame.gfxdraw.aacircle(self.screen, int(x), int(y), 7, (0, 0, 0))

            # draw white rectangle with grey border below the point with all information

            # render point coordinates as text
            coordinates = self.large_font.render(
                "(" + str(hovered_point.x) + ", " + str(hovered_point.y) + ")", True, (0, 0, 0))

            # render descriptions as text
            descriptions = [self.large_font.render(
                desc, True, (0, 0, 0)) for desc in hovered_point.descriptions]

            # calculate width and height of rect
            width = 4 + max([coordinates.get_width()] +
                            [desc.get_width() for desc in descriptions]) + 4
            height = 3 + coordinates.get_height() + 3 + \
                sum([desc.get_height() for desc in descriptions]) + 3

            pygame.draw.rect(self.screen, (255, 255, 255),
                             (x - width / 2, y + 10, width, height))
            pygame.draw.rect(self.screen, (200, 200, 200),
                             (x - width / 2, y + 10, width, height), 1)

            self.screen.blit(
                coordinates, (x - coordinates.get_width() / 2, y + 13))
            cur_y = y + 13 + coordinates.get_height() + 3
            for desc in descriptions:
                self.screen.blit(desc, (x - desc.get_width() / 2, cur_y))
                cur_y += desc.get_height()

        # handle the animation state
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
                self.animation_x += self.map_value(self.animation_speed * self.width / 1000 * (
                    time() - self.last_animation_time), 0, self.width, 0, (self.max_x - self.min_x))
                self.last_animation_time = time()

    # start animation
    def start_animation(self):
        self.animation_speed = 200  # measured in 0.1% of the screen width per second
        self.animation_x = self.min_x
        self.reset_timer = None
        self.last_animation_time = time()

    # stop animation
    def stop_animation(self):
        self.animation_speed = 0
        self.animation_x = self.max_x

    # print cache info of every function
    def print_cache_info(self):
        for f in self.functions:
            if f.is_valid():
                f.print_cache_info()

    # function that analyses all graphs for zeros, maximums, minimums and intersecitons
    def analyse_graphs(self, start = None, end = None):
        # if start and end are not set, set them to the whole graph
        if start is None:
            start = self.min_x
            end = self.max_x
            self.special_points = []

            # save analysed borders
            self.analysed_min_x = self.min_x
            self.analysed_max_x = self.max_x

        # save last 2 values of each function
        last_values = []
        last2_values = []

        # save last special points
        last_special_points = []

        # sensitivity for root finding
        sensitivity = 100000

        # loop through x-values
        step_size = (self.max_x - self.min_x) / 100

        # first run is a test run to test for equal functions -> infinite intersections; or zero functions -> infinite zeros
        test_run = True

        for x in numpy.arange(start - step_size, end, step_size):
            new_values = [f.get_value(x) for f in self.functions]
            new_special_points = []

            for i in range(len(new_values)):
                if new_values[i] is None:
                    continue

                if new_values[i] == 0:
                    # add zero if exactly 0
                    if not test_run:
                        self.add_special_point(
                            x, i, "Zero", step_size / sensitivity * 2, last_special_points)
                    new_special_points.append([i, "Zero"])
                elif len(last_values) > 0 and last_values[i] is not None:
                    # check if last value an new value have different signs
                    if new_values[i] > 0 and last_values[i] < 0 or new_values[i] < 0 and last_values[i] > 0:
                        # root finding algorithm to find zeros -> bisection method
                        step = step_size / 4
                        midpoint = x - step_size / 2
                        broken = False
                        while step > step_size / sensitivity:
                            value = self.functions[i].get_value(midpoint)
                            if value is None:
                                broken = True
                                break
                            elif value == 0:
                                break
                            elif numpy.sign(value) == numpy.sign(last_values[i]):
                                midpoint += step
                                step /= 2
                            else:
                                midpoint -= step
                                step /= 2

                        # add zero if found
                        if not broken:
                            if not test_run:
                                self.add_special_point(
                                    midpoint, i, "Zero", step_size / sensitivity * 2, last_special_points)
                            new_special_points.append([i, "Zero"])

                # search for intersections
                for j in range(i + 1, len(new_values)):
                    if new_values[j] is None:
                        continue

                    if new_values[i] == new_values[j]:
                        if not test_run:
                            self.add_special_point(
                                x, i, "Intersection", step_size / sensitivity * 2, last_special_points)
                        new_special_points.append([i, "Intersection"])
                        if not test_run:
                            self.add_special_point(
                                x, j, "Intersection", step_size / sensitivity * 2, last_special_points)
                        new_special_points.append([j, "Intersection"])
                    elif len(last_values) > 0 and last_values[i] is not None and last_values[j] is not None:
                        if numpy.sign(new_values[i] - new_values[j]) != numpy.sign(last_values[i] - last_values[j]):
                            # root finding algorithm to find intersections
                            step = step_size / 4
                            midpoint = x - step_size / 2
                            broken = False
                            while step > step_size / sensitivity:
                                iValue = self.functions[i].get_value(midpoint)
                                jValue = self.functions[j].get_value(midpoint)
                                if iValue is None or jValue is None:
                                    broken = True
                                    break
                                elif iValue == jValue:
                                    break
                                elif numpy.sign(iValue - jValue) == numpy.sign(last_values[i] - last_values[j]):
                                    midpoint += step
                                    step /= 2
                                else:
                                    midpoint -= step
                                    step /= 2
                            if not broken:
                                if not test_run:
                                    self.add_special_point(
                                        midpoint, i, "Intersection", step_size / sensitivity * 2, last_special_points)
                                new_special_points.append([i, "Intersection"])
                                if not test_run:
                                    self.add_special_point(
                                        midpoint, j, "Intersection", step_size / sensitivity * 2, last_special_points)
                                new_special_points.append([j, "Intersection"])

                # check for maximums and minimums
                if len(last_values) > 0 and len(last2_values) > 0:
                    for i in range(len(new_values)):
                        if new_values[i] is None or last_values[i] is None or last2_values[i] is None:
                            continue

                        # check for maximums or minimums
                        if last_values[i] > last2_values[i] and last_values[i] > new_values[i] or last_values[i] < last2_values[i] and last_values[i] < new_values[i]:
                            # save whether it's a maximum or minimum
                            sign = numpy.sign(last_values[i] - last2_values[i])

                            # golden ratio and bounds
                            gr = (1 + math.sqrt(5)) / 2
                            a = x - 2 * step_size
                            b = x

                            # find maximum by golden-section search, inaccuracies because of missing precision
                            broken = False
                            while b - a > step_size / sensitivity and not broken:
                                # so that (b - c) / (c - a) = gr
                                c = (gr * a + b) / (1 + gr)
                                cy = self.functions[i].get_value(c)
                                if cy is None:
                                    continue

                                d = a + b - c
                                dy = self.functions[i].get_value(d)
                                if dy is None:
                                    broken = True

                                if numpy.sign(dy - cy) == 0:
                                    break
                                elif numpy.sign(dy - cy) == sign:
                                    a = c
                                else:
                                    b = d

                            if not broken:
                                extr_x = (a + b) / 2
                                extr_y = self.functions[i].get_value(extr_x)

                                # save extremum
                                if sign == 1:
                                    if not test_run:
                                        self.add_special_point(
                                            extr_x, i, "Maximum", step_size / sensitivity * 2, last_special_points)
                                    new_special_points.append([i, "Maximum"])
                                else:
                                    if not test_run:
                                        self.add_special_point(
                                            extr_x, i, "Minimum", step_size / sensitivity * 2, last_special_points)
                                    new_special_points.append([i, "Minimum"])

                                # if value is close enough to zero, save it as a zero
                                if abs(extr_y) < step_size / sensitivity * 100:
                                    if not test_run:
                                        self.add_special_point(
                                            extr_x, i, "Zero", step_size / sensitivity * 2, last_special_points)
                                    new_special_points.append([i, "Zero"])

                                # if value is close enough to another value, save it as an intersection
                                for j in range(len(new_values)):
                                    if i == j:
                                        continue
                                    valueJ = self.functions[j].get_value(
                                        extr_x)
                                    if valueJ is None:
                                        continue
                                    if abs(extr_y - valueJ) < step_size / sensitivity * 100:
                                        if not test_run:
                                            self.add_special_point(
                                                extr_x, i, "Intersection", step_size / sensitivity * 2, last_special_points)
                                        new_special_points.append(
                                            [i, "Intersection"])
                                        if not test_run:
                                            self.add_special_point(
                                                extr_x, j, "Intersection", step_size / sensitivity * 2, last_special_points)
                                        new_special_points.append(
                                            [j, "Intersection"])

            last2_values = last_values
            last_values = new_values
            last_special_points = new_special_points
            test_run = False

        # check for y-intercepts
        for i in range(len(self.functions)):
            if self.functions[i].get_value(0) is not None:
                self.add_special_point(
                    0, i, "Y-Intercept", step_size / sensitivity * 2, [])

    # add special point to list
    def add_special_point(self, x, index, description, sensitivity, last_special_points):
        # check if point is already in list
        for p in last_special_points:
            if p[0] == index and p[1] == description:
                return

        # round x to two digits above sensitivity
        x = round(x, -math.ceil(math.log10(sensitivity)) - 1)

        for p in self.special_points:
            if p.add_point(x, index, description):
                return

        if description == "Zero":
            y = 0
        else:
            y = round(self.functions[index].get_value(
                x), -math.ceil(math.log10(sensitivity)) - 1)

        self.special_points.append(Point(x, y, index, description))

    # evaluate function as string without x
    def evaluate_function_as_string(self, index):
        value = self.functions[index].value
        if value is None:
            return ""
        else:
            # round value to 10 digits
            return " = " + str(round(value, 10))

    # return simplified function
    def get_simplified_function(self, index):
        return self.functions[index].string

    # return if function index is valid
    def is_valid_function(self, index):
        return self.functions[index].is_valid()

# class for points
class Point:
    def __init__(self, x, y, index, description):
        # convert -0 to 0
        self.x = x if x != 0 else 0
        self.y = y if y != 0 else 0
        self.index = index
        self.descriptions = [description]

    # add point to point if same x values
    def add_point(self, x, index, description):
        # check if point has same x value
        if index == self.index and x == self.x:
            # insert description alphabetically
            if description not in self.descriptions:
                added = False
                for i in range(len(self.descriptions)):
                    if description < self.descriptions[i]:
                        self.descriptions.insert(i, description)
                        added = True
                        break
                if not added:
                    self.descriptions.append(description)
            
            return True
        return False
