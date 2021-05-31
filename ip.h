/**
 * @file bits.c
 * @author Pithon Gabriel
 * @brief 
 * @version 0.1
 * @date 2021-03-18
 * 
 * @copyright Copyright (c) 2021
 * 
 */

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
    int type;               //type=0
    in_addr_t addr;
    long long int id;
}newP_packet;

typedef struct{
    int type;
    int nb_connections;
}ini_packet;


#define 	MMax(x,y) (x>y ? x:y)

char *fifo_output_path = "/tmp/info_output";
char *fifo_input_path = "/tmp/info_intput";
/**
 * @struct game_packet1
 * 
 * @brief
 * this structure contains the first packet to send when you start a connection  with someone else, it contains the statics data
 *  
 */
typedef struct{
    int head[10];
    int ok;

}   game_packet1;

/**
 * @struct game_packet2
 * @brief 
 *  this structure contains all the dynamic values,the purpose is to send it quickly and frequently
 *  "chunkP": [1562, 1556] 12 bits
 *  "chunkC": 7 bits
 *  "inventory": {
 *      "storage": (id of the item*nb slots) 8*21=168 bits, the first bytes is for the first slot and so on
 *      "equipment": (id of the item*nb slots) 8*11=88 bits, the first bytes is for the first slot and so on
 *  } => datas saves in 4*8 bytes the 168 first bits for the storage and the 88 last for the equipment
 *  "stats": {
 *      "stats1": {
 *          "STR":  1st byte
 *          "DEX":  2nd byte
 *          "CON":  3rd byte
 *          "INT":  4th byte
 *          "WIS":  5th byte
 *          "CHA":  6th byte
 *          "HP":  7th byte
 *          "HP_max":  8th byte 
 *      }
 *      "stats2":{
 *          "Mana":  1st byte 
 *          "Mana_max":  2nd byte
 *          "Money":  3rd byte
 *          "DEF":   4th byte / 2 firsts bits
 *          "ATK":  4th byte / 2 seconds bits
 *      }
 *  }
 *  "Direction": 2 bits 0 -> left, 1 -> right, 2 -> up, 3 -> down in 8 bits structure
 *  "spells": 10 bits    in 16 bits structure
 *  "trade" :{
 *      "tradeInvitation": state : 1 bits, to : 7 bits and refused : 1 bits ==> 9 bits
 *      "tradedItems": 5 items, so 5*id (8 bits)
 *      "confirmFlag": 1 bit (y/n)
 *      "tradeState" : 0->"REFUSED", 1->"ACCEPTED", 2->"REFUSED" ==> 2 bits
 * } ==> 64 bits structure : 9 firsts tradeInvitation, 48 next tradedItems, 1 next confirmFlag and the 2 next tradeState
 */

typedef struct{
    uint_fast8_t head;
    int chunkP;
    uint_fast8_t chunkC;
    uint_fast64_t inventory1;
    uint_fast64_t inventory2;
    uint_fast64_t inventory3;
    uint_fast64_t inventory4;
    uint_fast64_t stats1;
    uint_fast32_t stats2;
    uint_fast8_t direction;
    uint_fast16_t spellsID;
    uint_fast64_t trade;
}   game_packet2;

#define SET_version(packet,h) ( packet.head |= ( h << 2) )
#define IS_SET_BIT(section,pos) ((section >> pos) & 0x1 )


#define host_ip "127.0.0.1"