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

void stop(char *msg){
    perror(msg);
    exit(EXIT_FAILURE);
}

/*int checkin(char *list[], char *elem){
    //check if an element elem is in the list and check if the list is complete,
    //return 1 if it's in, else -1
    int notComplete=0;
    for(int i=0; i<len(list);i++){
        if(elem==list[i])
            return i;
    }
    return -1;
}*/

int main(int argc, char *argv[]){
    /*
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
    }*/
    game_packet1 pck;

    //game_packet2 pack={0,0,0};
    char *addrc[10]; //address ip list of the clients
    int naddr;
    int fdudp;      //fd udp
    int fdtcp;      //tcp file descriptor
    fd_set fds;     //set of file descriptors
    int acivity;    //number of file descriptor active
    char msg[BUFSIZ];
    struct sockaddr_in serv, cli;

    bzero(&serv, sizeof(serv));
    if((fdudp=socket(AF_INET,SOCK_DGRAM,0))==-1)
        stop("socket");
    serv.sin_addr.s_addr=INADDR_ANY; //accept all the incoming messages
    serv.sin_family=AF_INET;
    serv.sin_port=htons(7000);

    //fdmax is the maximum number in the fd set fds
    //int fdmax=MMax(fdudp,ind)+1;
    int len=sizeof(cli);
    if(bind(fdudp, (const struct sockaddr *) &serv, sizeof(serv))==-1)
        stop("bind");
    /*
    while(1){
        //set of sockets intialisation for the select
        FD_ZERO(&fds);
        FD_SET(fdudp, &fds);
        FD_SET(ind, &fds);
        FD_SET(fdtcp,&fds);
        acivity=select(fdmax, &fds, NULL, NULL, NULL);
        if(FD_ISSET(fdudp,&fds)){
            if(recvfrom(fdudp, (char *) &msg, BUFSIZ-1,0,(struct sockaddr *) &cli,(unsigned int *) &len)<0)
                stop("recvfrom");
            //joueur déjà connecté
            if((naddr=checkin(addrc,(char *) cli.sin_addr))>=0){ 
                
            }
            //joueur non enregistré
            else if(naddr=-1){
                //données non récupérées
            }
        }
        if(FD_ISSET(ind,&fds)){

        }
    }*/
    recvfrom(fdudp,(char *) &pck, BUFSIZ-1,0,(struct sockaddr *) &cli,(unsigned int *) &len);
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
    printf("\n %d \n %d", pck.head, pck.ok);
    return 0;
}


//versions: 0 - le premier paquet set les infos invariables et les associes à un id | 1 - paquets envoyés une fois la connection établie, 4 bits du milieu de l'octet=> id du joueur