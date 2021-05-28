import time

from config.mapConf import *


class Anim:
    def __init__(
        self,
        gameController,
        centerPoint,
        duration,
        frames,
        once=False,
        effect=None,
        surface=None,
    ):

        """Class bliting for <duration> secondes the animation based of <frames> at the <blitPoint> to <surface> which is a center of a rect.t
        The animation is in a non blocking model by using the time.

        There is a controller that display the animation given some flags that are handled by method show() and close()

        DISCLAIMER :
        This type of animation is just a way of bliting clickly some frames, not applying transitions !"""

        self.effect = None

        # FRAMES
        self.frames = frames
        self.aniLength = len(frames)
        self.frameIndex = 0

        # SURFACE
        self.surface = surface
        self.Game = gameController
        self.rect = (
            self.surface.get_rect(center=centerPoint)
            if self.surface != None
            else self.frames[0].get_rect(center=centerPoint)
        )

        # TIME
        self.aniDeltaTime = duration / self.aniLength  # s
        self.lastRenderedTime = 0  # set so that the difference between the check up and the lastRenderedTime is higher  (initial state = no animation)

        # FLAGS
        self.showFlag = False
        self.once = once

    def show(self):

        self.showFlag = True

    def hide(self):

        self.showFlag = False

    def mainLoop(self):

        if self.showFlag:
            if self.surface != None:
                self.surface = self.frames[self.frameIndex]
                self.Game.screen.blit(self.surface, self.rect)
            else:
                self.Game.screen.blit(self.frames[self.frameIndex], self.rect)

            if time.time() - self.lastRenderedTime > self.aniDeltaTime:

                self.frameIndex = (self.frameIndex + 1) % self.aniLength
                self.lastRenderedTime = time.time()

                if self.once and self.frameIndex == len(self.frames) - 1:
                    self.close()
