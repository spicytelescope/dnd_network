from config.netConf import CHAT_COLORS

# UPDATE : The already putted values are meant to be use by default, e.g there is a default direction for example
# This is done to avoid the trace of None, which are unusable by other python client and provokes bugs

TEMPLATE_POS = {
    "type": "info_pos",
    "player_name": "Unknown_name",
    "sender_id": "Unknown_id",
    "chunkPos": [],  # [1562, 1556]
    "chunkCoor": [],  # [0, 0]
    "imagePos": 0,  # 1
    "direction": "down",
    "currentPlace": "openWorld",
    "buildingPos": [],
    "chunkData": {},  # TODO
}

TEMPLATE_INVENTORY = {
    "type": "info_inv",
    "sender_id": "Unknown_id",
    "storage": {
        # "50": [2, 4]
    },
    "equipment": {
        # "0": 26,
        # "6": 131,
        # "8": 6,
    },
}

TEMPLATE_CHARACTER_INFO = {
    "type": "info_charac",
    "sender_id": "Unknown_id",
    "chunkPos": [],  # [1562, 1556]
    "storage": {
        # "50": [2, 4]
    },
    "equipment": {
        # "0": 26,
        # "6": 131,
        # "8": 6,
    },
    "spellsID": [
        # 2,
        # 18,
    ],
    "stats": {  # -1 means unset
        "STR": -1,
        "DEX": -1,
        "CON": -1,
        "INT": -1,
        "WIS": -1,
        "CHA": -1,
        "HP": -1,
        "HP_max": -1,
        "Mana": -1,
        "Mana_max": -1,
        "Money": -1,
        "DEF": -1,
        "ATK": -1,
    },
}

# This packet must be the first one to be send, when joining a LAN -> Discovery packet
TEMPLATE_NEW_CONNECTION = {
    "type": "discovery",
    "classId": 0,  # 0
    "sender_id": "Unknown_id",  # sample : 92a3c27f-4ee7-4d94-b72d-f29b501fadf4
    "map_seed": 1,
    "spellsID": [
        # 2,
        # 18,
    ],
    "stats": {  # -1 means unset
        "STR": -1,
        "DEX": -1,
        "CON": -1,
        "INT": -1,
        "WIS": -1,
        "CHA": -1,
        "HP": -1,
        "HP_max": -1,
        "Mana": -1,
        "Mana_max": -1,
        "Money": -1,
        "DEF": -1,
        "ATK": -1,
    },
    "player_name": "Unknown_name",
    "storage": {
        # "50": [2, 4]
    },
    "equipment": {
        # "0": 26,
        # "6": 131,
        # "8": 6,
    }
}

TEMPLATE_DECONNEXION = {
    "type": "deconnection",
    "sender_id": "Unknown_id",
    "player_name": "Unknown_name",
}

TEMPLATE_MESSAGE = {
    "type": "message",
    "sender_id": "Unknown_id",  # To retrieve the type afterward, and display it in the chat;
    "content": "",
    "color_code": "DEFAULT",
    "italic": False,
}

TEMPLATE_FIGHT = {
    "type": "fight",
    "sender_id": "Unknown_id",
    "action_type": "MOVEMENT",
    "dest": 15,
}

# //TODO
TEMPLATE_TRADE_OFFER = {"type": "trade"}


# OLD :

# BASE SCHEME
# data["players"][self.Hero.networkId] = {
#     "chunkPos": self.Hero.posMainChunkCenter,
#     "chunkCoor": self.Hero.Map.chunkData["currentChunkPos"],
#     "inventory": {"storage": {}, "equipment": {}},
#     "creator": not any(
#         [player["creator"] for player in data["players"].values()]
#     ),
#     "characterInfo": {
#         "classId": self.Hero.classId,
#         "imagePos": self.Hero.imageState["imagePos"],
#         "direction": self.Hero.direction,
#         "spellsID": self.Hero.spellsID,
#         "type": self.Hero.type,
#         "stats": self.Hero.stats,
#     },
#     "mapInfo": {
#         "seed": self.Map.mapSeed
#         if not any([player["creator"] for player in data["players"].values()])
#         else None,
#         "chunkData": {},
#     },
#     "trade": {
#         "tradeInvitation": {"state": False, "to": None, "refused": False},
#         "tradedItems": [],
#         "confirmFlag": False,  # Flag send when player 1 lock and ask for confirmation
#         "tradeState": "UNDEFINED",  # Flag send when player 2 accept the trade
#     },
# }
