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
#include <sys/ioctl.h>

#define CONNECTIONS_MAX 10
#define PORT_UDP 7000
#define PORT_TCP 8000
#define host_ip "127.0.0.1"
#define ID_LEN 16
#define BUFSIZE 1024
#define UNKNOWN_ID "unknown_id"

typedef struct
{
    long long int id;
} static_packet;

typedef struct
{
    int type;          //type=1
    int chunkPos[2];   //position of the chunk
    int chunkCoord[2]; //coord of the player inside the chunk
    char direction;    //0 left, 1
} packet_pos;

typedef struct
{
    int type;          //type=2
    int storage[21];   //storage
    int equipment[11]; //equipment
    int status;        //0 free to interact, 1 not avaible yet
    int stats[13];     //STR, DEX, CON, INT, WIS, CHA, HP, HP_MAX, Mana, Mana_max, Money, DEF, ATK
    uint_fast8_t direction;
    uint_fast16_t spellsID;
    uint_fast64_t trade;
} packet_info;

typedef struct
{

} packet_trade;

typedef struct
{
    int type; //type=1
    int indice;
    char selfID[ID_LEN];
    in_addr_t players_addr[CONNECTIONS_MAX];
    char players_id[CONNECTIONS_MAX][ID_LEN];
} newP_packet;

typedef struct
{
    int type; //type=2
    in_addr_t adrrn;
} new_packet; //use to send new player to others players

#define MMax(x, y) (x > y ? x : y)

char *fifo_output_path = "/tmp/info_output";
char *fifo_input_path = "/tmp/info_input";

#define SET_version(packet, h) (packet.head |= (h << 2))
#define IS_SET_BIT(section, pos) ((section >> pos) & 0x1)

#define DECONNECTION_TIMEOUT_BYTES 0xfb
#define DECONNECTION_MANUAL_BYTES 0xfc

void stop(char *msg)
{
    perror(msg);
    exit(EXIT_FAILURE);
}
