#include <dirent.h>
#include <errno.h>
#include <fcntl.h>
#include <grp.h>
#include <math.h>
#include <pwd.h>
#include <time.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <sys/stat.h>
#include <sys/types.h>
#include <sys/wait.h>
#include <unistd.h>

#define BUFFLEN 1024
#define TRUE 1
#define FALSE 0

void gestionnaire (int numero)
{
        signal(numero, gestionnaire);
        // Ca peut servir
}

int main(int argc, char **argv){
    // Create the fifo needed to get informations from the game
    if(mkfifo("info_output", 0777) == -1){
        if(errno != EEXIST){
            perror("mkfifo");
            exit(EXIT_FAILURE);
        }
    }
    if(mkfifo("info_input", 0777) == -1){
        if(errno != EEXIST){
            perror("mkfifo");
            exit(EXIT_FAILURE);
        }
    }
    // Open the fifo
    int ind, outd;
    if((ind = open("info_output", O_RDONLY)) == -1){
        perror("open");
        exit(EXIT_FAILURE);
    }
    if((outd = open("info_input", O_WRONLY)) == -1){
        perror("open");
        exit(EXIT_FAILURE);
    }

    // signal(SIGUSR1, gestionnaire);

    char buf[BUFFLEN + 1];
    bzero(buf, BUFFLEN);
    int rval = 0;

    // Listenning the fifo
    while(TRUE){
        bzero(buf, BUFFLEN);
        if((rval = read(ind, buf, BUFFLEN)) < 0){
            perror("read");
            exit(EXIT_FAILURE);
        }
        if(rval != 0){
            puts(buf);
            write(outd, buf, strlen(buf));
        }
    }

    close(ind);
    close(outd);
    exit(EXIT_SUCCESS);
}