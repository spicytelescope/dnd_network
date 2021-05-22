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

#define SET_NUM2(cpy,src) {for(int u=0;u<8;u++){\
                                cpy |=(((src >> (u+8)) & 0x1)<<u); \
                                printf("%d\n",cpy);\
                            }\
                         }


// set the stats1 of game_packet2
#define SET_STATS1(packet2,stats)   {\
                    packet2.stats1 |= ((uint64_t)stats[0]);\
                    packet2.stats1 |= ((uint64_t)stats[1] << 8);\
                    packet2.stats1 |= ((uint64_t)stats[2] << 16);\
                    packet2.stats1 |= ((uint64_t)stats[3] << 24);\
                    packet2.stats1 |= ((uint64_t)stats[4] << 32);\
                    packet2.stats1 |= ((uint64_t)stats[5] << 40);\
                    packet2.stats1 |= ((uint64_t)stats[6] << 48);\
                    packet2.stats1 |= ((uint64_t)stats[7] << 56);\
                    }
#define host_ip "127.0.0.1"

void stop(char *msg){
    perror(msg);
    exit(EXIT_FAILURE);
}

int checkin(int *list, int elem){
    //check if an element elem is in the list and check if the list is complete,
    //return i if it's in, else -1
    for(int i=0; i<10;i++){
        if(elem==list[i])
            return i;
    }
    return -1;
}


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
    game_packet1 pack;
    memset(&pack,0,sizeof(game_packet1));
    pack.head[2]=10;
    pack.ok=2;
    int sfd;
    int stats[]={10,17,24,15,5,37,23,23};
    struct sockaddr_in cli;
    bzero(&cli, sizeof(cli));
    if((sfd=socket(AF_INET,SOCK_DGRAM,0))==-1)
        stop("socket");
    if(!inet_aton(host_ip,&(cli.sin_addr)))
        stop("adress ip");
    cli.sin_family=AF_INET;
    cli.sin_port=htons(7000);
    /*SET_STATS1(pack,stats);
    for(int i=0;i<64;i++){
        if(IS_SET_BIT(pack.stats1,i)){
            printf("+");
        }
        else{
            printf(".");
        }
    }*/
    int len=sizeof(cli);
    uint8_t n[]={0,0,0,0,0,0,0,0};
    //SET_NUM(n,pack.stats1);
    sendto(sfd,(char *) &pack,sizeof(pack),0,(struct sockaddr *) &cli, len);
    in_addr_t a[10];
    memcpy(&a[3], &cli.sin_addr.s_addr, sizeof(cli));
    int u=checkin(&a,cli.sin_addr.s_addr);
    printf("%d %d", pack.head[2], u);
    return 0;
}
