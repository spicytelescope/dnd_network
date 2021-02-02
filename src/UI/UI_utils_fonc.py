# Thanks to http://www.akeric.com/blog/?p=720
import pygame, math
from utils.utils import logger


def blurSurf(surface, amt) -> pygame.Surface:
    """

    Blur the given surface by the given 'amount'.  Only values 1 and greater
    are valid.  Value 1 = no blur.
    """

    if amt < 1.0:
        amt = 1.0
        logger.warning("BLUR AMOUNT MUST BE GREATER THAN 1.0")

    scale = 1.0 / float(amt)
    surf_size = surface.get_size()
    scale_size = (int(surf_size[0] * scale), int(surf_size[1] * scale))
    surf = pygame.transform.smoothscale(surface, scale_size)
    surf = pygame.transform.smoothscale(surf, surf_size)
    return surf

def formatDialogContent(string, charLimit)-> list:
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