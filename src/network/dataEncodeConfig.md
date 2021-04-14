# Data Enconding Information

```json
{
  "players": {
    "92a3c27f-4ee7-4d94-b72d-f29b501fadf4": { // 36 octets car 32 caractères (on ne compte pas les tirets), mais comme c'est de l'hexa, c'est peut être mieux de convertir d'hexa vers binaire donc 32 caractères d'hexa = 128 bits soit 16 octets
      "chunkPos": [1562, 1556], // dynamic data, limit : (1+2)*CHUNK_SIZE = 3072 -> 12 bits de 0 à 11 -> 1 octet + 4 bit
      "chunkCoor": [0, 0], // dynamic data, limit : 7 bits -> MAX = 2^7-1 = 128 max
      "inventory": {
        "storage": {"50":  [2,4]}, // dynamic data, schema : {item_id: item_pos} avec item_id : entier codé sur 1 octet, item_pos : 2 entiers de 2 (largeur_max) à 6 (hauteur_max) soit 4 bit pour la hauteur et 2 pour la largeur, nombre d'élements max : 21
        "equipment": { "0": 26, "6": 131, "8": 6 } // dynamic data, schema : {slot_id: itme_id} avec item_id : entier codé sur 1 octet, slot_id : 4 bits, nombre d'éléments max : 11
      },
      "creator": true, // constant data : 1 bit
      "characterInfo": {
        "classId": 0, // constant data : 2 bits car 3 classes dispo, 0->warrior jusqu'à 2->hunter
        "imagePos": 1, // constant data, 2 bits
        "direction": "left", // dynamic data, 2 bits 0 -> left, 1 -> right, 2 -> up, 3 -> down
        "spellsID": [2, 18], // dynamic data, max_spells=20 et max_id=19 donc 5 bits à coder pour chacun soit 10 bits en tout
        "name": "Xt", // constant data, MAX_NAME_LENGTH = 20 donc 20 octets (On est obligé d'y passer là)
        "stats": { // Pour toute ces stats, on considère le max à 255 donc 1 octet
          "STR": 17, // dynamic data
          "DEX": 10, // dynamic data
          "CON": 16, // dynamic data
          "INT": 8, // dynamic data
          "WIS": 16, // dynamic data
          "CHA": 16, // dynamic data
          "HP": 18, // dynamic data
          "HP_max": 18, // dynamic data
          "Mana": 16, // dynamic data
          "Mana_max": 16, // dynamic data
          "Money": 27, // dynamic data
          "DEF": 4, // dynamic data
          "ATK": 2 // dynamic data
        }
      },
      "mapInfo": {
        "seed": 0, // constant data, il y a normalement une infinité de valeurs, mais on va bloquer à 32 bit pour commencer, en ne considérant que des valeurs positives
        "chunkData": {} // dynamic data, on y touche pas pour l'instant
      },
      "trade": {
        "tradeInvitation": { "state": false, "to": null, "refused": false }, // dynamic data, 2 bits car "state" et "refused" sont des booleens, le champ "to" est un id donc 128 bits (voir l'id en haut)
        "tradedItems": [15, 18], // dynamic data, ne contient que des ids, max_id = 137 (soit 1 octet pour un item_id) et il y a 5 emplacements d'échanges soit 5 octets en tout
        "confirmFlag": false, // dynamic data, booleen donc 1 bit
        "tradeState": "UNDEFINED" // dynamic data, peut prendre "ACCEPTED", "REFUSED" ou "UNDEFINED", on pars du principe suivant : 0->"REFUSED", 1->"ACCEPTED", 2->"REFUSED" donc 2 bits à encoder
      }
    }
  }
}
```
