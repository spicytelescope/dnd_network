import pygame
from pygame.locals import *

class ChatBox:
    def __init__(self, game):
        self.game = game
        self.surface = pygame.Surface((400, 320)).convert()
        self.surface.fill((200, 200, 200))
        self.rect = self.surface.get_rect()
        self.rect.bottomleft = (0, self.game.screen.get_height())
        self.font = pygame.font.Font(None, 24)
        self.log = []
        # self.COLOR_INACTIVE = pygame.Color("lightskyblue3")
        # self.COLOR_ACTIVE = pygame.Color((255, 255, 255))
        # self.active = False
        self.input_box = InputBox(
            self, 0, self.game.screen.get_height() - 64, 400, 32)
        # Position beginning to print the log
        self.y_start = self.game.screen.get_height() - 64 - 32

    def update(self):
        self.input_box.update()

    def draw(self):
        self.game.screen.blit(self.surface, self.rect,
                              special_flags=BLEND_MULT)
        self.print_log()
        self.input_box.draw(self.game.screen)

    def handle_event(self, event):
        active = self.input_box.handle_event(event)
        return active

    def print_log(self):
        # print(self.log)
        x = 5
        y = self.y_start
        sp = max(0, len(self.log) - 8)
        offset = min(self.input_box.camera, sp)
        for i in range(offset, len(self.log)):
            # type(text) == str
            # print(self.log[i])
            if type(self.log[i]) == tuple:
                if self.log[i][0] == "red":
                    txt_surface = self.font.render(self.log[i][1], True, (255, 0, 0))
                if self.log[i][0] == "white":
                    txt_surface = self.font.render(self.log[i][1], True, (255, 255, 255))
                if self.log[i][0] == "green":
                    txt_surface = self.font.render(self.log[i][1], True, (0, 255, 0))
                if self.log[i][0] == "blue":
                    txt_surface = self.font.render(self.log[i][1], True, (0, 0, 255))

            else:
                txt_surface = self.font.render(self.log[i], True, (255, 255, 255))
            self.game.screen.blit(txt_surface, (x, y))
            y -= 25
            if y < self.rect.top:
                break

    def write_log(self, text):
        if type(text) != tuple:
            texts = []
            while len(text) > 41:
                head = text[:41] + '-'
                text = text[41:]
                texts.append(head)
            texts.append(text)
            # print(texts)
            for t in texts:
                self.log.insert(0, t)
        else:
            self.log.insert(0, text)
        self.input_box.camera = 0


class InputBox:

    def __init__(self, chat_box, x, y, w, h, text='Chat here ...'):
        self.chat_box = chat_box
        self.COLOR_INACTIVE = pygame.Color((150, 150, 150))
        self.COLOR_ACTIVE = pygame.Color((255, 255, 255))
        self.FONT = pygame.font.Font(None, 25)
        self.rect = pygame.Rect(x, y, w, h)
        self.color = self.COLOR_INACTIVE
        self.text = text
        self.txt_surface = self.FONT.render(text, True, self.color)
        self.active = False
        self.first = True
        self.camera = 0

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            if self.rect.collidepoint(event.pos):
                self.text = ""
                self.active = not self.active
                if self.first:
                    self.first = False
                    self.text = ''
            else:
                self.active = False
            self.color = self.COLOR_ACTIVE if self.active else self.COLOR_INACTIVE
        if event.type == KEYDOWN:
            if self.active:
                if event.key == K_RETURN:
                    self.chat_box.write_log(self.text)
                    self.text = ''
                    self.camera = 0
                elif event.key == K_BACKSPACE:
                    self.text = self.text[:-1]
                else:
                    self.text += event.unicode
                self.txt_surface = self.FONT.render(
                    self.text, True, self.color)
        if not self.first and not self.active:
            self.text = "Use mouse's wheel to scroll!!!!"
            self.txt_surface = self.FONT.render(
                self.text, True, self.color)
        # Mouse wheel
        if event.type == MOUSEWHEEL:
            pos = pygame.mouse.get_pos()
            if 0 < pos[0] < self.chat_box.surface.get_width() and self.chat_box.game.screen.get_height() > pos[1] > self.chat_box.game.screen.get_height() - self.chat_box.surface.get_height():
                self.camera += event.y
                self.camera = 0 if self.camera < 0 else self.camera

        return self.active

    def update(self):
        pass

    def draw(self, screen):
        screen.blit(self.txt_surface, (self.rect.x+5, self.rect.y+10))
        pygame.draw.rect(screen, self.color, self.rect, 2)