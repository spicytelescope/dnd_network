# Dnd Networking Project

ZEBI
ZEBIx2

notes:
client.c renvoit tout ce qui est ecrit dans le pipe "info_input" et le renvoit dans le pipe "info_output"

du coup faut utiliser la fonction select et y mettre le file descriptor de info output et tous les sock id

puis si il se passe qqch dans le pipe "info_output" il faut erecupérer l'info et l'envoyer sur le réeau et si une info arrive de réseau faut la mettre dans le pipe "info-input"