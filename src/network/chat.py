import math
import pygame as pg
from pygame.constants import *
from config.netConf import *
from utils.Network_helpers import *
from copy import deepcopy
from .packet_types import *
from utils.utils import logger


def formatDialogContent(string, charLimit=CHAR_LIMIT_DEFAULT) -> list:
    """Cut a string of words into substrings of words that doesn't exceeds <charLimit>."""

    stringList = string.split(" ")
    resetMax = math.ceil(len(string) / charLimit)
    resets = 0
    charCount = 0
    resultList = []
    tmpList = []

    for word in stringList:
        charCount += len(word)
        if (charCount + len(tmpList)) >= charLimit:
            resultList.append((" ").join(tmpList))
            charCount = len(word)
            tmpList = []
            resets += 1
        tmpList.append(word)

    if resets != resetMax:
        resultList.append((" ").join(tmpList))

    return resultList


class ChatWindow:
    def __init__(self, gameController, Hero) -> None:

        self.Game = gameController

        # ------------------ TEXTURES ---------- #

        self.surf = pg.Surface(CHAT_WINDOW_DIM, SRCALPHA)
        self.rect = self.surf.get_rect(topright=(1024, 0))

        # ---------------- FIGHT ATTR ------------- #

        self.turn = 0
        self.text = [
            ("Jordan", "just joined the chat !", CHAT_COLORS["CONNEXION"], True),
            WELCOME_MESSAGE,
        ]
        self.textSurf = None
        self.textRect = None

        # self.addTurn()
        self.updateTextSurf()

    def process_command(self):

        current_line = self.text[-1][1]
        if current_line == "/clear":
            self.text = []
        elif current_line == "/help":
            self.addText(
                "",
                "Commands : /clear -> clear the window ; /mp {p_name} -> send a private message to {p_name}",
                True,
            )

    def updateTextSurf(self, received = False):

        if not received:
            self.process_command()

        self.textSurf = pg.Surface(
            (self.rect.width, len(self.text) * VERTICAL_SPACING), SRCALPHA
        )
        self.textRect = self.textSurf.get_rect()

        for i, (sender_name, text, color, italic) in enumerate(self.text):
            font = pg.font.SysFont("dejavusansmono", CHAT_FONT_SIZE)
            font.italic = italic
            self.textSurf.blit(
                font.render(
                    f"{sender_name} : {text}"
                    if not italic
                    else f">>> {sender_name} {text}",
                    True,
                    color,
                ),
                (0, i * VERTICAL_SPACING),
            )

        self.textRect.bottom = self.rect.height

    def addText(self, sender_name, text, italic=False, color_code="DEFAULT", send=False, recv=False):

        textList = []
        textList += formatDialogContent(text)
        fTextList = []
        for text in textList:
            if send:
                msg_packet = deepcopy(TEMPLATE_MESSAGE)
                msg_packet["sender_id"] = self.Game.networkController.Hero.networkId
                msg_packet["content"] = text
                msg_packet["color_code"] = CHAT_COLORS[color_code]
                msg_packet["italic"] = italic
                write_to_pipe(IPC_FIFO_OUTPUT, msg_packet)

            fTextList.append((sender_name, text, CHAT_COLORS[color_code], italic))

        self.text += fTextList
        self.updateTextSurf(received=recv)

    def reset(self):

        self.text = []

    def show(self):
        self.surf.fill((0, 0, 0, 127))
        self.surf.blit(self.textSurf, self.textRect)
        self.Game.screen.blit(self.surf, self.rect)

    def update(self, event):

        if event.type == pg.QUIT:
            pg.quit()
            exit()

        # if event.type == KEYDOWN:
        #     if event.key == K_SPACE:
        #         self.addTurn()
        #     if event.key == K_t:
        #         self.addText(str(input("Enter your action : ")))

        if event.type == MOUSEBUTTONDOWN:

            if event.button == 4 and self.textRect.top <= 0:
                self.textRect.topleft = [
                    self.textRect.topleft[0],
                    self.textRect.topleft[1] + SCROLL_VALUE,
                ]

            if event.button == 5 and self.textRect.bottom >= self.rect.height:
                self.textRect.topleft = [
                    self.textRect.topleft[0],
                    self.textRect.topleft[1] - SCROLL_VALUE,
                ]


