from copy import copy
import math
import os
import platform
import random

import noise
import pygame
import utils.RessourceHandler as RessourceHandler
from config.devConf import *
from config.HUDConf import *
from config.mapConf import *
from config.textureConf import *
from gameController import *
from .envGenerator import *
from HUD.miniMap import MiniMap
from pygame.locals import *
from tqdm import tqdm
from utils.utils import iso_vec_into_standard, logger
from multiprocessing import Process


class OpenWorldMap:

    """Class generating a world map using an 2D-Array made with
    Perlin noise to make it real.

    The process is the following : 2D-Array filled with perlin noise values between -1 and 1,
    and therefor given the value, render a biome (which is a rgb code for now)
    """

    def __init__(self, config, gameController, debug=False) -> None:

        # ---------- State ----------- #
        self._stateSaved = False
        self._stateLoaded = False
        self.mainChunk_string = None
        self.chunkSurfacesString = {}

        self.Game = gameController
        self.loadingMenu = None
        self.Hero = None

        # ------------------- UNIT TESTING --------------------- #
        assert (
            type(config) is dict
        ), f"Wrong argument on class initialisation, the config passed must be a dict"

        # ------------------- LOADING MAP CONFIG --------------- #

        self.stepGeneration = config["STEP_GENERATION"]
        self.circularMap = config["CIRCULAR_MAP"]
        self.scale = config["DEFAULT_VIEW_SCALE"]
        self.id = config["id"]
        self.posOffset = [0, 0]
        self.octaves = OCTAVES_DEFAULT  # Number of biomes
        self.persistence = PERSISTENCE_DEFAULT  # randomness
        self.lacunarity = LACUNARITY_DEFAULT  # Details of each biomes
        self.mapSeed = 0
        self.enableWaterAnimation = config["ANIMATE_WATER"]["enabled"]

        # ------------------- PROGRESS BAR --------------------- #

        self.showLoading = True
        self.chunkGenerationCounter = 0
        self.progressBar = None

        # ------------------- WORLD_MAP ONLY ------------------- #

        if self.id == 0:
            self.worldMapTab = [
                [{"color": None} for _ in range(self.Game.resolution)]
                for __ in range(self.Game.resolution)
            ]
            self.WorldMapSurf = pygame.Surface(self.Game.WINDOW_SIZE)
            self.WorldMapLoaded = False
            if self.circularMap:
                # World map Settings
                self.CIRCULAR_MASK = [
                    [
                        (i - self.Game.resolution / 2) ** 2
                        + (j - self.Game.resolution / 2) ** 2
                        <= (self.Game.resolution / 2) ** 2
                        for j in range(self.Game.resolution)
                    ]
                    for i in range(self.Game.resolution)
                ]

        # ------------------- CHUNKS (ONLY FOR PLAYER MAP) ----- #

        if self.id == 1:
            if self.enableWaterAnimation:
                pygame.time.set_timer(
                    config["ANIMATE_WATER"]["eventId"],
                    config["ANIMATE_WATER"]["animation_delay"],
                )
                self.waterAnimationCount = 0

            # Length of a chunk, which results in a square of CHUNK_SIZE by CHUNK_SIZE
            self.CHUNK_SIZE = self.Game.resolution
            assert (
                self.CHUNK_SIZE % 2 == 0
            ), f"<ERROR> : the CHUNK_SIZE needs to be a multiple of 2"
            self.MAX_LDO = math.log(self.CHUNK_SIZE // 16, 2)
            self.lod = self.MAX_LDO - config["LOD"]

            # Number of layers of surrounding chunks the player can have around him
            self.currentChunkSubdivision = (
                min(self.Game.WINDOW_SIZE) // self.stepGeneration
            )
            self.renderDistance = 1
            self.maxChunkGen = (1 + self.renderDistance * 2) ** 2
            self.reGenChunkFlag = False
            self.reGenProcessHandler = None

            # By default, the chunk where the player spawns will be considered at 0,0
            # This system of coordonates follows the direction and the axis of the one of pygame !

            self.chunkData = {
                "mainChunk": pygame.Surface(
                    (
                        self.CHUNK_SIZE * (self.renderDistance + 2),
                        self.CHUNK_SIZE * (self.renderDistance + 2),
                    )
                ),
                "currentChunkPos": [0, 0],
            }

            # The minimum distance of the chunk needs to be greater than half of the self.screen's size
            assert (
                self.CHUNK_SIZE * self.renderDistance >= self.Game.resolution
            ), "<ERROR> : Chunk settings aren't set up properly for chunk generation"

        assert (
            self.Game.resolution % self.stepGeneration == 0
        ), f"<ERROR> : the step generation need a multiple of self.Game.resolution"

        # ------------------- CREATING OPEN WORLD HANDLER -------------- #

        if self.id == 1 and not debug:
            self.envHandler = EnvHandler(self.Game, self)
            self.envGenerator = self.envHandler.envGenerator

            # Pathfinding purpose
            self.matrix = [
                [
                    1
                    for _ in range(
                        self.currentChunkSubdivision * (self.renderDistance + 2)
                    )
                ]
                for __ in range(
                    self.currentChunkSubdivision * (self.renderDistance + 2)
                )
            ]

    def genChunkStructures(self):
        """Adding each chunks structure, the bliting will be handled by parallelism"""

        for j in range(-self.renderDistance, self.renderDistance + 1):
            for i in range(-self.renderDistance, self.renderDistance + 1):

                chunkCoor = (
                    str(i + self.chunkData["currentChunkPos"][0])
                    + ";"
                    + str(j + self.chunkData["currentChunkPos"][1])
                )

                # Checking if a chunk is not already generated, otherwise we don't generate it
                if chunkCoor not in self.chunkData.keys():
                    # Adding a chunk entry in the chunkData dict
                    self.chunkData[
                        str(i + self.chunkData["currentChunkPos"][0])
                        + ";"
                        + str(j + self.chunkData["currentChunkPos"][1])
                    ] = {
                        "initialised": False,
                        "textureTab": [
                            [
                                {"color": None}
                                for i in range(self.currentChunkSubdivision)
                            ]
                            for j in range(self.currentChunkSubdivision)
                        ],
                        "elementTab": [
                            [
                                {
                                    "type": None,
                                    "value": None,
                                    "name": None,
                                    # Parameters for some landscapes elements that have random textures, fix the textures.
                                    "surfIndex": -1,
                                    "structure": {
                                        "name": None,
                                        "surf": None,
                                        "borderSurf": None,
                                        "isBorder": False,
                                    },
                                }
                                for i in range(MIN_CHUNK_SUBDIVISON)
                            ]
                            for j in range(MIN_CHUNK_SUBDIVISON)
                        ],
                        # Flag for marking if a chunk has already been processed by the envGenerator
                        "elementsGenerated": False,
                        "surface": pygame.Surface(
                            (self.Game.resolution, self.Game.resolution)
                        ),
                    }

    def generateMainChunk(self, nChunks):
        """Creating nChunks chunks (too much chunks ya) around the one at the coordonates of self.chunkData["currentChunkPos"], and then turning it into 1 big picture"""

        self.chunkData["mainChunk"] = pygame.Surface(
            (
                self.CHUNK_SIZE * (self.renderDistance + 2),
                self.CHUNK_SIZE * (self.renderDistance + 2),
            )
        )

        assert (
            self.id == 1
        ), f"<ERROR> : the generateMainChunk method can only be call for the PLAYER_MAP"

        for j in range(-self.renderDistance, self.renderDistance + 1):
            for i in range(-self.renderDistance, self.renderDistance + 1):

                chunkCoor = (
                    str(i + self.chunkData["currentChunkPos"][0])
                    + ";"
                    + str(j + self.chunkData["currentChunkPos"][1])
                )

                # Checking if a chunk is not already generated, otherwise we don't generate it
                if (
                    chunkCoor not in self.chunkData.keys()
                    or not self.chunkData[chunkCoor]["initialised"]
                ):

                    self.chunkData[chunkCoor]["initialised"] = True

                    self.chunkGenerationCounter += 1
                    self.loadingMenu.updateProgressBar(
                        f"chunk_{self.chunkGenerationCounter}", "map"
                    )
                    # Handling progress bar
                    self.progressBar = tqdm(
                        total=(self.Game.resolution // self.stepGeneration) ** 2,
                        desc=f"Generating chunks {self.chunkGenerationCounter}/{nChunks}",
                        ncols=TQDM_MAP_GENERATION_WIDTH,
                    )

                    # We multiply by '-i' or '-j as the direction is the opposite of    the    scrolling offset

                    self.posOffset = [
                        self.Game.resolution
                        * (-(i + self.chunkData["currentChunkPos"][0])),
                        self.Game.resolution
                        * (-(j + self.chunkData["currentChunkPos"][1])),
                    ]

                    # We then generate the textureTab with the perlin values and create the appropriate surface
                    self._initMap(
                        self.chunkData[
                            str(i + self.chunkData["currentChunkPos"][0])
                            + ";"
                            + str(j + self.chunkData["currentChunkPos"][1])
                        ]["textureTab"],
                        self.chunkData[
                            str(i + self.chunkData["currentChunkPos"][0])
                            + ";"
                            + str(j + self.chunkData["currentChunkPos"][1])
                        ]["surface"],
                    )

                    self.loadingMenu.confirmLoading(
                        f"chunk_{self.chunkGenerationCounter}", "map"
                    )

                # We still need to reset the posOffset for the other chunks to generate
                self.posOffset = [0, 0]

                self.chunkData["mainChunk"].blit(
                    self.chunkData[chunkCoor]["surface"],
                    (
                        self.CHUNK_SIZE * (i + self.renderDistance),
                        self.CHUNK_SIZE * (j + self.renderDistance),
                    ),
                )

                self.progressBar.close()

        if self.chunkGenerationCounter == nChunks:

            # After bliting the primary texture, we generate the trees and stuff like that

            # Applying isometric

            self.chunkData["mainChunk"] = pygame.transform.rotate(
                self.chunkData["mainChunk"], 45
            )
            self.chunkData["mainChunk"] = pygame.transform.scale(
                self.chunkData["mainChunk"],
                (
                    self.chunkData["mainChunk"].get_width(),
                    self.chunkData["mainChunk"].get_height() // 2,
                ),
            )

            self.loadingMenu.updateProgressBar("worldElements")
            self.envHandler.generateWorldElements(fastGen=(nChunks == 0))
            self.loadingMenu.confirmLoading("worldElements")
            # pygame.image.save(self.chunkData["mainChunk"], "mainChunk.png")

            self.miniMap.update()

            self.Hero.posMainChunkCenter = [
                int(
                    self.chunkData["mainChunk"].get_width() / 2
                    - self.Hero.blitOffset[0]
                ),
                int(
                    self.chunkData["mainChunk"].get_height() / 2
                    - self.Hero.blitOffset[1]
                ),
            ]

            # We reset the progress bar chunk countee
            self.chunkGenerationCounter = 0

    def ___insertNoiseTile(self, x, y, textureTab) -> None:
        """Method inserting into one tile (with the size of STEP_GENERATIONxSTEP_GENERATION) a
        perlin noise value and then a color"""

        textureTab[y][x] = noise.pnoise2(
            ((x * self.stepGeneration) - self.posOffset[0]) / self.scale,
            ((y * self.stepGeneration) - self.posOffset[1]) / self.scale,
            octaves=self.octaves,
            persistence=self.persistence,
            lacunarity=self.lacunarity,
            repeatx=self.Game.resolution,
            repeaty=self.Game.resolution,
            base=self.mapSeed,
        )

        # Inserting color

        # Taking care of the round map if enabled in the config object
        if self.circularMap and not self.CIRCULAR_MASK[y][x]:
            textureTab[y][x] = {"color": WATER}
        else:
            if textureTab[y][x] < -0.05:
                textureTab[y][x] = {"color": WATER}
            elif textureTab[y][x] < 0:
                textureTab[y][x] = {"color": BEACH}
            elif textureTab[y][x] < 0.2:
                textureTab[y][x] = {"color": GREEN}
            elif textureTab[y][x] < 0.35:
                textureTab[y][x] = {"color": MOUNTAIN}
            elif textureTab[y][x]:
                textureTab[y][x] = {"color": SNOW}

        # handling progress bar
        if self.id == 1 and self.showLoading:
            self.progressBar.update(1)

    def __generateMapTab(self, textureTab):
        """Filling a textureTab with values generated through the method ___insertNoiseTile"""

        for j in range(len(textureTab)):
            for i in range(len(textureTab)):
                self.___insertNoiseTile(i, j, textureTab)

    def _initMap(self, textureTab, surface):
        """Initialize a chunks at chunkCoor by creating a surface based on a textureTab with the following steps :
        - insert in the textureTab perlin noise values,
        - given the perlin noise, transform each values into tuples of colors to identify which texture to blit
        - blit the basic texture in the SCREEN_SIZExSCREEN_SIZE surface - blit the solid elements of the world with rule-based pseudo-random generation"""

        textureToBlit = None
        self.__generateMapTab(textureTab)
        for j in range(len(textureTab)):
            for i in range(len(textureTab)):

                # Basic texture generation

                if textureTab[j][i]["color"] == WATER:
                    # As the water is an animation, we don't randomly generate it
                    textureToBlit = textureConf.WORLD_TEXTURES["WATER_ANIMATIONS"][0]
                elif textureTab[j][i]["color"] == BEACH:
                    textureToBlit = random.choice(
                        textureConf.WORLD_TEXTURES["SAND_SPRITES"]
                    )
                elif textureTab[j][i]["color"] == GREEN:
                    textureToBlit = random.choice(
                        textureConf.WORLD_TEXTURES["PLAINS_SPRITES"]
                    )
                elif textureTab[j][i]["color"] == MOUNTAIN:
                    textureToBlit = random.choice(
                        textureConf.WORLD_TEXTURES["MOUNTAIN_SPRITES"]
                    )
                elif textureTab[j][i]["color"] == SNOW:
                    textureToBlit = random.choice(
                        textureConf.WORLD_TEXTURES["SNOW_SPRITES"]
                    )

                surface.blit(
                    textureToBlit,
                    (
                        i * self.stepGeneration,
                        j * self.stepGeneration,
                        self.stepGeneration,
                        self.stepGeneration,
                    ),
                )

    def chunkController(self):
        """
        Update the self.chunkData["currentChunkPos"] array by keeping tracks of where the player
        is regarding of the chunks.

        If the player goes on a bordered chunks (a chunk that didn't generated other chunks yet),
        it will call the generateMainChunk method with the following way :

        XXX                                       XXXY
        XXX => (player goes on the right side) => XXXY (Y are the new chunks)
        XXX                                       XXXY
        """

        if (
            abs(standard_vec_into_iso(*self.Hero.blitOffset)[0])
            >= standard_vec_into_iso(self.CHUNK_SIZE / 2, 0)[0]
        ):

            # We need to re compute the coordonates as we redefine a new center for the big chunkss
            if (
                standard_vec_into_iso(*self.Hero.blitOffset)[0] < 0
            ):  # Go to the right chunk
                self.chunkData["currentChunkPos"][0] += 1
                print("offset : ", standard_vec_into_iso(*self.Hero.blitOffset))
                logger.debug(
                    f"{[standard_vec_into_iso(self.CHUNK_SIZE, 0)[0] + standard_vec_into_iso(*self.Hero.blitOffset)[0], standard_vec_into_iso(*self.Hero.blitOffset)[1]]}"
                )
                self.Hero.blitOffset = iso_vec_into_standard(
                    standard_vec_into_iso(self.CHUNK_SIZE, 0)[0]
                    + standard_vec_into_iso(*self.Hero.blitOffset)[0],
                    0,
                )
                self.Hero.disp_mainChunkPosX = (
                    self.Hero.initChunkPosX + self.Hero.blitOffset[0]
                )

            else:
                self.chunkData["currentChunkPos"][0] -= 1
                self.Hero.blitOffset = iso_vec_into_standard(
                    standard_vec_into_iso(*self.Hero.blitOffset)[0]
                    - standard_vec_into_iso(self.CHUNK_SIZE, 0)[0],
                    0,
                )

            self.reGenChunkFlag = True

        if (
            abs(standard_vec_into_iso(*self.Hero.blitOffset)[1])
            >= standard_vec_into_iso(0, self.CHUNK_SIZE / 2)[1]
        ):
            if (
                standard_vec_into_iso(*self.Hero.blitOffset)[1] < 0
            ):  # Go to the down chunk
                self.chunkData["currentChunkPos"][1] += 1
                self.Hero.blitOffset = iso_vec_into_standard(
                    0,
                    standard_vec_into_iso(0, self.CHUNK_SIZE)[1]
                    + standard_vec_into_iso(*self.Hero.blitOffset)[1],
                )

            else:
                self.chunkData["currentChunkPos"][1] -= 1
                self.Hero.blitOffset = iso_vec_into_standard(
                    0,
                    standard_vec_into_iso(*self.Hero.blitOffset)[1]
                    - standard_vec_into_iso(0, self.CHUNK_SIZE)[1],
                )

            self.reGenChunkFlag = True

        # If there is a change of chunk, we need to regenerate if needed some chunks, and reset the flag system
        if self.reGenChunkFlag:

            self.Hero.disp_mainChunkPosX = (
                self.Hero.initChunkPosX + self.Hero.blitOffset[0]
            )
            self.Hero.disp_mainChunkPosY = (
                self.Hero.initChunkPosY + self.Hero.blitOffset[1]
            )

            logger.info(self.Hero.blitOffset)

            self.Hero.posMainChunkCenter = [
                int(
                    self.chunkData["mainChunk"].get_width() / 2
                    - self.Hero.blitOffset[0]
                ),
                int(
                    self.chunkData["mainChunk"].get_height() / 2
                    - self.Hero.blitOffset[1]
                ),
            ]

            chunkCoorsRegen = [
                (
                    self.chunkData["currentChunkPos"][0] + i,
                    self.chunkData["currentChunkPos"][1] + j,
                )
                for i in range(-self.renderDistance, self.renderDistance + 1)
                for j in range(-self.renderDistance, self.renderDistance + 1)
                if f"{self.chunkData['currentChunkPos'][0]+i};{self.chunkData['currentChunkPos'][1] + j}"
                not in self.chunkData.keys()
            ]
            # Check if the chunk supposely needed for regen are already generated or not
            # if len(chunkCoorsRegen) != 0:
            #     loadingIconThread = Thread(
            #         target=self.Map.loadingMenu.blitLoadingIcon, args=(self,)
            #     )
            #     loadingIconThread.start()

            self.genChunkStructures()
            self.reGenProcessHandler = Process(
                target=self.generateMainChunk, args=(len(chunkCoorsRegen),)
            )
            self.reGenProcessHandler.run()
            self.reGenChunkFlag = False

    def showTabMap(self):
        logger.debug(self.worldMapTab)

    # def zoom(self, surface, zoomType=1):
    #     # Center the map from where the player click
    #     dist_x = self.Game.resolution / 2 - pygame.mouse.get_pos()[0]
    #     dist_y = self.Game.resolution / 2 - pygame.mouse.get_pos()[1]
    #     self.posOffset[0] += dist_x
    #     self.posOffset[1] += dist_y
    #     if zoomType == 1:  # Left click
    #         if self.scale + ZOOM_FACTOR < MAX_ZOOM_IN_VALUE:
    #             self.scale *= ZOOM_FACTOR
    #         else:
    #             print(f"<ERROR> : ZOOM_IN LIMIT REACHED")
    #     elif zoomType == 3:  # Right click
    #         if self.scale - ZOOM_FACTOR > 0:  # preventing negative zoom
    #             self.scale /= ZOOM_FACTOR
    #         else:
    #             print(f"<ERROR> : ZOOM_OUT LIMIT REACHED")
    #     if self.Game.debug_mode:
    #         logger.debug(f"scale : {self.scale}")

    #     self._initMap(self.worldMapTab, surface)
    #     self.screen.blit(surface, (0, 0))

    def updateWaterAnimation(self):
        """ Method going through all the surrouding chunks and updating the surface of the water to make an animation """

        assert (
            self.id == 1
        ), f"<ERROR> : can't invoke this method within WORLD_MAP configuration"

        self.waterAnimationCount += 1
        if self.waterAnimationCount == 3:
            self.waterAnimationCount = 0
        for j in range(-self.renderDistance, self.renderDistance + 1):
            for i in range(-self.renderDistance, self.renderDistance + 1):

                chunkCoor = (
                    str(i + self.chunkData["currentChunkPos"][0])
                    + ";"
                    + str(j + self.chunkData["currentChunkPos"][1])
                )
                chunkTab = self.chunkData[chunkCoor]["textureTab"]

                if (
                    chunkCoor in self.chunkData.keys()
                    and not self.chunkData["mainChunk"].get_locked()
                ):
                    for k in range(len(chunkTab)):
                        for l in range(len(chunkTab)):
                            if chunkTab[k][l]["color"] == WATER:
                                # We use the update fuction to update a part of the main chunk
                                self.chunkData["mainChunk"].blit(
                                    textureConf.WORLD_TEXTURES["WATER_ANIMATIONS"][
                                        self.waterAnimationCount
                                    ],
                                    (
                                        self.CHUNK_SIZE * (i + self.renderDistance)
                                        + (l * self.stepGeneration),
                                        self.CHUNK_SIZE * (j + self.renderDistance)
                                        + (k * self.stepGeneration),
                                    ),
                                )

            pygame.display.flip()

    def show(self, Hero):

        if (
            not self.Game.screen.get_locked()
            and not self.chunkData["mainChunk"].get_locked()
        ):
            self.Game.screen.blit(
                self.chunkData["mainChunk"],
                (
                    Hero.disp_mainChunkPosX,
                    Hero.disp_mainChunkPosY,
                ),
            )

    def updateMapSeed(self, mode):

        if mode == "up":
            self.mapSeed += 1
        else:
            if self.mapSeed > 0:
                self.mapSeed -= 1

    def setLenBiomes(self, mode):

        self.octaves += 1 if mode == "up" and self.octaves != MAX_BIOMES else 0
        self.octaves -= 1 if mode == "down" and self.octaves != MIN_BIOMES else 0

    def loadPlayerdMap(self, nChunks: int, Hero) -> None:
        """Generate the player Map by loading the chunk textures and generating the first chunks

        Arguments:
        --

        nChunks : number of chunks that are generated, usually set according to the Map render distance

        Return Value:
        --

        None
        """
        if Hero.genOrder == 0:
            self.loadingMenu.updateProgressBar("biomeTextures")
            RessourceHandler.loadOpenWorldRessources(self.stepGeneration)
            self.loadingMenu.confirmLoading("biomeTextures")
            RessourceHandler.loadMiniMapRessources()
            self.miniMap = MiniMap(self.Game, self, Hero)
            self.genChunkStructures()
            self.generateMainChunk(nChunks)

        Hero.initChunkPosX = -self.chunkData["mainChunk"].get_width() / 2 + Hero.pos[0]
        Hero.initChunkPosY = -self.chunkData["mainChunk"].get_height() / 2 + Hero.pos[1]
        Hero.disp_mainChunkPosX = Hero.initChunkPosX
        Hero.disp_mainChunkPosY = Hero.initChunkPosY

    def initWorldMap(self):

        RessourceHandler.loadOpenWorldRessources(self.stepGeneration)
        self._initMap(self.worldMapTab, self.WorldMapSurf)
        self.WorldMapLoaded = True

    def resetChunks(self):
        """Method called to regenate the chunk, usually after the LDO has been modified"""

        # Copy the current chunk coor in order not to lose them because we regen the main chunk from it
        tmpCurrentPos = self.chunkData["currentChunkPos"]

        self.chunkData = {
            "mainChunk": pygame.Surface(
                (
                    self.CHUNK_SIZE * (self.renderDistance + 2),
                    self.CHUNK_SIZE * (self.renderDistance + 2),
                )
            ),
            "currentChunkPos": [0, 0],
        }

        self.chunkData["currentChunkPos"] = tmpCurrentPos

        # Reseting the textures according to the new stepGeneration value
        RessourceHandler.loadLandscapeRessources(self.stepGeneration)
        RessourceHandler.loadOpenWorldRessources(self.stepGeneration)

    # def __getstate__(self):

    #     state = self.__dict__.copy()
    #     state.pop("progressBar")
    #     state.pop("Game")

    #     if not self._stateSaved:

    #         if self.id == 1:
    #             for entry in [
    #                 attr
    #                 for attr in list(self.chunkData.keys())
    #                 if attr not in ["mainChunk", "currentChunkPos"]
    #             ]:
    #                 print(f"SAVING {entry} - {entry}")
    #                 tmpSurf = self.chunkData[entry]["surface"]
    #                 self.chunkSurfacesString[entry] = (
    #                     pygame.image.tostring(tmpSurf, "RGB"),
    #                     tmpSurf.get_size(),
    #                 )

    #             self.mainChunk_string = (
    #                 pygame.image.tostring(self.chunkData["mainChunk"], "RGB"),
    #                 self.chunkData["mainChunk"].get_size(),
    #             )

    #             state = self.__dict__.copy()
    #             state.pop("Game")
    #             state.pop("progressBar")

    #         if self.id == 0:

    #             WorldMapSurf = state.pop("WorldMapSurf")
    #             state["WorldMapSurf_string"] = (
    #                 pygame.image.tostring(WorldMapSurf, "RGB"),
    #                 WorldMapSurf.get_size(),
    #             )

    #         elif self.id == 1:

    #             state["chunkData"].pop("mainChunk")
    #             for entry in [
    #                 attr
    #                 for attr in list(self.chunkData.keys())
    #                 if attr not in ["mainChunk", "currentChunkPos"]
    #             ]:
    #                 state["chunkData"][entry].pop("surface")

    #         self._stateSaved = True
    #         self._stateLoaded = False  # To reload it afterward

    #     return state

    # def __setstate__(self, state):

    #     state["_stateSaved"] = False  #  Reseting it for next loading

    #     print(state["chunkSurfacesString"].keys())
    #     if state["id"] == 0:
    #         WorldMapSurf_string, size = state.pop("WorldMapSurf_string")
    #         state["WorldMapSurf"] = pygame.image.fromstring(
    #             WorldMapSurf_string, size, "RGB"
    #         )

    #     elif state["id"] == 1:

    #         mainChunk_str, mainChunkSize = state["mainChunk_string"]
    #         state["chunkData"]["mainChunk"] = pygame.image.fromstring(
    #             mainChunk_str, mainChunkSize, "RGB"
    #         )

    #         for entry, (stringSurf, size) in state["chunkSurfacesString"].items():
    #             state["chunkData"][entry]["surface"] = pygame.image.fromstring(
    #                 stringSurf, size, "RGB"
    #             )

    #     self.__dict__.update(state)

    # if self.id == 1:
    #     self.miniMap.__init__(self.Game, self, self.Hero)
