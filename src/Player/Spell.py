import pygame
from config.spellsConf import *
from os import listdir
from os.path import isfile, join


class Spell:
    def __init__(
        self,
        spellId,
        name,
        desc,
        lvl,
        effect,
        dmg,
        type,
        dmgRange,
        weaponRestriction,
        animationDuration,
        animationFramesPath,
        iconPath,
        className,
    ):

        # ------ SPELL META DATA ------- #

        self.id = spellId
        self.name = name
        self.desc = desc
        self.lvl = lvl
        self.effect = effect
        self.dmg = dmg
        self.dmgRange = dmgRange
        self.className = className
        self.weaponRestriction = weaponRestriction
        self.type = type

        # -------- SPELL TEXTURES --------- #

        self.iconPath = iconPath
        self.animationDuration = animationDuration
        self.animationFramesPath = animationFramesPath
        self.animDelta = None

        self.animationFrames = None
        self.icon = None

        # -------- SPELL GAME STATE ------- #
        self.unlocked = False

    def loadTextures(self):

        logger.info(f"LOADING {self.iconPath}")
        self.animationFrames = [
            pygame.image.load(f"{self.animationFramesPath}/{f}")
            for f in listdir(self.animationFramesPath)
            if isfile(join(self.animationFramesPath, f))
        ]

        self.icon = pygame.image.load(self.iconPath).convert_alpha()
        self.animDelta = self.animationDuration / len(self.animationFrames)

    def show(self, centerCoor, size, updateFnc):

        for frame in self.animationFrames:

            spellSurf = pygame.transform.scale(frame, size)
            updateFnc(spellFrameInfo=(spellSurf, spellSurf.get_rect(center=centerCoor)))
            time.sleep(self.animDelta)

    # def __getstate__(self):

    #     state = self.__dict__.copy()
    #     for attrName in ["icon", "animationFrames"]:
    #         state.pop(attrName)

    #     return state

    # def __setstate__(self, state):

    #     self.loadTextures()
