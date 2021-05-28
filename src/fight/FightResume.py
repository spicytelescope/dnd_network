import pygame
from pygame.constants import KEYDOWN, K_RETURN, SRCALPHA

from config.UIConf import DUNGEON_FONT, TEXT_FONT_SIZE
from gameObjects.Ennemy import Ennemy
from config.itemConf import *


class FightRecap:
    def __init__(self, gameController, FightMode) -> None:

        self.Game = gameController
        self.FightMode = FightMode
        self.show = True
        self.TEXT_COLOR = (0, 0, 0)

        #  ------------------ STATS ----------------- #

        self.fightStats = FightMode.stats
        self.totalDealt = 0

        # ------------- TEXTURES ----------------- #

        self.moneySurf = pygame.image.load("./assets/Items/money.png").convert_alpha()

        self.layout = pygame.transform.scale(
            pygame.image.load("./assets/UI/fight/recapLayout.png"),
            (int(self.Game.resolution * 0.75), int(self.Game.resolution * 0.75)),
        ).convert_alpha()
        self.layoutRect = self.layout.get_rect(
            center=(self.Game.resolution // 2, self.Game.resolution // 2)
        )

        self.dmgSurf = pygame.Surface(
            (int(self.layoutRect.width * 0.85), int(self.layoutRect.height * 0.3)),
            SRCALPHA,
        )
        self.dmgSurfRect = self.dmgSurf.get_rect(
            center=(self.layoutRect.width // 2, int(self.layoutRect.height * 0.35))
        )

        self.lootSurf = pygame.Surface(
            (int(self.layoutRect.width * 0.85), int(self.layoutRect.height * 0.3)),
            SRCALPHA,
        )
        self.lootSurfRect = self.lootSurf.get_rect(
            center=(self.layoutRect.width // 2, int(self.layoutRect.height * 0.75))
        )
        # self.lootSurf.fill((255,255,255))
        # self.dmgSurf.fill((255,255,255))
        # pygame.draw.lines(
        #     self.lootSurf,
        #     (0, 0, 0),
        #     True,
        #     [
        #         (0, 0),
        #         (self.lootSurfRect.width-1, 0),
        #         [coor - 1 for coor in self.lootSurfRect.size],
        #         (0, self.lootSurfRect.height-1),
        #     ],
        #     2,
        # )

        # Titles
        exitFont = pygame.font.Font(DUNGEON_FONT, 40)
        exitFont.italic = True
        self.exitTitle = exitFont.render(
            "Press <Enter> to end the fight", True, self.TEXT_COLOR
        )
        self.exitTitleRect = self.exitTitle.get_rect(
            center=(self.layoutRect.width // 2, int(self.layoutRect.height * 0.93))
        )

        self.RecapFont = pygame.font.Font(DUNGEON_FONT, 80).render(
            "FIGHT RECAP", True, self.TEXT_COLOR
        )
        self.RecapFontRect = self.RecapFont.get_rect(
            center=(self.layoutRect.width // 2, int(self.layoutRect.height * 0.08))
        )

        self.DmgTitle = pygame.font.Font(DUNGEON_FONT, 50).render(
            "----------- DAMAGES DEALT ----------", True, self.TEXT_COLOR
        )
        self.DmgTitleRect = self.DmgTitle.get_rect(
            center=(self.layoutRect.width // 2, int(self.layoutRect.height * 0.18))
        )

        self.LootTitle = pygame.font.Font(DUNGEON_FONT, 50).render(
            "--------------- LOOTS ---------------", True, self.TEXT_COLOR
        )
        self.LootTitleRect = self.LootTitle.get_rect(
            center=(self.layoutRect.width // 2, int(self.layoutRect.height * 0.55))
        )

    def initDmgSurf(self):

        self.totalDealt = sum(self.fightStats.values())
        PADDING = self.dmgSurfRect.height // 3
        for i, (entityName, entityDmg) in enumerate(self.fightStats.items()):
            dmgText = ""

            if self.totalDealt > 0:
                dmgText = f"{entityName} : {entityDmg} damage points ({round(100*entityDmg/self.totalDealt, 2)}%)"
            else:
                dmgText = f"{entityName} : 0 damage points (100%)"

            dmgFont = pygame.font.Font(DUNGEON_FONT, 50).render(
                dmgText,
                True,
                self.TEXT_COLOR,
            )
            self.dmgSurf.blit(
                dmgFont,
                (
                    int(self.dmgSurfRect.width * 0.05),
                    int(self.dmgSurfRect.height * 0.1) + i * PADDING,
                ),
            )

    def initLootSurf(self, entityList):

        PADDING = self.lootSurfRect.height // 3
        for i, entity in enumerate(entityList):

            if isinstance(entity, Ennemy):
                entityNameFont = pygame.font.Font(DUNGEON_FONT, 50, italic=True).render(
                    f"{entity._fightName} : ",
                    True,
                    (0, 0, 0),
                )
                lootFont = pygame.font.Font(DUNGEON_FONT, 50, italic=True).render(
                    f"{entity.loot.property['name']}",
                    True,
                    RARETY_TYPES[entity.loot.property["rarety"]]["color"],
                )
                goldFont = pygame.font.Font(DUNGEON_FONT, 50).render(
                    f"{entity._fightName} : {entity.XP} XP and {entity.goldValue}",
                    True,
                    self.TEXT_COLOR,
                )

                self.lootSurf.blit(
                    entityNameFont,
                    (
                        int(self.lootSurfRect.width * 0.05),
                        i * PADDING,
                    ),
                )
                self.lootSurf.blit(
                    lootFont,
                    (
                        entityNameFont.get_width()
                        + 10
                        + int(self.lootSurfRect.width * 0.05),
                        i * PADDING,
                    ),
                )

                self.lootSurf.blit(
                    entity.loot.icon,
                    (
                        int(self.lootSurfRect.width * 0.05)
                        + lootFont.get_width()
                        + entityNameFont.get_width()
                        + 10,
                        i * PADDING,
                    ),
                )

                self.lootSurf.blit(
                    goldFont,
                    (
                        int(self.lootSurfRect.width * 0.05),
                        PADDING // 2 + i * PADDING,
                    ),
                )

                self.lootSurf.blit(
                    self.moneySurf,
                    (
                        int(self.lootSurfRect.width * 0.05) + goldFont.get_width() + 10,
                        PADDING // 2 + 15 + i * PADDING,
                    ),
                )

    def mainLoop(self):

        self.bg = self.Game.screen.copy()
        self.initDmgSurf()

        while self.show:

            self.Game.screen.blit(self.bg, (0, 0))
            self.layout = pygame.transform.scale(
                pygame.image.load("./assets/UI/fight/recapLayout.png").convert_alpha(),
                (int(self.Game.resolution * 0.75), int(self.Game.resolution * 0.75)),
            )

            for event in pygame.event.get():

                if event.type == KEYDOWN and event.key == K_RETURN:
                    self.FightMode.endFight()
                    self.show = False

            # Titles
            self.layout.blit(self.RecapFont, self.RecapFontRect)
            self.layout.blit(self.DmgTitle, self.DmgTitleRect)
            self.layout.blit(self.LootTitle, self.LootTitleRect)
            self.layout.blit(self.exitTitle, self.exitTitleRect)
            # Info surfs
            self.layout.blit(self.dmgSurf, self.dmgSurfRect)
            self.layout.blit(self.lootSurf, self.lootSurfRect)
            self.Game.screen.blit(self.layout, self.layoutRect)

            self.Game.show()
