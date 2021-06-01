import pygame
from config import musicConf
from config.musicConf import *


class MusicController:
    def __init__(self, gameController) -> None:

        self.Game = gameController
        self.sounds = musicConf.SOUNDS_BANK
        self.mainChannel = pygame.mixer.Channel(0)
        self.mainChannel.set_volume(
            0.3
        ) if self.Game.enableSound else self.mainChannel.set_volume(0)

    def _changeSong(self, place):
        self.mainChannel.fadeout(FADE_IN_OUT_TIME)
        self.mainChannel.play(self.sounds[place], -1, fade_ms=FADE_IN_OUT_TIME)

    def _addSong(self, place):
        self.mainChannel.play(self.sounds[place], -1, fade_ms=FADE_IN_OUT_TIME)

    def setMusic(self, place):

        if pygame.mixer.music.get_busy():
            self._changeSong(place)
        # pass

        else:
            self._addSong(place)
        # pass