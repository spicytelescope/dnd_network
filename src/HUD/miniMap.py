import time
from threading import Thread
from config import playerConf

import config.HUDConf as HUDConf
import config.mapConf as mapConf
import pygame
from config import menuConf
from config.itemConf import *
from config.mapConf import *
from config.menuConf import *
from config.menuConf import WALKING_LOADIN_GUY_ANIM_TIME
from config.playerConf import *
from pygame.constants import KEYDOWN, MOUSEBUTTONDOWN


class MiniMap:
    """Class handling the displaying ot the minimap, which means :
    - showing the position of the player on the currentMainChunk
    - if the player press M, show the map scrolls, and enable zooming
    - default mode is "LocalArea" which shows the mainChunk, an other mode on index 0 is the "WorldArea" which shows the world map"""

    def __init__(self, gameController, Map, Hero):

        self.Game = gameController
        self.Map = Map
        self.Hero = Hero
        self._show = False

        # ---------- MINIMAP DISPLAY ---------- #

        self.width = self.Game.resolution // 5
        self.height = self.Game.resolution // 5
        self.size = [self.width, self.height]

        self.surf = pygame.transform.scale(self.Map.chunkData["mainChunk"], self.size)

        self.layout = pygame.transform.scale(
            HUDConf.PLAYER_ICON_SLOT,
            (self.Game.resolution // 4, self.Game.resolution // 4),
        )
        # Bliting the minimap at the topLeft point
        self.blitPoint = [self.Game.resolution - self.layout.get_width(), 0]

        self.layoutRect = self.layout.get_rect(topleft=self.blitPoint)

        self.rect = self.surf.get_rect(
            center=(self.layoutRect.width // 2, self.layoutRect.height // 2)
        )

        # Player Icon
        self.playerIcon = playerConf.CLASSES[self.Hero.classId]["icon"]
        self.playerIconRect = self.playerIcon.get_rect(center=self.rect.center)

        # ------------ EXTENDED MAP DISPLAY ------------ #

        self.WorldMap = None
        self.worldMapSurf = None

        self.extendedSurf = pygame.transform.scale(
            mapConf.EXTENDED_MINIMAP_BG,
            (int(self.Game.resolution * 0.75), int(self.Game.resolution * 0.75)),
        )

        self.extendedRect = self.extendedSurf.get_rect(
            center=(self.Game.resolution // 2, self.Game.resolution // 2)
        )
        self.TOPLEFT_CHUNK_BLIT = self.extendedRect.topleft

        self.playerIconExtendedRect = self.playerIcon.get_rect(
            center=self.extendedRect.center
        )

        self.extendedMapLayout = pygame.transform.scale(
            mapConf.EXTENDED_MAP_LAYOUT,
            (int(self.Game.resolution * 0.75), int(self.Game.resolution * 0.75)),
        )

        self.toolBarLayout = [
            mapConf.BAR_MAP_LAYOUT_WORLD_AREA,
            mapConf.BAR_MAP_LAYOUT_LOCAL_AREA,
        ]
        self.toolButtonsRects = [
            pygame.Rect(275, 86, 89, 47),
            pygame.Rect(365, 87, 89, 47),
        ]
        self.toolBarLayoutRect = self.toolBarLayout[0].get_rect(
            center=(
                self.Game.resolution // 2,
                self.extendedRect.topleft[1] - self.toolBarLayout[0].get_height() // 2,
            )
        )

        # World Map Loading

        self.flyingDragon = [
            pygame.transform.scale(
                img, (self.Game.resolution // 5, self.Game.resolution // 5)
            )
            for img in menuConf.WALKING_LOADING_GUY
        ]
        self.walkingGuyIndex = 0
        self.walkingGuyRect = self.flyingDragon[0].get_rect(
            topleft=(0, self.Game.resolution // 12)
        )

        self.walkingGuyDeltaTime = WALKING_LOADIN_GUY_ANIM_TIME / (
            len(menuConf.WALKING_LOADING_GUY)
        )  # s
        self.WalkingGuylastRenderedTime = time.time()

        # ---------------------- ZOOM HANDLING --------------- #

        self.buttonIndex = 1  # Default view set to localArea

        self.ZOOM_SAMPLE = [int(elt * 0.3) for elt in self.extendedSurf.get_size()]
        self.zoomValue = None
        self.dist_x = None
        self.dist_y = None

        # ------------------ MAPS UPDATING ----------------- #
        self.chunkMap = None
        self.extendedChunkMap = None
        self.chunkMapRaw = None
        self.chunkRect = None

        self.mode = ["WorldArea", "LocalArea"]

    def setWorldMap(self):

        worldMapGenThread = Thread(target=self.WorldMap.initWorldMap)
        worldMapGenThread.start()

        while not self.WorldMap.WorldMapLoaded:
            if (
                time.time() - self.WalkingGuylastRenderedTime
            ) > self.walkingGuyDeltaTime:

                self.WalkingGuylastRenderedTime = time.time()
                self.walkingGuyIndex = (self.walkingGuyIndex + 1) % len(
                    menuConf.WALKING_LOADING_GUY
                )

            loadingIcon = pygame.transform.scale(
                self.flyingDragon[self.walkingGuyIndex],
                (self.Game.resolution // 4, self.Game.resolution // 4),
            )

            loadingIconRect = loadingIcon.get_rect(
                center=(
                    self.extendedSurf.get_width() // 2,
                    self.extendedSurf.get_height() // 2,
                )
            )
            self.extendedSurf = pygame.transform.scale(
                mapConf.EXTENDED_MINIMAP_BG,
                (int(self.Game.resolution * 0.75), int(self.Game.resolution * 0.75)),
            )
            self.extendedSurf.blit(loadingIcon, loadingIconRect)
            self.extendedSurf.blit(self.extendedMapLayout, (0, 0))
            self.Game.screen.blit(self.extendedSurf, self.extendedRect)
            self.Game.show()

        self.worldMapSurf = pygame.transform.scale(
            self.WorldMap.WorldMapSurf,
            (int(self.Game.resolution * 0.70), int(self.Game.resolution * 0.70)),
        )

    def update(self):

        self.chunkMapRaw = self.Map.chunkData["mainChunk"]

        cropRect = pygame.Rect(
            0,
            0,
            self.chunkMapRaw.get_width() * MINIMAP_ZOOM_RATIO,
            self.chunkMapRaw.get_height() * MINIMAP_ZOOM_RATIO,
        )

        cropRect.center = (
            self.chunkMapRaw.get_width() // 2,
            self.chunkMapRaw.get_width() // 2,
        )

        # Minimap
        self.chunkMap = self.chunkMapRaw.subsurface(cropRect)
        self.surf = pygame.transform.scale(self.chunkMap, self.size)

        # Extended surf
        self.extendedChunkMap = pygame.transform.scale(
            self.chunkMapRaw,
            (int(self.Game.resolution * 0.70), int(self.Game.resolution * 0.70)),
        )
        self.chunkRect = self.extendedChunkMap.get_rect(
            center=(
                self.extendedSurf.get_width() // 2,
                self.extendedSurf.get_height() // 2,
            )
        )

        self.zoomValue = self.chunkRect.size
        self.offsetZoom = self.chunkRect.size
        self.dist_x = 0
        self.dist_y = 0

    def checkActions(self, event):

        if (
            event.type == KEYDOWN
            and event.key == self.Game.KeyBindings["Toggle Minimap"]["value"]
        ):
            self._show = False

        if event.type == pygame.QUIT:
            pygame.quit()
            exit()

        if event.type == MOUSEBUTTONDOWN:

            for i, rect in enumerate(self.toolButtonsRects):
                if rect.collidepoint(pygame.mouse.get_pos()):
                    self.buttonIndex = i
                    continue

            # ------------- ZOOM HANDLING ----------- #

            # zoom in
            if event.button == 4 and self.extendedRect.collidepoint(
                pygame.mouse.get_pos()
            ):

                self.dist_x = (
                    pygame.mouse.get_pos()[0]
                    - self.chunkRect.center[0]
                    - self.TOPLEFT_CHUNK_BLIT[0]
                )
                self.dist_y = (
                    pygame.mouse.get_pos()[1]
                    - self.chunkRect.center[1]
                    - self.TOPLEFT_CHUNK_BLIT[1]
                )

                self.zoomValue = [
                    dim + self.ZOOM_SAMPLE[i]
                    for i, dim in enumerate(self.zoomValue)
                ]
            elif (
                event.button == 5
            ):  # zoom out, if it doesn't mean to zoom out more than the original size
                if (
                    self.zoomValue[0] > self.offsetZoom[0]
                    and self.zoomValue[1] > self.offsetZoom[1]
                ):
                    self.zoomValue = [
                        dim - self.ZOOM_SAMPLE[i]
                        for i, dim in enumerate(self.zoomValue)
                    ]

    def show(self):

        # update the map with the move of the player
        cropRect = pygame.Rect(
            0,
            0,
            self.chunkMapRaw.get_width() * MINIMAP_ZOOM_RATIO,
            self.chunkMapRaw.get_height() * MINIMAP_ZOOM_RATIO,
        )

        # Need minus operator to follow the movement of the player
        cropRect.center = [
            int(self.chunkMapRaw.get_width() / 2 - self.Hero.blitOffset[0]),
            int(self.chunkMapRaw.get_height() / 2 - self.Hero.blitOffset[1]),
        ]

        self.chunkMap = self.chunkMapRaw.copy().subsurface(cropRect)
        self.surf = pygame.transform.scale(self.chunkMap, self.size)

        self.layout.blit(self.surf, self.rect)

        if not self.Game.screen.get_locked():
            self.Game.screen.blit(self.layout, self.layoutRect)

    def drawExtendedMap(self):

        self.Map.show(self.Hero)
        if self._show:

            self.extendedSurf = pygame.transform.scale(
                mapConf.EXTENDED_MINIMAP_BG,
                (int(self.Game.resolution * 0.75), int(self.Game.resolution * 0.75)),
            )

            if self.buttonIndex == 0:

                if self.worldMapSurf == None:
                    self.setWorldMap()

                self.worldMapSurf = pygame.transform.scale(
                    self.worldMapSurf, self.zoomValue
                )

                self.chunkRect = self.worldMapSurf.get_rect(
                    center=(
                        self.extendedSurf.get_width() // 2,
                        self.extendedSurf.get_height() // 2,
                    )
                )

                self.extendedSurf.blit(self.worldMapSurf, self.chunkRect)

            elif self.buttonIndex == 1:

                self.extendedChunkMap = self.chunkMapRaw.copy()
                self.extendedChunkMap.blit(
                    pygame.transform.scale2x(self.playerIcon),
                    (
                        int(self.chunkMapRaw.get_width() / 2 - self.Hero.blitOffset[0]),
                        int(
                            self.chunkMapRaw.get_height() / 2 - self.Hero.blitOffset[1]
                        ),
                    ),
                )

                # self.chunkRect.center = (
                #     self.extendedRect[0] + self.dist_x, self.extendedRect[1] + self.dist_y)
                self.extendedChunkMap = pygame.transform.scale(
                    self.extendedChunkMap, self.zoomValue
                )

                self.chunkRect = self.extendedChunkMap.get_rect(
                    center=(
                        self.extendedSurf.get_width() // 2,
                        self.extendedSurf.get_height() // 2,
                    )
                )

                self.extendedSurf.blit(self.extendedChunkMap, self.chunkRect)

            self.extendedMapLayout = pygame.transform.scale(
                mapConf.EXTENDED_MAP_LAYOUT,
                (int(self.Game.resolution * 0.75), int(self.Game.resolution * 0.75)),
            )

            self.extendedSurf.blit(self.extendedMapLayout, (0, 0))
            self.Game.screen.blit(self.extendedSurf, self.extendedRect)
            self.Game.screen.blit(
                self.toolBarLayout[self.buttonIndex], self.toolBarLayoutRect
            )

            self.Game.show()

    def __getstate__(self):

        state = self.__dict__.copy()
        for attrName in [
            "surf",
            "layout",
            "playerIcon",
            "extendedSurf",
            "extendedMapLayout",
            "toolBarLayout",
            "flyingDragon",
            "chunkMap",
            "extendedChunkMap",
            "chunkMapRaw",
        ]:
            state.pop(attrName)

    def __setstate__(self, state):

        self.__dict__.update(state)
