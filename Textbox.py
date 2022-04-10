import pygame, pygame.gfxdraw, string
from time import time
from RectArea import RectArea

# class for a pygame textbox
class Textbox:
    def __init__(self, x, y, width, height, default_text, text, added_text, color):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.area = RectArea(x, y, width, height)
        self.default_text = default_text
        self.added_text = added_text
        self.text = text
        self.font = pygame.font.SysFont("Roboto", 26)
        self.number_font = pygame.font.SysFont("Arial", 18)
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

    # function that handles the textbox and returns whether the textbox was changed
    def handle_event(self, event):
        if event.type == pygame.KEYDOWN and self.active:
            if event.key == pygame.K_BACKSPACE:
                # remove last character
                if self.cursor_pos > 0:
                    self.text = self.text[:self.cursor_pos - 1] + self.text[self.cursor_pos:]
                    self.cursor_pos -= 1

                    return True
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

                    return True

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

        return False

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

        # draw added text in grey
        added_text = self.number_font.render(self.added_text, True, (200, 200, 200))
        added_rect = added_text.get_rect()
        added_rect.x = rect.right + 3
        added_rect.centery = self.y + self.height / 2
        screen.blit(added_text, added_rect)

        # draw cursor at right position if it's active
        text1 = self.font.render(self.default_text + self.text[:self.cursor_pos], True, (0, 0, 0))
        rect1 = text1.get_rect()
        rect1.x = self.x + 30
        rect1.centery = self.y + self.height / 2

        if self.active and time() % 1 < 0.5:
            pygame.draw.line(screen, (0, 0, 0), (rect1.right, rect1.y + 1), (rect1.right, rect1.bottom - 1))

        # draw white rectangle at the end of the text
        pygame.draw.rect(screen, (255, 255, 255), (self.x + self.width, rect.y, 1000, rect.height))