# Dnd Networking Project

## Description

Pyhm World is a 2D RPG made in Python 3.8 for the 3A STI programmation project.

## Installation

First of all, you will need python3.8 installed in your machine.
**A later version of Python does not work for the moment**.

After cloning the repository, place yoursef into the root of the project by making the following command :

Then, let's install one package needed for the open world's generation and the other for graphical interfaces :

```bash
sudo apt install python3-tk
sudo apt install libpython3.8
sudo apt update
sudo apt upgrade
```

The last thing needed is a packet / virtual environnement manager, to install the dependencies of the project :

```bash
sudo apt install pipenv
sudo apt update
```

Enter the shell and install the dependencies :

```bash
pipenv shell
pipenv install
```

Launch the program with **./main.py** and Enjoy.

If **pipenv** isn't working, quit the shell by typing **exit** and do :

```bash
python3 -m pip install -r ./requirements.txt
ou
pip3 install -r ./requirements.txt
```

# Game Branch

When pulling stuff from this branch, don't forget to do the following in order to get a db working :

```bash
cd saves
python3 initDB.py
cd ../
./main.py
```

If you get an error like this:

```
pygame.error: ALSA: Couldn't open audio device: No such file or directory
```

Set theses lines as follow :

**utils/musicController.py** :

```python

self.sounds = musicConf.SOUNDS_BANK -> # self.sounds = musicConf.SOUNDS_BANK
self.mainChannel = pygame.mixer.Channel(0) -> # self.mainChannel = pygame.mixer.Channel(0)
self.mainChannel = pygame.mixer.Channel(0) -> # self.mainChannel.set_volume(0.3)
pass
.
.
.
def setMusic(self, place):

    if pygame.mixer.music.get_busy():
        self._changeSong(place)
        pass

    else:
        self._addSong(place)
        pass
    ->
    # if pygame.mixer.music.get_busy():
        # self._changeSong(place)
    pass

    # else:
        # self._addSong(place)
    pass
```

**main.py** :

```python
pygame.mixer.init() -> # pygame.mixer.init()
```

**utils/RessourceLoader.py** :

```python
musicConf.SOUNDS_BANK = {
        songName: pygame.mixer.Sound(songPath)
        for songName, songPath in musicConf.SOUNDS_PATH.items()
    } ->
    # musicConf.SOUNDS_BANK = {
    #     songName: pygame.mixer.Sound(songPath)
    #     for songName, songPath in musicConf.SOUNDS_PATH.items()
    # }
```
