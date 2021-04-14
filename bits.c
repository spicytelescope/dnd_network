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

#define SET_version(packet,h) ( packet.head |= ( h << 2) )
#define IS_SET_BIT(section,pos) ((section >> pos) & 0x1 )
#define SET_STATS1(packet2,stats)   {\
                    packet2.stats2 |= (stats[0]);\
                    packet2.stats2 |= (stats[1] << 8);\
                    packet2.stats2 |= (stats[2] << 16);\
                    packet2.stats2 |= (stats[3] << 24);\
                    packet2.stats2 |= (stats[4] << 32);\
                    packet2.stats2 |= (stats[5] << 40);\
                    packet2.stats2 |= (stats[6] << 48);\
                    packet2.stats2 |= (stats[7] << 56);\
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

void stop(char *msg){
    perror(msg);
    exit(EXIT_FAILURE);
}


/**
 * @struct game_packet1
 * 
 * @brief
 * this structure contains the first packet to send when you start a connection  with someone else, it contains the statics data
 *  
 */
typedef struct{
    uint8_t head;

}   game_packet1;
/**
 * @struct game_packet2
 * @brief 
 * this structure contains all the dynamic values,the purpose is to send it quickly and frequently
 * "stats1": {
          "STR":  1st byte
          "DEX":  2nd byte
          "CON":  3rd byte
          "INT":  4th byte
          "WIS":  5th byte
          "CHA":  6th byte
          "HP":  7th byte
          "HP_max":  8th byte 
    }
    stats2{
          "Mana":  1st byte 
          "Mana_max":  2nd byte
          "Money":  3rd byte
          "DEF":   4th byte / 2 firsts bits
          "ATK":  4th byte / 2 seconds bits
    }
 */
typedef struct{
    uint8_t head;
    uint64_t stats1;
    uint32_t stats2;
}   game_packet2;

int main(int argc, char *argv[]){
    game_packet2 pack={0,0,0};
    int sfd;
    struct sockaddr_in serv, cli;
    bzero(&serv, sizeof(serv));
    if((sfd=socket(AF_INET,SOCK_DGRAM,0))==-1)
        stop("socket");
    serv.sin_addr.s_addr=INADDR_ANY;
    serv.sin_family=AF_INET;
    serv.sin_port=htons(7000);
    for(int i=0;i<8;i++){
        if(IS_SET_BIT(pack.head,i)){
            printf("+");
        }
        else{
            printf(".");
        }
    }
    printf("\n \n");
    int len=sizeof(cli);
    bind(sfd, (const struct sockaddr *) &serv, sizeof(serv));
    recvfrom(sfd, (char *) &pack, BUFSIZ-1,0,(struct sockaddr *) &cli,(unsigned int *) &len);
    for(int i=0;i<64;i++){
        if(IS_SET_BIT(pack.stats1,i)){
            printf("+");
        }
        else{
            printf(".");
        }
    }
    uint32_t n[]={0,0,0,0};
    SET_NUM(n,pack.stats1);
    printf("\n %d \n %d \n %d \n %d \n", n[0], n[1], n[2], n[3]);
    return 0;
}


//versions: 0 - le premier paquet set les infos invariables et les associes à un id | 1 - paquets envoyés une fois la connection établie, 4 bits du milieu de l'octet=> id du joueur