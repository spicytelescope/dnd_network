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

#include "bits.h"

#define CONNECTIONS_MAX 10
#define PORT_UDP 7000
#define PORT_TCP 8000

void stop(char *msg){
    perror(msg);
    exit(EXIT_FAILURE);
}

int is_complete(int *array, int len, int nbNull){
    for(int i; i<len; i++){
        if(array[i]==nbNull){
            return 0;
        }
    }
    return 1;
}

int confirmation(int fd){

}

int checkin(in_addr_t list[], in_addr_t elem){
    //check if an element elem is in the list and check if the list is complete,
    //return i if it's in, else -1
    for(int i=0; i<CONNECTIONS_MAX;i++){
        if(elem==list[i])
            return i;
    }
    return -1;
}

int main(int argc, char *argv[]){
    // Create the fifo needed to get informations from the game
    if (mkfifo(fifo_output_path, 0777) == -1)
    {
        if (errno != EEXIST)
        {
            perror("mkfifo");
            exit(EXIT_FAILURE);
        }
    }
    if (mkfifo(fifo_input_path, 0777) == -1)
    {
        if (errno != EEXIST)
        {
            perror("mkfifo");
            exit(EXIT_FAILURE);
        }
    }
    // Open the fifo    
    int ind, outd;
    if ((ind = open(fifo_output_path, O_RDONLY)) == -1)
    {
        perror("open");
        exit(EXIT_FAILURE);
    }
    if ((outd = open(fifo_input_path, O_WRONLY)) == -1)
    {
        perror("open");
        exit(EXIT_FAILURE);
    }
    game_packet1 pck;

    int fd_connect[CONNECTIONS_MAX]; //fd sockets under connection
    int new_sock;       //fd socket new connect 
    in_addr_t under_connect[CONNECTIONS_MAX]; //temporaly saves the ip adress not connected yet
    //game_packet2 pack={0,0,0};
    in_addr_t addrc[CONNECTIONS_MAX]; //address ip list of the clients
    long long int idc[CONNECTIONS_MAX]; // id associated to the ip address
    memset(fd_connect,-1,sizeof(fd_connect));
    memset(under_connect,0,sizeof(under_connect));
    memset(addrc,0,sizeof(addrc));


    //file descriptors
    int naddr;
    int fdudp;      //fd udp
    int fdtcp;      //tcp file descriptor
    fd_set fds;     //set of file descriptors
    int acivity;    //number of file descriptor active
    char msg[BUFSIZ];
    struct sockaddr_in servUdp, servTcp, cli;
    char buffer[BUFSIZ];

    //UDP
    bzero(&servUdp, sizeof(servUdp));
    if((fdudp=socket(AF_INET,SOCK_DGRAM,0))==-1)
        stop("socket");
    servUdp.sin_addr.s_addr=INADDR_ANY; //accept all the incoming messages
    servUdp.sin_family=AF_INET;
    servUdp.sin_port=htons(PORT_UDP);
    if(bind(fdudp, (const struct sockaddr *) &servUdp, sizeof(servUdp))==-1)
        stop("bind udp");

    //TCP
    if((fdtcp=socket(AF_INET,SOCK_STREAM,0))==-1)
        stop("socket");
    if(setsockopt(fdtcp, SOL_SOCKET, SO_REUSEADDR, (char *) 1, sizeof((char *) 1)<0)){
        stop("setsockopt");
    }
    servTcp.sin_addr.s_addr=INADDR_ANY; //accept all the incoming messages
    servTcp.sin_family=AF_INET;
    servTcp.sin_port=htons(PORT_TCP);
    if(bind(fdtcp, (const struct sockaddr *) &servTcp, sizeof(servUdp))==-1)
        stop("bind tcp");
    if(listen(fdtcp,10)<0){
        stop("listen");
    }
    //connection(ip dest)
    //fdmax is the maximum number in the fd set fds
    int fdmax=MMax(fdudp,ind);
    fdmax=MMax(fdmax,fdtcp);
    int len=sizeof(cli);

    
    //select loop
    while(1){
        //set of sockets intialisation for the select
        FD_ZERO(&fds);
        for(int con=0; con<CONNECTIONS_MAX; con++){
            if(fd_connect[con]>0){
                FD_SET(fd_connect[con],&fds);
                fdmax=MMax(fd_connect[con],fdmax);
            }
        }
        FD_SET(fdudp, &fds);
        FD_SET(ind, &fds);
        FD_SET(fdtcp,&fds);
        acivity=select(fdmax, &fds, NULL, NULL, NULL);
        int addrlen= sizeof(cli);
        //TCP socket for the new connections
        if(FD_ISSET(fdtcp,&fds)){
            if((new_sock=accept(fdtcp,(struct sockaddr *) &cli, (socklen_t *) addrlen))<0){
                stop("accept");
            }
            if((naddr=checkin(under_connect, cli.sin_addr.s_addr))!=-1){
                char msg=0x00;
                send(new_sock, &msg, 1,0);
            }
            else if((naddr=checkin(addrc, cli.sin_addr.s_addr)!=-1)){
                char msg= 0x00;
                send(new_sock, &msg, 1,0);
            }
            else{
                for(int con=0;con<CONNECTIONS_MAX;con++){
                    if(fd_connect[con]==-1){
                        fd_connect[con]=new_sock;
                        under_connect[con]=cli.sin_addr.s_addr;
                        memset(&cli, 0, sizeof(cli));
                        char msg= 0xff; //plus que ça en vrai
                        send(new_sock, &msg, 1,0);
                        for(int u=0;u<CONNECTIONS_MAX;u++){
                            if(addrc[u]!=0){
                                sendto(fdudp,"packet",7,0,);
                            }
                        }
                        break;
                    }
                }
            }
        }
        for(int con=0;con<CONNECTIONS_MAX;con++){
            if(FD_ISSET(fd_connect[con],&fds)){
                confirmation(fd_connect);
            }
        }
        


        //UDP socket for the registered players
        if(FD_ISSET(fdudp,&fds)){
            if(recvfrom(fdudp, (char *) &msg, BUFSIZ+1,0,(struct sockaddr *) &cli,(unsigned int *) &len)<0)
                stop("recvfrom");
            //player already connected 
            if((naddr=checkin(addrc, cli.sin_addr.s_addr))>=0){ 
                
            }
            //player unknown
            else if(naddr=-1){
                //data deleted
            }
        }
        if(FD_ISSET(ind,&fds)){

        }
    }


    recvfrom(fdudp,(char *) &buffer, BUFSIZ-1,0,(struct sockaddr *) &cli,(unsigned int *) &len);
    if(buffer[0] == 0x1){
        for(int i=0;i<8;i++){
            if(IS_SET_BIT((char) *buffer,i)){
                printf("+");
            }
            else{
                printf(".");
            }
        }
        memcpy(&pck,&buffer,sizeof(game_packet1));
    }
    /*
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
    */
    printf("\n %d \n %d", pck.head[2], pck.ok);
    return 0;
}


//versions: 0 - le premier paquet set les infos invariables et les associes à un id | 1 - paquets envoyés une fois la connection établie, 4 bits du milieu de l'octet=> id du joueur