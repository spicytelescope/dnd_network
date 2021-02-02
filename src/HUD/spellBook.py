import math
from time import *

import pygame
from config import playerConf
from config.menuConf import *
from config.playerConf import *
from config.spellsConf import *
import config.spellsConf as spellsConf
from config.UIConf import *
from UI.UI_utils_text import *


class SpellBook:
    """ Book displaying 3 spells per pages, spells unblocked by the player's level"""

    def __init__(self, gameController, Hero):

        self.Game = gameController
        self.Hero = Hero

        self.open = False

        self.MAX_PAGE = None
        self.MAX_PAGE_INDEX = None
        self.pageIndex = 0  # is an index so starts at one

        # ANIMATIONS

        self.openAnimFrames = [
            pygame.transform.scale(img, (self.Game.resolution, self.Game.resolution))
            for img in spellsConf.OPEN_ANIM_FRAMES
        ]
        self.closeAnimFrames = [
            pygame.transform.scale(img, (self.Game.resolution, self.Game.resolution))
            for img in spellsConf.CLOSE_ANIM_FRAMES
        ]
        self.nextAnimFrames = [
            pygame.transform.scale(img, (self.Game.resolution, self.Game.resolution))
            for img in spellsConf.NEXT_ANIM_FRAMES
        ]
        self.backAnimFrames = [
            pygame.transform.scale(img, (self.Game.resolution, self.Game.resolution))
            for img in spellsConf.BACK_ANIM_FRAMES
        ]

        # STATIC SURF

        self.bg = None

        self.blankPage = pygame.transform.scale(
            spellsConf.SPELLBOOK_MAIN_SURF, (self.Game.resolution, self.Game.resolution)
        )
        self.mainSurf = self.blankPage.copy()
        self.rect = self.openAnimFrames[0].get_rect(
            center=(self.Game.resolution // 2, self.Game.resolution // 2)
        )

        # BUTTONS

        self.buttons = spellsConf.SPELLBOOK_BUTTONS
        for button in self.buttons:
            self.buttons[button]["rect"] = self.buttons[button]["surf"].get_rect(
                center=tuple(self.buttons[button]["blitPoint"])
            )

        # SPELLS INFORMATIONS

        self.animTitle = pygame.font.Font(
            DUNGEON_FONT, int(BUTTON_FONT_SIZE * 2)
        ).render(f"~ ANIMATION ~", True, (0, 0, 0))
        self.animTitleRect = self.animTitle.get_rect(center=TITLE_CENTER_POINT_RIGHT)

        self.classNameTitle = pygame.font.Font(
            DUNGEON_FONT, int(BUTTON_FONT_SIZE * 2)
        ).render(
            f"~ {playerConf.CLASSES[self.Hero.classId]['name']} ~", True, (0, 0, 0)
        )
        self.classNameTitleRect = self.classNameTitle.get_rect(
            center=TITLE_CENTER_POINT_LEFT
        )

        self.spellsSurfInfos = []
        self.spellsRectInfos = []
        self.spellsDesc = []
        self.spellAnims = []
        self.spells = []

        self.descSlot = pygame.Surface(SPELL_DESC_SURF_DIM, pygame.SRCALPHA)
        self.descSlot.fill((0, 0, 0, 127))

        self.descSlotRect = self.descSlot.get_rect(center=SPELL_DESC_CENTER)

    def updateSpellBook(self):
        """Method used to review all the spells availables by the player and display them"""
        count = 0

        self.spellsSurfInfos = []
        self.spellsRectInfos = []
        self.spellsDesc = []
        self.spellAnims = []
        self.spells = []

        self.MAX_PAGE = math.ceil(len(self.Hero.spellsID) / 3)
        self.MAX_PAGE_INDEX = self.MAX_PAGE - 1
        self.pageIndex = 0

        for spellId in self.Hero.spellsID:

            spell = spellsConf.SPELL_DB[spellId]
            spell.loadTextures()
            spell.animationFrames = [
                pygame.transform.scale(elt, SPELL_ANIMATION_DIM)
                for elt in spell.animationFrames
            ]

            spellInfoSurf = pygame.Surface(SPELL_INFO_SURF_DIM).convert_alpha()
            spellInfoSurf.fill((0, 0, 0, 0))
            spellInfoRect = spellInfoSurf.get_rect(
                topleft=(
                    SPELL_INFO_INIT_POINT[0],
                    SPELL_INFO_INIT_POINT[1] + SPELL_INFO_SURF_DIM[1] * count,
                )
            )

            # Fonts
            nameFont = pygame.font.Font(DUNGEON_FONT, SPELL_NAME_FONT_SIZE).render(
                f"{spell.name} (lvl {spell.lvl})", True, (0, 0, 0)
            )
            nameFontRect = nameFont.get_rect(center=SPELL_LEVEL_NAME_CENTER)

            descText = ScrollText(
                self.descSlot, f"{spell.desc} ({spell.effect})", 5, (0, 0, 0)
            )

            dmgFont = pygame.font.Font(DUNGEON_FONT, SPELL_NAME_FONT_SIZE).render(
                str(spell.dmg), True, (0, 0, 0)
            )
            dmgFontRect = dmgFont.get_rect(
                center=(SPELL_INFO_DMG_ICON_POINT[0] + 60, SPELL_INFO_DMG_ICON_POINT[1])
            )

            dmgRangeFont = pygame.font.Font(DUNGEON_FONT, SPELL_NAME_FONT_SIZE).render(
                str(spell.dmgRange), True, (0, 0, 0)
            )
            dmgRangeFontRect = dmgRangeFont.get_rect(
                center=(
                    SPELL_INFO_DMGRANGE_ICON_POINT[0] + 60,
                    SPELL_INFO_DMGRANGE_ICON_POINT[1],
                )
            )

            #  Icons
            dmgIcon = pygame.transform.scale(
                spellsConf.DMG_ICON.copy(), SPELL_INFO_ICON_DIM
            )
            dmgIconRect = dmgIcon.get_rect(center=SPELL_INFO_DMG_ICON_POINT)

            dmgRangeIcon = pygame.transform.scale(
                spellsConf.DMGRANGE_ICON.copy(), SPELL_INFO_ICON_DIM
            )
            dmgIconRangeRect = dmgRangeIcon.get_rect(
                center=SPELL_INFO_DMGRANGE_ICON_POINT
            )

            spellInfoSurf.blit(nameFont, nameFontRect)
            spellInfoSurf.blit(dmgFont, dmgFontRect)
            spellInfoSurf.blit(dmgRangeFont, dmgRangeFontRect)

            spellInfoSurf.blit(dmgIcon, dmgIconRect)
            spellInfoSurf.blit(dmgRangeIcon, dmgIconRangeRect)

            icon = pygame.transform.scale(
                spell.icon,
                (int(spellInfoRect.height * 0.45), int(spellInfoRect.height * 0.45)),
            )
            iconRect = icon.get_rect(topleft=(10, 10))
            spellInfoSurf.blit(icon, iconRect)

            self.spellsSurfInfos.append(spellInfoSurf)
            self.spellsRectInfos.append(spellInfoRect)
            self.spellsDesc.append(descText)
            self.spellAnims.append(
                Anim(
                    self.Game,
                    SPELL_ANIMATION_CENTER,
                    spell.animationDuration,
                    spell.animationFrames,
                )
            )
            self.spells.append(spell)

            count = (count + 1) % 3

    def transition(self, name, frames, time):

        print(self.bg)
        if name == "open":
            self.open = True
        elif name == "close":
            self.open = False
        elif name == "next":
            self.pageIndex += 1 if self.pageIndex != self.MAX_PAGE_INDEX else 0
        elif name == "back":
            self.pageIndex -= 1 if self.pageIndex != 0 else 0

        for frame in frames:
            self.Game.screen.blit(self.bg, (0, 0))
            self.Game.screen.blit(frame, self.rect)
            self.Game.show(combatMode=False)
            sleep(time / len(frames))

    def setBackground(self):
        self.bg = self.Game.screen.copy()

    def show(self, combatMode=False):

        self.setBackground()
        if not self.open:
            self.transition("open", self.openAnimFrames, OPEN_ANIM_TIME)

        while self.open:

            for event in pygame.event.get():

                if (
                    event.type == pygame.KEYDOWN
                    and event.key == self.Game.KeyBindings["Toggle Spell Book"]["value"]
                    and not combatMode
                ):
                    self.transition("close", self.closeAnimFrames, CLOSE_ANIM_TIME)

                # ---------- FIGHT MODE ---------- #

                if combatMode and event.type == pygame.MOUSEBUTTONDOWN:

                    for i, spellRect in enumerate(self.spellsRectInfos):
                        if (
                            spellRect.collidepoint(
                                [
                                    coor - offset
                                    for coor, offset in zip(
                                        pygame.mouse.get_pos(), self.rect.topleft
                                    )
                                ]
                            )
                            and self.pageIndex * 3 <= i < self.pageIndex * 3 + 3
                            and i < len(self.Hero.spellsID)
                        ):
                            logger.debug(f"casting {self.spells[i].name}")
                            self.transition(
                                "close", self.closeAnimFrames, CLOSE_ANIM_TIME
                            )
                            if self.pageIndex == 0 and i == 0:  # Auto attack case
                                self.Game.fightMode.makeSpell(
                                    self.spells[i], autoattack=True
                                )
                            else:
                                self.Game.fightMode.makeSpell(self.spells[i])

                # --------- PAGE SELECTION ------------ #

                for button in self.buttons:

                    if button == "next" and self.pageIndex == self.MAX_PAGE_INDEX:
                        continue
                    elif button == "back" and self.pageIndex == 0:
                        continue

                    if self.buttons[button]["rect"].collidepoint(
                        pygame.mouse.get_pos()
                    ):

                        self.mainSurf.blit(
                            self.buttons[button]["surfClicked"],
                            self.buttons[button]["rect"],
                        )

                        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:

                            if button == "next":
                                self.transition(
                                    "next", self.nextAnimFrames, NEXT_ANIM_TIME
                                )
                            else:
                                self.transition(
                                    "back", self.backAnimFrames, BACK_ANIM_TIME
                                )

                    else:
                        self.mainSurf.blit(
                            self.buttons[button]["surf"], self.buttons[button]["rect"]
                        )

            if self.open:
                self.Game.screen = self.bg.copy()
                self.Game.screen.blit(self.mainSurf, self.rect)

                pygame.draw.lines(
                    self.Game.screen, (0, 0, 0), True, SPELL_DESC_SLOT_POINTS, 4
                )
                self.Game.screen.blit(self.classNameTitle, self.classNameTitleRect)
                self.Game.screen.blit(self.animTitle, self.animTitleRect)

                for i in range(self.pageIndex * 3, self.pageIndex * 3 + 3):
                    if i < len(self.Hero.spellsID):
                        # ----------- SPELL HOOVERING / ANIMATION -------------- #

                        # Bliting desc on spellSurfInfo hoovering
                        if self.spellsRectInfos[i].collidepoint(pygame.mouse.get_pos()):

                            self.spellsDesc[i].update()
                            self.Game.screen.blit(self.descSlot, self.descSlotRect)

                            # Launching animation
                            self.spellAnims[i].show()
                        else:
                            self.spellAnims[i].hide()

                        self.Game.screen.blit(
                            self.spellsSurfInfos[i], self.spellsRectInfos[i]
                        )
                        self.spellAnims[i].mainLoop()

                self.Game.show(combatMode=False)

    # def __getstate__(self):

    #     state = self.__dict__.copy()

    #     for attrName in [
    #         "openAnimFrames",
    #         "closeAnimFrames",
    #         "backAnimFrames",
    #         "nextAnimFrames",
    #         "blankPage",
    #         "mainSurf",
    #         "buttons",
    #         "animTitle",
    #         "spellsSurfInfos",
    #         "descSlot",
    #     ]:
    #         state.pop(attrName)

    # def __setstate__(self, state):

    #     self.__dict__.update(state)
    #     self.__init__(self.Game, self.Hero)