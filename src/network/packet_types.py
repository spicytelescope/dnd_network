# UPDATE : The already putted values are meant to be use by default, e.g there is a default direction for example
# This is done to avoid the trace of None, which are unusable by other python client and provokes bugs

TEMPLATE_POS = {
    "name": "info_pos",
    "player_name": "Unknown_name",
    "sender_id": "Unknown_id",
    "chunkPos": [],  # [1562, 1556]
    "chunkCoor": [],  # [0, 0]
    "imagePos": 0,  # 1
    "direction": "down",
    "chunkData": {},  # TODO
}

TEMPLATE_INVENTORY = {
    "name": "info_inv",
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
    "name": "info_charac",
    "sender_id": "Unknown_id",
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
    "name": "discovery",
    "classId": 0,  # 0
    "sender_id": "Unknown_id",  # sample : 92a3c27f-4ee7-4d94-b72d-f29b501fadf4
    "map_seed": 1,
    "creator": False,
    "player_name": "Unknown_name",
}

# //TODO
TEMPLATE_TRADE_OFFER = {"name": "trade"}


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
#         "name": self.Hero.name,
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