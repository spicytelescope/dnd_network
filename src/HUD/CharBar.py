from config import playerConf
from config.menuConf import *
from config.UIConf import *
import pygame
from config.playerConf import *
from config.HUDConf import *
import config.HUDConf as HUDConf


class CharBar:
    def __init__(self, gameController, Hero):

        self.Hero = Hero
        self.Game = gameController

        # Health bars
        self.barsSurf = [HUDConf.BAR_IMG.copy() for _ in range(3)]
        self.bars = [HEALTH_BAR, MANA_BAR, EXP_BAR]

        self.healUnit = pygame.Surface(
            (BAR_CONTENT_DIM[0] // self.Hero.stats["HP_max"], BAR_CONTENT_DIM[1])
        )
        self.healUnit.fill(HEALTH_BAR["color"])
        self.manaUnit = pygame.Surface(
            (BAR_CONTENT_DIM[0] // self.Hero.stats["Mana_max"], BAR_CONTENT_DIM[1])
        )
        self.manaUnit.fill(MANA_BAR["color"])

        self.expUnit = pygame.Surface(
            (BAR_CONTENT_DIM[0] // self.Hero._XP["Expmax"], BAR_CONTENT_DIM[1])
        )
        self.expUnit.fill(EXP_BAR["color"])

        # Slots
        self.playerIconSlot = pygame.transform.scale(
            HUDConf.PLAYER_ICON_SLOT,
            (self.Game.resolution // 8, self.Game.resolution // 8),
        )
        self.playerIconSlotRect = self.playerIconSlot.get_rect()

        # Hero Icon
        self.playerIcon = pygame.transform.scale(
            playerConf.CLASSES[self.Hero.classId]["icon"],
            (self.Game.resolution // 10, self.Game.resolution // 10),
        )
        self.playerIconRect = self.playerIcon.get_rect(
            center=self.playerIconSlotRect.center
        )

        # Hero name
        self.nameFont = None
        self.nameLayout = None
        self.nameLayoutRect = None
        self.nameFontRect = None

        # Hero class/lvl

        self.classFont = None
        self.classLayout = None
        self.classLayoutRect = None
        self.classFontRect = None

    def show(self):

        # Player and icon updating
        self.nameFont = pygame.font.Font(DUNGEON_FONT, BUTTON_FONT_SIZE).render(
            f"{self.Hero.name}", True, (255, 255, 255)
        )

        self.nameLayout = pygame.transform.scale(
            HUDConf.NAME_SLOT.copy(),
            (
                int(self.nameFont.get_width() * 1.5),
                int(self.nameFont.get_height() * 1.5),
            ),
        )

        self.nameLayoutRect = self.nameLayout.get_rect(
            topleft=(0, self.playerIconSlotRect.height + 2)
        )

        self.nameFontRect = self.nameFont.get_rect(
            center=(self.nameLayoutRect.width // 2, self.nameLayoutRect.height // 2)
        )
        self.nameLayout.blit(self.nameFont, self.nameFontRect)

        #  Class and level updating

        self.classFont = pygame.font.Font(DUNGEON_FONT, BUTTON_FONT_SIZE).render(
            f"{CLASSES_NAMES[self.Hero.classId]} lv. {self.Hero._Level}",
            True,
            (255, 255, 255),
        )

        self.classLayout = pygame.transform.scale(
            HUDConf.NAME_SLOT.copy(),
            (
                int(self.classFont.get_width() * 1.5),
                int(self.classFont.get_height() * 1.5),
            ),
        )

        self.classLayoutRect = self.nameLayout.get_rect(
            topleft=(0, self.playerIconSlotRect.height + self.nameLayoutRect.height + 4)
        )

        self.classFontRect = self.nameFont.get_rect(
            center=(self.classLayoutRect.width // 2, self.classLayoutRect.height // 2)
        )
        self.classLayout.blit(self.classFont, self.classFontRect)

        # Bliting Player Icon, Name and Class

        self.playerIconSlot.blit(self.playerIcon, self.playerIconRect)

        self.Game.screen.blit(self.nameLayout, self.nameLayoutRect)
        self.Game.screen.blit(self.classLayout, self.classLayoutRect)
        self.Game.screen.blit(self.playerIconSlot, (0, 0))

        self.barsSurf = [HUDConf.BAR_IMG.copy() for _ in range(3)]

        # Bliting health bars

        self.barsSurf[0].blit(
            pygame.transform.scale(
                self.healUnit,
                (
                    int(
                        self.Hero.stats["HP"]
                        / self.Hero.stats["HP_max"]
                        * BAR_CONTENT_DIM[0]
                    ),
                    BAR_CONTENT_DIM[1],
                ),
            ),
            (
                BAR_CONTENT_BLITPOINT[0],
                BAR_CONTENT_BLITPOINT[1],
            ),
        )
        self.barsSurf[1].blit(
            pygame.transform.scale(
                self.manaUnit,
                (
                    int(
                        self.Hero.stats["Mana"]
                        / self.Hero.stats["Mana_max"]
                        * BAR_CONTENT_DIM[0]
                    ),
                    BAR_CONTENT_DIM[1],
                ),
            ),
            (
                BAR_CONTENT_BLITPOINT[0],
                BAR_CONTENT_BLITPOINT[1],
            ),
        )

        self.barsSurf[2].blit(
            pygame.transform.scale(
                self.expUnit,
                (
                    int(
                        self.Hero._XP["Exp"]
                        / self.Hero._XP["Expmax"]
                        * BAR_CONTENT_DIM[0]
                    ),
                    BAR_CONTENT_DIM[1],
                ),
            ),
            (
                BAR_CONTENT_BLITPOINT[0],
                BAR_CONTENT_BLITPOINT[1],
            ),
        )

        for i, bar in enumerate(self.bars):

            self.Game.screen.blit(self.barsSurf[i], bar["initPoint"])

    # def __getstate__(self):

    #     state = self.__dict__.copy()
    #     for attrName in [
    #         "barsSurf",
    #         "healUnit",
    #         "manaUnit",
    #         "playerIconSlot",
    #         "playerIcon",
    #         "nameFont",
    #         "nameLayout",
    #     ]:
    #         state.pop(attrName)

    # def __setstate__(self, state):

    #     self.__dict__.update(state)
    #     self.__init__(self.Game, self.Hero)