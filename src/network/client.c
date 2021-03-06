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

void print_ip(unsigned int ip)
{
    unsigned char bytes[4];
    bytes[0] = ip & 0xFF;
    bytes[1] = (ip >> 8) & 0xFF;
    bytes[2] = (ip >> 16) & 0xFF;
    bytes[3] = (ip >> 24) & 0xFF;
    printf("%d.%d.%d.%d\n", bytes[0], bytes[1], bytes[2], bytes[3]);
}

int confirmation(int fdt, int fdu, char *addressH, struct sockaddr_in hote, struct sockaddr_in udpcli, in_addr_t *addrcli, char idc[CONNECTIONS_MAX][ID_LEN], char *selfID, int to_python_descriptor)
{
    // if (inet_aton(addressH, &(udpcli.sin_addr)) == 0)
    //     stop("inet_aton");
    // sendto(fdu, "yo", 3, 0, &udpcli, sizeof(udpcli));
    int nb_addr = 0;
    char message[BUFSIZE];
    hote.sin_port = htons(PORT_TCP);
    printf("%s\n", addressH);
    if (inet_aton(addressH, &(hote.sin_addr)) == 0)
        stop("inet_aton");
    socklen_t lh = sizeof(hote);
    if (connect(fdt, (struct sockaddr *)&hote, lh) == -1)
        stop("connect [1]");

    bzero(message, BUFSIZE);
    recv(fdt, &message, BUFSIZE + 1, 0);
    if ((int)*message == 1)
    {
        printf("\033[0;33m[C Client]\033[0;37m : Confirmation Protocol - 1\n");
        addrcli[(int)*(message + 4)] = hote.sin_addr.s_addr;
        // printf("Stocked IP address : %d %d\n", addrcli[(int)*(message + 4)], (int)*(message + 4));
        strncpy(idc[(int)*(message + 4)], (message + 8), ID_LEN);

        //send ids to pipe
        /*for (int i = 0; i < CONNECTIONS_MAX + 4; i++)
        {
            if ((in_addr_t) * (message + 4 * i + 16) != 0)
            {
                addrcli[i] = (in_addr_t) * (message + i * 4 + 16);
                strncpy(idc[i], (message + 64 + i * ID_LEN), ID_LEN);
                nb_addr++;
            }
            for (int i = 0; i < CONNECTIONS_MAX; i++)
            {
                if (strcmp(idc[i], UNKNOWN_ID) != 0)
                    write(to_python_descriptor, idc[i], BUFSIZE);
            }
        }*/
        if (nb_addr == 0)
            send(fdt, "ok", 3, 0);
    }
    else
        return -1;
    for (int i = 0; i < CONNECTIONS_MAX; i++)
    {
        if (addrcli[i] != 0)
        {
            udpcli.sin_addr.s_addr = addrcli[i];
            //sendto(fdu, (char *)&selfID, sizeof(long long int), 0, (struct sockaddr *)&udpcli, sizeof(udpcli));
        }
    }
    int lencli = sizeof(udpcli);
    printf("\033[0;33m[C Client]\033[0;37m : Confirmation - 2\n");

    while (1)
    {
        // if (nb_addr != 0)
        // {
        //     recvfrom(fdu, &message, 3, 0, (struct sockaddr *)&udpcli, (socklen_t *)&lencli);
        //     nb_addr--;
        // }
        // if (nb_addr == 0)
        // {
        send(fdt, selfID, ID_LEN, 0);
        close(fdt);
        return 0;
        // }
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
            recv(fdt, &message, BUFSIZE + 1, 0);

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
    /**
     * @brief check if an element elem is in the list and check if the list is complete,
     * @return i if it's in, else -1 
     * 
    **/

    for (int i = 0; i < CONNECTIONS_MAX; i++)
    {
        if (elem == list[i])
            return i;
    }
    return -1;
}

int main(int argc, char *argv[])
{

    printf("CONNECTED WITH FOLLOWING ARGS : \n");
    for (int i = 0; i < argc; i++)
    {
        printf("\t-> %d : %s\n", i, argv[i]);
    }
    // Open the fifo
    int from_python_descriptor,
        to_python_descriptor;
    char size[5];
    int err;
    int bytesAvailable;
    char udp_to_python_packet[BUFSIZE];
    if ((from_python_descriptor = open(fifo_output_path, O_RDWR)) == -1)
    {
        perror("open - from_python_descriptor");
        exit(EXIT_FAILURE);
    }
    if ((to_python_descriptor = open(fifo_input_path, O_RDWR)) == -1)
    {
        perror("open - to_python_descriptor");
        exit(EXIT_FAILURE);
    }

    newP_packet newp;
    new_packet new;
    int indice_temp = -1;

    int activity = 0;
    int true = 1;
    int complete = 0;
    int fd_connect[CONNECTIONS_MAX];          //fd sockets under connection
    int new_sock;                             //fd socket new connect
    in_addr_t under_connect[CONNECTIONS_MAX]; //temporaly saves the ip adress not connected yet
    //game_packet2 pack={0,0,0};
    in_addr_t addrc[CONNECTIONS_MAX];  //address ip list of the clients
    char idc[CONNECTIONS_MAX][ID_LEN]; // id associated to the ip address
    memset(fd_connect, -1, sizeof(fd_connect));
    memset(under_connect, 0, sizeof(under_connect));
    memset(addrc, 0, sizeof(addrc));

    //all the packets
    char selfID[ID_LEN];
    struct sockaddr_in firstContactIP;

    if (argc == 3)
    {
        strncpy(selfID, argv[1], ID_LEN);
        inet_pton(AF_INET, argv[2], &firstContactIP.sin_addr);
        addrc[0] = firstContactIP.sin_addr.s_addr;
    }

    //file descriptors
    int naddr;
    int fdudp;  //fd udp
    int fdtcp;  //tcp file descriptor
    fd_set fds; //set of file descriptors
    char msg[BUFSIZE];
    struct sockaddr_in servUdp, servTcp, cliTCP, cliUDP;
    char buffer[BUFSIZE];
    bzero(buffer, BUFSIZE);
    int rval = 0;

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
    {
        printf("Port used : %d \n", PORT_UDP);
        stop("bind udp");
    }

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
    if (argc == 3) //adress & ip game_id
    {
        cliTCP.sin_family = AF_INET;
        cliTCP.sin_port = htons(PORT_TCP);
        // printf("%s\n", argv[1]);
        confirmation(fdtcp, fdudp, argv[2], cliTCP, cliUDP, addrc, idc, selfID, to_python_descriptor);
        printf("\033[0;33m[C Client]\033[0;37m : List of ip adress in decimal conversion :\n");
        for (int i = 0; i < CONNECTIONS_MAX; i++)
        {
            print_ip(addrc[i]);
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
    if (listen(fdtcp, 10) == -1)
    {
        stop("listen");
    }
    //connection(ip dest)
    //fdmax is the maximum number in the fd set fds
    int addrlen = sizeof(cliTCP);
    int fdmax = MMax(fdudp, from_python_descriptor);
    fdmax = MMax(fdmax, fdtcp);
    int len = sizeof(cliTCP);
    int nactivity = 0;
    //select loop
    while (1)
    {
        // printf("Entering in the loop ... \n");
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
        FD_SET(from_python_descriptor, &fds);
        FD_SET(fdtcp, &fds);
        activity = select(fdmax + 1, &fds, NULL, NULL, NULL);
        nactivity = 0;
        bzero(msg, BUFSIZE);
        //TCP socket for the new connections
        while (nactivity < activity)
        {
            if (FD_ISSET(fdtcp, &fds))
            {
                nactivity++;
                if ((new_sock = accept(fdtcp, (struct sockaddr *)&cliTCP, (socklen_t *)&addrlen)) < 0)
                {
                    stop("accept");
                }

                printf("\033[0;33m[C Client]\033[0;37m : Confirmation - 3\n");
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
                                printf("\033[0;33m[C Client]\033[0;37m : Confirmation - 4\n");
                                fd_connect[con] = new_sock;
                                under_connect[con] = cliTCP.sin_addr.s_addr;
                                memset(&cliTCP, 0, sizeof(cliTCP));
                                memset(&newp, -1, sizeof(newp));
                                newp.type = 1;
                                newp.indice = con;
                                strncpy(newp.selfID, selfID, ID_LEN);
                                for (int n; n < CONNECTIONS_MAX; n++)
                                {
                                    if (addrc[n] != 0)
                                    {
                                        newp.players_addr[n] = addrc[n];
                                        strncpy(newp.players_id[n], idc[n], ID_LEN);
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
                    nactivity++;
                    recv(fd_connect[con], &msg, BUFSIZE + 1, 0);
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
                            strncpy(idc[i], msg, ID_LEN);
                            fd_connect[con] = 0;
                            // printf("%d\n", addrc[i]);
                            // printf("A new player joined the game : %s \n", idc[i]);
                            char *disc_msg = "{\n  \"type\": \"discovery_request\"\n}";
                            if (write(to_python_descriptor, disc_msg, strlen(disc_msg)) < 0) //transmiting data
                            {
                                perror("Writing to to_python_client fifo - disc");
                                exit(EXIT_FAILURE);
                            } //transmiting data
                            break;
                        }
                    }
                }
            }

            //UDP socket for the registered players
            if (FD_ISSET(fdudp, &fds))
            {
                nactivity++;
                bzero(msg, BUFSIZE);
                bzero(udp_to_python_packet, BUFSIZE);
                rval = 0;
                if (rval = recvfrom(fdudp, (char *)&msg, BUFSIZE + 1, 0, (struct sockaddr *)&cliUDP, (unsigned int *)&len) < 0)
                    stop("recvfrom");

                // printf("buffer (size=%d) recv : %s\n", strlen(msg), msg);
                // Sending packet size first :
                // sprintf(udp_to_python_packet, "%d%s\n", strlen(msg), msg);
                // printf("Recv & send to python : %s\n", udp_to_python_packet);
                if (write(to_python_descriptor, msg, strlen(msg)) < 0) //transmiting data
                {
                    perror("Writing to to_python_client fifo");
                    exit(EXIT_FAILURE);
                } //transmiting data

                //player already connected
                if ((naddr = checkin(under_connect, cliUDP.sin_addr.s_addr)) >= 0)
                {
                    //new connection
                    if (indice_temp != -1)
                    {
                        addrc[indice_temp] = 0;
                        strncpy(idc[indice_temp], UNKNOWN_ID, strlen(UNKNOWN_ID) + 1);
                    }
                    for (int i = 0; i < CONNECTIONS_MAX; i++)
                    {
                        if (addrc[i] == 0)
                        {
                            indice_temp = i;
                            addrc[indice_temp] = cliUDP.sin_addr.s_addr;
                            strncpy(idc[indice_temp], msg, ID_LEN); //send id
                        }
                    }
                    sendto(fdudp, "ok", 3, 0, (struct sockaddr *)&cliUDP, sizeof(cliUDP));
                    //set son id
                }
                /*else if ((naddr = checkin(addrc, cliUDP.sin_addr.s_addr)) >= 0)
                {
                    /*if (*msg == 'o')
                    {
                        if (write(to_python_descriptor, idc[indice_temp], ID_LEN) < 0) //transmiting data
                        {
                            perror("Writing to to_python_client fifo");
                            exit(EXIT_FAILURE);
                        }                 //transmiting data
                        indice_temp = -1; // from "player_connecting ...." to "player_connected !"
                    }
                    else if ((int)*msg == 2)
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
                    else if (*msg == DECONNECTION_MANUAL_BYTES)
                    {
                        for (int i = 0; i < CONNECTIONS_MAX; i++)
                        {
                            if (addrc[i] == cliUDP.sin_addr.s_addr)
                            {
                                addrc[i] = 0;
                                // TODO CREATE JSON PACKET FROM C -> {name:"deconnexion", "sender_id": idc[i]}

                                strncpy(idc[i], UNKNOWN_ID, strlen(UNKNOWN_ID) + 1);

                                break;
                            }
                        }
                    }
                    else
                    {
                        printf("buffer recv : %s", msg);
                        if (write(to_python_descriptor, msg, strlen(msg)) < 0) //transmiting data
                        {
                            perror("Writing to to_python_client fifo");
                            exit(EXIT_FAILURE);
                        } //transmiting data
                        printf("Receiving data from network \n");
                    }
                }
                //player unknown
                else if (naddr == -1)
                {
			printf("buffer recv : %s", msg);
                        if (write(to_python_descriptor, msg, strlen(msg)) < 0) //transmiting data
                        {
                            perror("Writing to to_python_client fifo");
                            exit(EXIT_FAILURE);
                        } //transmiting data
                    printf("zebi oui le random \n");
                    //data deleted
                    char *msgerror = "please connect first";
                    sendto(fdudp, &msgerror, 21, 0, (struct sockaddr *)&cliUDP, (unsigned int)len);
                }*/
            }

            if (FD_ISSET(from_python_descriptor, &fds))
            {
                nactivity++;
                bzero(buffer, BUFSIZE);
                bzero(size, 4);
                bytesAvailable = 0;
                // printf("zebi \n");

                /*if ((rval = read(from_python_descriptor, size, 4)) < 0)
                {
                    perror("read - from_python_descriptor - size");
                    exit(EXIT_FAILURE);
                }*/
                // printf("size: %d \n", atoi(size));
                if (err = ioctl(from_python_descriptor, FIONREAD, &bytesAvailable) == -1)
                {
                    perror("read - from_python_descriptor - ioctl");
                    exit(EXIT_FAILURE);
                }
                else
                {
                    if (bytesAvailable != 0)
                        printf("\033[0;33m[C Client]\033[0;37m : Packet size transmitted : %d\n", bytesAvailable);
                }

                if ((rval = read(from_python_descriptor, buffer, bytesAvailable)) < 0)
                {
                    perror("read - from_python_descriptor - read");
                    exit(EXIT_FAILURE);
                }

                if (rval != 0)
                {
                    // printf("Transmitting : %s\n", buffer);

                    //cas de la déco manuelle
                    /*if (*buffer == DECONNECTION_MANUAL_BYTES)
                    {
                        char msgdeco = DECONNECTION_MANUAL_BYTES;
                        for (int n = 0; n < CONNECTIONS_MAX; n++)
                        {
                            if (addrc[n] != 0)
                            {
                                cliUDP.sin_addr.s_addr = addrc[n];
                                sendto(fdudp, &msgdeco, 1, 0, (struct sockaddr *)&cliUDP, sizeof(cliUDP));
                            }
                        }
                        return EXIT_SUCCESS;
                    }

                    // // //déco timeout
                    else if (*buffer == DECONNECTION_TIMEOUT_BYTES)
                    {
                        printf("DECONNECTION_TIMEOUT_BYTES \n");
                        int deco_val;
                        char deco_id[ID_LEN];
                        if ((deco_val = read(from_python_descriptor, deco_id, ID_LEN + 1)) < 0)
                        {
                            perror("read");
                            exit(EXIT_FAILURE);
                        }
                        if (deco_id != 0)
                        {
                            for (int i = 0; i < CONNECTIONS_MAX; i++)
                            {
                                if (strcmp(idc[i], deco_id) == 0)
                                {
                                    addrc[i] = 0;
                                    strncpy(idc[i], UNKNOWN_ID, strlen(UNKNOWN_ID) + 1);
                                    break;
                                }
                            }
                        }
                    }
                    else
                    {*/
                    // Default case - Transmitting packets to every players
                    for (int n = 0; n < CONNECTIONS_MAX; n++)
                    {
                        //printf("Chekcing adress %d : %d\n", n, addrc[n]);
                        if (addrc[n] != 0)
                        {
                            cliUDP.sin_addr.s_addr = addrc[n];
                            sendto(fdudp, &buffer, bytesAvailable, 0, (struct sockaddr *)&cliUDP, sizeof(cliUDP));
                            printf("\033[0;33m[C Client]\033[0;37m : Transmitting packet to network \n");
                        }
                    }
                    // printf("-------------\n");

                    //}
                }
            }
        }
    }

    return EXIT_SUCCESS;
}

//versions: 0 - le premier paquet set les infos invariables et les associes à un id | 1 - paquets envoyés une fois la connection établie, 4 bits du milieu de l'octet=> id du joueur
