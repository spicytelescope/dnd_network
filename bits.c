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

#include "ip.h"

void stop(char *msg)
{
    perror(msg);
    exit(EXIT_FAILURE);
}

int is_complete(int *array, int len, int nbNull)
{
    for (int i; i < len; i++)
    {
        if (array[i] == nbNull)
        {
            return 0;
        }
    }
    return 1;
}

int confirmation(int fdt, int fdu, char *addressH, struct sockaddr_in hote, struct sockaddr_in udpcli, in_addr_t *addrcli, long long int *idc, long long int selfID)
{
    int activity;
    int nb_addr = 0;
    char message[BUFSIZ];
    hote.sin_port = htons(PORT_TCP);
    fd_set fds;
    if (!inet_aton(addressH, &(hote.sin_addr)))
        stop("inet_aton");
    socklen_t lh = sizeof(hote);
    if (connect(fdt, (struct sockaddr *)&hote, lh) == -1)
        stop("connect");
    recv(fdt, &message, BUFSIZ + 1, 0);
    if ((int)*message == 1)
    {
        printf("ok\n");
        addrcli[(int)*(message + 4)] = hote.sin_addr.s_addr;
        idc[(int)*(message + 4)] = (int)*(message + 8);
        //send id to pipe
        for (int i = 0; i < CONNECTIONS_MAX + 4; i++)
        {
            if ((in_addr_t) * (message + 4 * i + 16) != 0)
            {
                addrcli[i] = (in_addr_t) * (message + i * 4 + 16);
                idc[i] = (long long int)*(message + 56 + i * 4);
                nb_addr++;
            }
        }
        if (nb_addr == 0)
            send(fdt, "ok", 3, 0);
    }
    else
        return -1;
    sleep(5);
    for (int i = 0; i < CONNECTIONS_MAX; i++)
    {
        if (addrcli[i] != 0)
        {
            udpcli.sin_addr.s_addr = addrcli[i];
            sendto(fdu, (char *)&selfID, sizeof(long long int), 0, (struct sockaddr *)&udpcli, sizeof(udpcli));
        }
    }
    int lencli = sizeof(udpcli);
    printf("ok\n");
    while (1)
    {
        if (nb_addr != 0)
        {
            recvfrom(fdu, &message, 3, 0, (struct sockaddr *)&udpcli, (socklen_t *)&lencli);
            nb_addr--;
        }
        if (nb_addr == 0)
        {
            send(fdt, "ok", 3, 0);
            close(fdt);
            return 0;
        }
        //count (7 for exemple)
        //check the reponse of the others servers
        // pas oublier de close !!!
    }
    /*while (1)
    {
        printf("ok\n");
        //condition if all the server are find
        FD_ZERO(&fds);
        FD_SET(fdt, &fds);
        FD_SET(fdu, &fds);
        printf("ok\n");
        activity = select(fdmax, &fds, NULL, NULL, NULL);
        printf("ok\n");
        int lencli = sizeof(udpcli);
        printf("ok\n");
        if (FD_ISSET(fdt, &fds))
        {
            printf("ok\n");
            recv(fdt, &message, BUFSIZ + 1, 0);

            if ((int)*message == 1)
            {
                addrcli[(int)*(message + 4)] = hote.sin_addr.s_addr;
                idc[(int)*(message + 4)] = (int)*(message + 8);
                //send id to pipe
                for (int i = 0; i < CONNECTIONS_MAX + 4; i++)
                {
                    if ((in_addr_t) * (message + 4 * i + 16) != 0)
                    {
                        addrcli[i] = (in_addr_t) * (message + i * 4 + 16);
                        idc[i] = (long long int)*(message + 56 + i * 4);
                        nb_addr++;
                    }
                }
                if (nb_addr == 0)
                    send(fdt, "ok", 3, 0);
            }
            else
                return -1;
            //first com
            //first->recieve id and the number of the other player with their id
            //send to pipe id
            sleep(5);
            for (int i = 0; i < CONNECTIONS_MAX; i++)
            {
                if (addrcli[i] != 0)
                {
                    udpcli.sin_addr.s_addr=addrcli[i];
                    sendto(fdu, (char *)&selfID, sizeof(long long int), 0, (struct sockaddr *)&udpcli, sizeof(udpcli));
                }
            }
        }
        if (FD_ISSET(fdu, &fds))
        {
            recvfrom(fdu, &message, 3, 0, (struct sockaddr *)&udpcli,(socklen_t *) &lencli);
            nb_addr--;
            if (nb_addr == 0)
            {
                send(fdt, "ok", 3, 0);
            }
            //count (7 for exemple)
            //check the reponse of the others servers
            // pas oublier de close !!!
        }
    }*/

    //connection TCP
    //confirmation UDP
    return 0;
}

