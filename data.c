#include <dirent.h>
#include <fcntl.h>
#include <grp.h>
#include <math.h>
#include <pwd.h>
#include <sys/stat.h>
#include <sys/wait.h>
#include <stdio.h>
#include <stdint.h>
#include <string.h> //strlen
#include <stdlib.h>
#include <errno.h>
#include <unistd.h>    //close
#include <arpa/inet.h> //close
#include <sys/types.h>
#include <sys/socket.h>
#include <netinet/in.h>
#include <sys/time.h> //FD_SET, FD_ISSET, FD_ZERO macros
#include <netinet/in.h>
#include <netdb.h>
#include <time.h>



typedef struct{
    long long int id;
}static_packet;

typedef struct{
    int type;               //type=1    
    int chunkPos[2];        //position of the chunk
    int chunkCoord[2];      //coord of the player inside the chunk
    char direction;         //0 left, 1
}packet_pos;

typedef struct{
    int type;               //type=2
    int storage[21];        //storage
    int equipment[11];      //equipment
    int status;             //0 free to interact, 1 not avaible yet
    int stats[13];          //STR, DEX, CON, INT, WIS, CHA, HP, HP_MAX, Mana, Mana_max, Money, DEF, ATK
    uint_fast8_t direction; 
    uint_fast16_t spellsID; 
    uint_fast64_t trade;
}  packet_info;

typedef struct{

}packet_trade;



typedef struct{
    int type;
    int nb_connections;
}ini_packet;

