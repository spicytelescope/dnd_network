import logging
import matplotlib.pyplot as plt
import time
import pygame
import webbrowser


def openDoc():
    """Open the mkdocs static serv"""
    try:
        url = "../site/index.html"
        webbrowser.open(url, new=2)
    except:
        logger.error("NO WEB BROWSER SET UP FOR DISPLAYING THE MKDOC STATIC SERV")

def measureGenTime(Map, StepGen):

    # Plot config
    plt.ylabel("Generation Time")
    plt.xlabel("STEP_GENERATION")

    # Axis data
    genTimeArray = []
    stepGenerationArray = [2 ** i for i in range(6)]

    for stepGen in stepGenerationArray:

        Map.stepGeneration = stepGen
        Map.chunkData = {
            "mainChunk": pygame.Surface(
                (
                    Map.CHUNK_SIZE * (Map.renderDistance + 2),
                    Map.CHUNK_SIZE * (Map.renderDistance + 2),
                )
            ),
            "currentChunkPos": [0, 0],
        }
        t1 = time.time()
        Map.generateMainChunk(Map.renderDistance)
        genTimeArray.append(time.time() - t1)

    # Displaying the plot
    plt.plot(stepGenerationArray, genTimeArray)

    plt.show()


class CustomFormatter(logging.Formatter):
    """Logging Formatter to add colors and count warning / errors"""

    blue = "\x1b[36;21m"
    green = "\x1b[32;21m"
    yellow = "\x1b[33;21m"
    red = "\x1b[31;21m"
    bold_red = "\x1b[31;1m"
    reset = "\x1b[0m"
    format = "[%(asctime)s] - %(levelname)s : %(message)s (%(filename)s:%(lineno)d)"

    FORMATS = {
        logging.DEBUG: blue + format + reset,
        logging.INFO: green + format + reset,
        logging.WARNING: yellow + format + reset,
        logging.ERROR: red + format + reset,
        logging.CRITICAL: bold_red + format + reset,
    }

    def format(self, record):
        log_fmt = self.FORMATS.get(record.levelno)
        formatter = logging.Formatter(log_fmt)
        return formatter.format(record)


# create logger with 'spam_application'
logger = logging.getLogger("PHYM_LOGGER")
logging.basicConfig(filename="log", level=logging.DEBUG, filemode="w")

# create console handler with a higher log level
c_handler = logging.StreamHandler()
c_handler.setLevel(logging.DEBUG)
c_handler.setFormatter(CustomFormatter())

logger.addHandler(c_handler)