class Chat(object):
    def __init__(self):
        self.chatWindow = ChatWindow()
        self.name = "Jordan"
        self.input = TextBox(
            pg.Surface(CHAT_TEXTBOX_DIM).get_rect(
                center=(
                    self.chatWindow.rect.topleft[0] + self.chatWindow.rect.width // 2,
                    self.chatWindow.rect.height + CHAT_TEXTBOX_DIM[1] // 2,
                )
            ),
            command=self.add_text_to_chatWindow,
            clear_on_enter=True,
            inactive_on_enter=False,
        )
        self.color = (100, 100, 100)
        pg.key.set_repeat(*KEY_REPEAT_SETTING)

    def add_text_to_chatWindow(self, text):
        self.chatWindow.addText(self.name, ("").join(text), send=True)

    def checkEvent(self, event):
        self.input.get_event(event)

    def show(self, surface):
        self.chatWindow.show()
        self.input.update()
        self.input.draw(surface)

    def reset(self):
        self.input.buffer = []


class TextBox(object):
    def __init__(self, rect, **kwargs):
        self.rect = pg.Rect(rect)
        self.buffer = []
        self.final = None
        self.rendered = None
        self.render_rect = None
        self.render_area = None
        self.blink = True
        self.blink_timer = 0.0
        self.process_kwargs(kwargs)

    def process_kwargs(self, kwargs):
        defaults = {
            "id": None,
            "command": None,
            "active": True,
            "color": pg.Color("white"),
            "font_color": pg.Color("black"),
            "outline_color": pg.Color("black"),
            "outline_width": 2,
            "active_color": pg.Color("red"),
            "font": pg.font.Font(None, self.rect.height - 10),
            "clear_on_enter": False,
            "inactive_on_enter": True,
        }
        for kwarg in kwargs:
            if kwarg in defaults:
                defaults[kwarg] = kwargs[kwarg]
            else:
                raise KeyError("InputBox accepts no keyword {}.".format(kwarg))
        self.__dict__.update(defaults)

    def get_event(self, event):
        if event.type == pg.KEYDOWN and self.active:
            if event.key == pg.K_BACKSPACE:
                if self.buffer:
                    self.buffer.pop()
            elif event.unicode in ACCEPTED:
                self.buffer.append(event.unicode)
            elif event.key == pg.K_RETURN:
                self.command(self.buffer)
                if self.clear_on_enter:
                    self.buffer = []
                self.active = not self.inactive_on_enter
        elif event.type == pg.MOUSEBUTTONDOWN and event.button == 1:
            self.active = self.rect.collidepoint(event.pos)

    def execute(self):
        if self.command:
            self.command(self.buffer)
        self.active = not self.inactive_on_enter
        if self.clear_on_enter:
            self.buffer = []

    def update(self):
        new = "".join(self.buffer)
        if new != self.final:
            self.final = new
            self.rendered = self.font.render(self.final, True, self.font_color)
            self.render_rect = self.rendered.get_rect(
                x=self.rect.x + 2, centery=self.rect.centery
            )
            if self.render_rect.width > self.rect.width - 6:
                offset = self.render_rect.width - (self.rect.width - 6)
                self.render_area = pg.Rect(
                    offset, 0, self.rect.width - 6, self.render_rect.height
                )
            else:
                self.render_area = self.rendered.get_rect(topleft=(0, 0))
        if pg.time.get_ticks() - self.blink_timer > BLINK_TIME_OUT:
            self.blink = not self.blink
            self.blink_timer = pg.time.get_ticks()

    def draw(self, surface):
        outline_color = self.active_color if self.active else self.outline_color
        outline = self.rect.inflate(self.outline_width * 2, self.outline_width * 2)
        surface.fill(outline_color, outline)
        surface.fill(self.color, self.rect)
        if self.rendered:
            surface.blit(self.rendered, self.render_rect, self.render_area)
        if self.blink and self.active:
            curse = self.render_area.copy()
            curse.topleft = self.render_rect.topleft
            surface.fill(self.font_color, (curse.right + 1, curse.y, 2, curse.h))