int checkin(in_addr_t list[], in_addr_t elem)
{
    //check if an element elem is in the list and check if the list is complete,
    //return i if it's in, else -1
    for (int i = 0; i < CONNECTIONS_MAX; i++)
    {
        if (elem == list[i])
            return i;
    }
    return -1;
}

int main(int argc, char *argv[])
{
    // Create the fifo needed to get informations from the game
    /*
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
    // Open the fifo*/
    int ind = 7, outd; /*
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

    //all the packets

    long long int selfID = 12;
    newP_packet newp;
    new_packet new;
    int indice_temp = -1;

    int true = 1;
    int complete = 0;
    int fd_connect[CONNECTIONS_MAX];          //fd sockets under connection
    int new_sock;                             //fd socket new connect
    in_addr_t under_connect[CONNECTIONS_MAX]; //temporaly saves the ip adress not connected yet
    //game_packet2 pack={0,0,0};
    in_addr_t addrc[CONNECTIONS_MAX];   //address ip list of the clients
    long long int idc[CONNECTIONS_MAX]; // id associated to the ip address
    memset(fd_connect, -1, sizeof(fd_connect));
    memset(under_connect, 0, sizeof(under_connect));
    memset(addrc, 0, sizeof(addrc));

    //file descriptors
    int naddr;
    int fdudp;   //fd udp
    int fdtcp;   //tcp file descriptor
    fd_set fds;  //set of file descriptors
    int acivity; //number of file descriptor active
    char msg[BUFSIZ];
    struct sockaddr_in servUdp, servTcp, cliTCP, cliUDP;
    char buffer[BUFSIZ];

    //UDP
    bzero(&servUdp, sizeof(servUdp));
    if ((fdudp = socket(AF_INET, SOCK_DGRAM, 0)) == -1)
        stop("socket");
    servUdp.sin_addr.s_addr = INADDR_ANY; //accept all the incoming messages
    servUdp.sin_family = AF_INET;
    servUdp.sin_port = htons(PORT_UDP);
    cliUDP.sin_family = AF_INET;
    cliUDP.sin_port = htons(PORT_UDP);
    if (bind(fdudp, (const struct sockaddr *)&servUdp, sizeof(servUdp)) == -1)
        stop("bind udp");

    //TCP
    if ((fdtcp = socket(AF_INET, SOCK_STREAM, 0)) == -1)
        stop("socket");
    if (setsockopt(fdtcp, SOL_SOCKET, SO_REUSEADDR, &true, sizeof(int)) < 0)
    {
        stop("setsockopt tcp");
    }
    servTcp.sin_family = AF_INET;
    servTcp.sin_port = htons(PORT_TCP);
    //confirmation if failed stop the program
    if (argc == 2)
    {
        cliTCP.sin_family = AF_INET;
        cliTCP.sin_port = htons(PORT_TCP);
        printf("%s\n", argv[1]);
        confirmation(fdtcp, fdudp, argv[1], cliTCP, cliUDP, addrc, idc, selfID);
        for (int i = 0; i < CONNECTIONS_MAX; i++)
        {
            printf("%d\n", addrc[i]);
        }
    }
    if ((fdtcp = socket(AF_INET, SOCK_STREAM, 0)) == -1)
        stop("socket");
    if (setsockopt(fdtcp, SOL_SOCKET, SO_REUSEADDR, &true, sizeof(int)) < 0)
    {
        stop("setsockopt tcp");
    }
    servTcp.sin_family = AF_INET;
    servTcp.sin_port = htons(PORT_TCP);
    //confirmation if failed stop the program
    servTcp.sin_addr.s_addr = INADDR_ANY; //accept all the incoming messages
    if (bind(fdtcp, (const struct sockaddr *)&servTcp, sizeof(servTcp)) == -1)
        stop("bind tcp");
    if (listen(fdtcp, 10) < 0)
    {
        stop("listen");
    }
    //connection(ip dest)
    //fdmax is the maximum number in the fd set fds
    int fdmax = MMax(fdudp, ind);
    fdmax = MMax(fdmax, fdtcp);
    int len = sizeof(cliTCP);

    //select loop
    while (1)
    {
        //set of sockets intialisation for the select
        FD_ZERO(&fds);
        for (int con = 0; con < CONNECTIONS_MAX; con++)
        {
            if (fd_connect[con] > 0)
            {
                FD_SET(fd_connect[con], &fds);
                fdmax = MMax(fd_connect[con], fdmax);
            }
        }
        FD_SET(fdudp, &fds);
        FD_SET(ind, &fds);
        FD_SET(fdtcp, &fds);
        acivity = select(fdmax, &fds, NULL, NULL, NULL);
        int addrlen = sizeof(cliTCP);

        //TCP socket for the new connections
        if (FD_ISSET(fdtcp, &fds))
        {
            if ((new_sock = accept(fdtcp, (struct sockaddr *)&cliTCP, (socklen_t *)&addrlen)) < 0)
            {
                stop("accept");
            }
            printf("ok\n");
            if ((naddr = checkin(under_connect, cliTCP.sin_addr.s_addr)) != -1)
            {
                char message = 0x00;
                send(new_sock, &message, 1, 0);
            }
            else if ((naddr = checkin(addrc, cliTCP.sin_addr.s_addr) != -1))
            {
                char message = 0x00;
                send(new_sock, &message, 1, 0);
            }
            else
            {
                for (int con = 0; con < CONNECTIONS_MAX; con++)
                {
                    if (addrc[con] == 0)
                        break;
                    if (con == 9)
                        complete = 1;
                }
                if (complete == 0)
                {
                    for (int con = 0; con < CONNECTIONS_MAX; con++)
                    {
                        if (fd_connect[con] == -1)
                        {
                            fd_connect[con] = new_sock;
                            under_connect[con] = cliTCP.sin_addr.s_addr;
                            memset(&cliTCP, 0, sizeof(cliTCP));
                            memset(&newp, -1, sizeof(newp));
                            newp.type = 1;
                            newp.indice = con;
                            newp.selfID = selfID;
                            for (int n; n < CONNECTIONS_MAX; n++)
                            {
                                if (addrc[n] != -1)
                                {
                                    newp.players_addr[n] = addrc[n];
                                    newp.players_id[n] = idc[n];
                                }
                            }
                            for (int u = 0; u < CONNECTIONS_MAX; u++)
                            {
                                if (addrc[u] != 0)
                                {
                                    cliUDP.sin_addr.s_addr = addrc[u];
                                    new.type = 2;
                                    new.adrrn = under_connect[con];
                                    sendto(fdudp, (char *)&(new), sizeof(new), 0, (struct sockaddr *)&cliUDP, (unsigned int)len);
                                }
                            }
                            if (send(new_sock, &newp, sizeof(newp), 0) == -1)
                                stop("send");
                            break;
                        }
                    }
                }
                complete = 0;
            }
        }
        for (int con = 0; con < CONNECTIONS_MAX; con++)
        {
            if (FD_ISSET(fd_connect[con], &fds))
            {
                recv(fd_connect[con], &msg, BUFSIZ + 1, 0);
                if (indice_temp == 0)
                {
                    for (int i = 0; i < CONNECTIONS_MAX; i++)
                    {
                        if (addrc[i] != 0)
                        {
                            memcpy(&cliUDP.sin_addr.s_addr, &addrc[i], sizeof(addrc[i]));
                            sendto(fdudp, "ok", 3, 0, (struct sockaddr *)&cliUDP, (unsigned int)len);
                        }
                    }
                }
                for (int i = 0; i < CONNECTIONS_MAX; i++)
                {
                    if (addrc[i] == 0)
                    {
                        addrc[i] = under_connect[con];
                        fd_connect[con] = 0;
                        printf("%d\n", addrc[i]);
                        break;
                    }
                }
            }
        }

        //UDP socket for the registered players
        if (FD_ISSET(fdudp, &fds))
        {
            if (recvfrom(fdudp, (char *)&msg, BUFSIZ + 1, 0, (struct sockaddr *)&cliUDP, (unsigned int *)&len) < 0)
                stop("recvfrom");
            //player already connected
            if ((naddr = checkin(under_connect, cliUDP.sin_addr.s_addr)) >= 0)
            {
                //new connection
                if (indice_temp != -1)
                {
                    addrc[indice_temp] = 0;
                    idc[indice_temp] = 0;
                }
                for (int i = 0; i < CONNECTIONS_MAX; i++)
                {
                    if (addrc[i] == 0)
                    {
                        indice_temp = i;
                        addrc[indice_temp] = cliUDP.sin_addr.s_addr;
                        idc[indice_temp] = (long long int)*msg; //send id
                    }
                }
                sendto(fdudp, "ok", 3, 0, (struct sockaddr *)&cliUDP, sizeof(cliUDP));
                //set son id
            }
            else if ((naddr = checkin(addrc, cliUDP.sin_addr.s_addr)) >= 0)
            {
                if (*msg && 'o')
                {
                    indice_temp = -1;
                }
                else if ((int)*msg && 2)
                {
                    for (int n = 0; n < CONNECTIONS_MAX; n++)
                    {
                        if (under_connect[n] == 0)
                        {
                            under_connect[n] = (int)*(msg + 4);
                            break;
                        }
                    }
                }
                else if (*msg && 0xfc)
                {
                    for (int i = 0; i < CONNECTIONS_MAX; i++)
                    {
                        if (addrc[i] == cliUDP.sin_addr.s_addr)
                        {
                            addrc[i] == 0;
                            idc[i] == 0;
                            break;
                        }
                    }
                }
            }
            //player unknown
            else if (naddr == -1)
            {
                //data deleted
                char *msgerror = "please connect first";
                sendto(fdudp, &msgerror, 21, 0, (struct sockaddr *)&cliUDP, (unsigned int)len);
            }
        }
        if (FD_ISSET(ind, &fds))
        {
            //cas de la déco manuelle
                char msgdeco = 0Xfc;
                for (int n = 0; n < CONNECTIONS_MAX; n++)
                {
                    if (addrc[n] != 0)
                    {
                        cliUDP.sin_addr.s_addr = addrc[n];
                        sendto(fdudp, &msgdeco, 1, 0, (struct sockaddr *)&cliUDP, sizeof(cliUDP));
                    }
                }
                return 0;

            //déco timeout
                int id;
                for (int i = 0; i < CONNECTIONS_MAX; i++)
                { 
                    if (idc[i] == id)
                    {
                        addrc[i] = 0;
                        idc[i] = 0;
                        break;
                    }
                }
        }
    }

    recvfrom(fdudp, (char *)&buffer, BUFSIZ - 1, 0, (struct sockaddr *)&cliUDP, (unsigned int *)&len);
    if (buffer[0] == 0x1)
    {
        for (int i = 0; i < 8; i++)
        {
            if (IS_SET_BIT((char)*buffer, i))
            {
                printf("+");
            }
            else
            {
                printf(".");
            }
        }
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
    return 0;
}

//versions: 0 - le premier paquet set les infos invariables et les associes à un id | 1 - paquets envoyés une fois la connection établie, 4 bits du milieu de l'octet=> id du joueur