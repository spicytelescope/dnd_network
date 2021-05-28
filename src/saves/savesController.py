import sqlite3
import pickle
import pygame
from datetime import datetime
# from ..utils.utils import *

class SaveController:

    """Class made to save some parties"""

    def __init__(self) -> None:

        self.conn = sqlite3.connect("./saves/dnd_db.db")
        self.c = self.conn.cursor()
        self.tables = [
            # "Game",
            "Player_Map",
            "World_Map",
            "Hero",
            # "OptionMenu",
            # "PauseMenu",
            # "LoadingMenu",
        ]

        self.gameClasses = []

    def SaveData(self, id):
        """
        Cette fonction permet de sauvegarder la partie dans le bon emplacement en BD
        id : un entier entre 1 et 3, le numéro de la sauvegarde
        data : une liste avec les classes à sauvegarder
        Ne retourne rien
        """
        for classe, className in zip(self.gameClasses, self.tables):
            rqs = "UPDATE " + className + " SET Donnee = ? WHERE id = ?"
            self.c.execute(rqs, (self.DataToBytes(classe), id))
            self.conn.commit()

        now = datetime.now()
        dt_string = now.strftime("%d/%m/%Y : %H:%M:%S")
        self.c.execute("UPDATE Date SET DateS = ? WHERE id = ?", (dt_string, id))
        self.conn.commit()

        # logger.info(f"DATA SAVED TO DB - SLOT {id}")

    def LoadData(self, id):
        """
        Cette fonction récupère la partie de l'emplacement spécifié
        id : un entier entre 1 et 3, le numéro de la sauvegarde
        return : Une liste avec les classes chargées
        """
        res = []
        for className in self.tables:
            rqs = "SELECT Donnee FROM " + className + " WHERE id = ?"
            self.c.execute(rqs, (id,))
            res.append(self.BytesToData(self.c.fetchone()[0]))

        return res

    def DeleteData(self, id):
        """
        Cette fonction permet de supprimer une partie
        id : un entier entre 1 et 3, le numéro de la sauvegarde
        """
        for table in self.tables:
            rqs = "UPDATE " + table + " SET Donnee = ? WHERE id = ?"
            self.c.execute(rqs, (None, id))
            self.conn.commit()

        self.c.execute("UPDATE Date SET DateS = ? WHERE id = ?", (None, id))
        self.conn.commit()

    def DataToBytes(self, data):
        """
        Cette fonction convertie un objet python en données binaires
        data : un objet python
        return : l'objet sous forme binaire
        """
        print(data)
        return pickle.dumps(data)

    def BytesToData(self, bytes):
        """
        Cette fonction convertie des données binaires en objet python
        bytes : les données binaires
        return : l'objet python
        """
        return pickle.loads(bytes)

    def isSaved(self, id):
        """
        Cette fonction permet de savoir si une partie est vide ou non
        id: : un entier entre 1 et 3, le numéro de la sauvegarde
        return : un boolean, False si la partie est vide, True sinon.
        """
        self.c.execute("SELECT Donnee FROM Hero WHERE id = ?", (id,))
        return self.c.fetchone()[0] != None

    def getLastModifiedTime(self, id):
        """
        Cette fonction permet de savoir la dernière date de modification de la partie
        id : un entier entre 1 et 3, le numéro de la sauvegarde
        return : un string, la date de la dernière modification au format "D/M/Y : h:m:s" ou None
        """
        self.c.execute("SELECT DateS FROM Date WHERE id = ?", (id,))
        return self.c.fetchone()[0]


if __name__ == "__main__":

    S = SaveController()
    for i in range(1, 4):
        print(S.getLastModifiedTime(i))