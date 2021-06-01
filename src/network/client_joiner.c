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

// FIFO file path
char *fifo_output_path = "/tmp/info_output_joiner";
char *fifo_input_path = "/tmp/info_input_joiner";

char *joiner_to_crea_path = "/tmp/joiner_to_crea";
char *crea_to_joiner_path = "/tmp/crea_to_joiner";

void gestionnaire(int numero)
{
    signal(numero, gestionnaire);
    // Ca peut servir
}

int main(int argc, char **argv)
{
    // Open the fifo
    int joiner_to_crea, from_python_descriptor, to_python_client, crea_to_joiner;

    // signal(SIGUSR1, gestionnaire);

    char buf[BUFFLEN + 1];
    char child_buf[BUFFLEN + 1];
    bzero(buf, BUFFLEN);
    bzero(child_buf, BUFFLEN);
    int rval = 0;

    // Listenning the fifo
    // Forking to make two listening possible, 1 from the python client, the other from the joiner pipe -> protoype of a select

    pid_t status;

    switch (status = fork())
    {
    case -1:
        perror("Creation processus error");
        exit(EXIT_FAILURE);
    case 0:
        // Child process : listening to joiner's pipe
        puts("[+] Listening on crea_to_joiner pipe \n");
        if ((to_python_client = open(fifo_input_path, O_WRONLY)) == -1)
        {
            perror("open");
            exit(EXIT_FAILURE);
        }
        if ((crea_to_joiner = open(crea_to_joiner_path, O_RDONLY)) == -1)
        {
            perror("open");
            exit(EXIT_FAILURE);
        }

        while (TRUE)
        {
            bzero(child_buf, BUFFLEN);
            if ((rval = read(crea_to_joiner, child_buf, BUFFLEN)) < 0)
            {
                perror("read");
                exit(EXIT_FAILURE);
            }
            if (rval != 0)
            {
                if (write(to_python_client, child_buf, BUFFLEN) < 0) //transmiting data
                {
                    perror("Writing to to_python_client fifo");
                    exit(EXIT_FAILURE);
                } //transmiting data
            }
        }
        close(to_python_client);
        close(crea_to_joiner);
        break;

    default:
        // Parent process : listening to python client
        puts("[+] Starting the joiner client ...\n");
        if ((from_python_descriptor = open(fifo_output_path, O_RDONLY)) == -1)
        {
            perror("open");
            exit(EXIT_FAILURE);
        }
        if ((joiner_to_crea = open(joiner_to_crea_path, O_WRONLY)) == -1)
        {
            perror("open");
            exit(EXIT_FAILURE);
        }
        while (TRUE)
        {
            bzero(buf, BUFFLEN);
            if ((rval = read(from_python_descriptor, buf, BUFFLEN)) < 0)
            {
                perror("read");
                exit(EXIT_FAILURE);
            }
            if (rval != 0)
            {
                // printf("%d \n", rval); //Debuging part
                buf[rval] = '\0';
                // puts(buf);                                   //Debuging part
                if (write(joiner_to_crea, buf, rval) < 0) //transmiting data
                {
                    perror("Writing to joiner_to_crea fifo");
                    exit(EXIT_FAILURE);
                } //transmiting data
            }
        }
        close(from_python_descriptor);
        close(joiner_to_crea);
    }
    exit(EXIT_SUCCESS);
}
