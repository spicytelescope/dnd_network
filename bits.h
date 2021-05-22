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
#define SET_CHUNKP(packet2,chunkp)   {\
    packet2.chunkP |= ((uint_fast16_t)chunkp[0]);\
    packet2.chunkP |= ((uint_fast16_t)chunkp[1] << 6);\
    packet2.chunkP &= (0xfff);\
}

#define SET_CHUNKC(packet2,chunkC)   {\
    packet2.chunkC |= ((uint_fast8_t)chunkC);\
}

#define SET_INVENTORY1(packet2,inventory1)   {\
    packet2.inventory1 |= ((uint_fast64_t)inventory1[0]);\
    packet2.inventory1 |= ((uint_fast64_t)inventory1[1] << 8);\
    packet2.inventory1 |= ((uint_fast64_t)inventory1[2] << 16);\
    packet2.inventory1 |= ((uint_fast64_t)inventory1[3] << 24);\
    packet2.inventory1 |= ((uint_fast64_t)inventory1[4] << 32);\
    packet2.inventory1 |= ((uint_fast64_t)inventory1[5] << 40);\
    packet2.inventory1 |= ((uint_fast64_t)inventory1[6] << 48);\
    packet2.inventory1 |= ((uint_fast64_t)inventory1[7] << 56);\
}

#define SET_INVENTORY2(packet2,inventory2)   {\
    packet2.inventory2 |= ((uint_fast64_t)inventory2[0]);\
    packet2.inventory2 |= ((uint_fast64_t)inventory2[2] << 8);\
    packet2.inventory2 |= ((uint_fast64_t)inventory2[2] << 16);\
    packet2.inventory2 |= ((uint_fast64_t)inventory2[3] << 24);\
    packet2.inventory2 |= ((uint_fast64_t)inventory2[4] << 32);\
    packet2.inventory2 |= ((uint_fast64_t)inventory2[5] << 40);\
    packet2.inventory2 |= ((uint_fast64_t)inventory2[6] << 48);\
    packet2.inventory2 |= ((uint_fast64_t)inventory2[7] << 56);\
}

#define SET_INVENTORY3(packet2,inventory3)   {\
    packet2.inventory3 |= ((uint_fast64_t)inventory3[0]);\
    packet2.inventory3 |= ((uint_fast64_t)inventory3[3] << 8);\
    packet2.inventory3 |= ((uint_fast64_t)inventory3[2] << 16);\
    packet2.inventory3 |= ((uint_fast64_t)inventory3[3] << 24);\
    packet2.inventory3 |= ((uint_fast64_t)inventory3[4] << 32);\
    packet2.inventory3 |= ((uint_fast64_t)inventory3[5] << 40);\
    packet2.inventory3 |= ((uint_fast64_t)inventory3[6] << 48);\
    packet2.inventory3 |= ((uint_fast64_t)inventory3[7] << 56);\
}

#define SET_INVENTORY4(packet2,inventory4)   {\
    packet2.inventory4 |= ((uint_fast64_t)inventory4[0]);\
    packet2.inventory4 |= ((uint_fast64_t)inventory4[4] << 8);\
    packet2.inventory4 |= ((uint_fast64_t)inventory4[2] << 16);\
    packet2.inventory4 |= ((uint_fast64_t)inventory4[3] << 24);\
    packet2.inventory4 |= ((uint_fast64_t)inventory4[4] << 32);\
    packet2.inventory4 |= ((uint_fast64_t)inventory4[5] << 40);\
    packet2.inventory4 |= ((uint_fast64_t)inventory4[6] << 48);\
    packet2.inventory4 |= ((uint_fast64_t)inventory4[7] << 56);\
}

#define SET_STATS1(packet2,stats)   {\
    packet2.stats1 |= ((uint_fast64_t)stats[0]);\
    packet2.stats1 |= ((uint_fast64_t)stats[1] << 8);\
    packet2.stats1 |= ((uint_fast64_t)stats[2] << 16);\
    packet2.stats1 |= ((uint_fast64_t)stats[3] << 24);\
    packet2.stats1 |= ((uint_fast64_t)stats[4] << 32);\
    packet2.stats1 |= ((uint_fast64_t)stats[5] << 40);\
    packet2.stats1 |= ((uint_fast64_t)stats[6] << 48);\
    packet2.stats1 |= ((uint_fast64_t)stats[7] << 56);\
}

#define SET_STATS2(packet2,stats)   {\
    packet2.stats2 |= ((uint_fast32_t)stats[0]);\
    packet2.stats2 |= ((uint_fast32_t)stats[1] << 8);\
    packet2.stats2 |= ((uint_fast32_t)stats[2] << 16);\
    packet2.stats2 |= ((uint_fast32_t)stats[3] << 24);\
}

#define SET_DIRECTION(packet2,direction)   {\
    packet2.direction |= ((uint_fast8_t)direction);\
    packet2.direction &= (0x3);\
}

#define SET_SPELLSID(packet2,spells)   {\
    packet2.spellsID |= ((uint_fast16_t)spells[0]);\
    packet2.spellsID |= ((uint_fast16_t)spells[1] << 5);\
    packet2.spellsID &= (0xfff);\
}

#define SET_TRADE(packet2,trade)   {\
    packet2.trade |= ((uint_fast64_t)trade[0]);\
    packet2.trade |= ((uint_fast64_t)trade[1] << 9);\
    packet2.trade |= ((uint_fast64_t)trade[2] << 57);\
    packet2.trade |= ((uint_fast64_t)trade[3] << 58);\
    packet2.trade &= (0x3fffffff);\
}


#define SET_NUM(cpy,src) {for(int u=0;u<8;u++){\
                                cpy[0] |=(((src >> u) & 0x1)<<u); \
                                cpy[1] |=(((src >> (u+8)) & 0x1)<<u); \
                                cpy[2] |=(((src >> (u+16)) & 0x1)<<u); \
                                cpy[3] |=(((src >> (u+24)) & 0x1)<<u); \
                                cpy[4] |=(((src >> (u+32)) & 0x1)<<u); \
                                cpy[5] |=(((src >> (u+40)) & 0x1)<<u); \
                                cpy[6] |=(((src >> (u+48)) & 0x1)<<u); \
                                cpy[7] |=(((src >> (u+56)) & 0x1)<<u); \
                            }\
                         }

#define host_ip "127.0.0.1"