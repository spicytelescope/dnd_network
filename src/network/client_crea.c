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
char *fifo_output_path = "/tmp/info_output_creator";
char *fifo_input_path = "/tmp/info_input_creator";

char *crea_to_joiner_path = "/tmp/crea_to_joiner";
char *joiner_to_crea_path = "/tmp/joiner_to_crea";

void gestionnaire(int numero)
{
    signal(numero, gestionnaire);
    // Ca peut servir
}

int main(int argc, char **argv)
{
    // Open the fifo
    int from_python_descriptor, to_python_client, from_crea_to_joiner, joiner_to_crea;

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
        puts("[+] Listening on joiner_to_crea pipe \n");
        if ((to_python_client = open(fifo_input_path, O_WRONLY)) == -1)
        {
            perror("open");
            exit(EXIT_FAILURE);
        }

        if ((joiner_to_crea = open(joiner_to_crea_path, O_RDONLY)) == -1)
        {
            perror("open");
            exit(EXIT_FAILURE);
        }
        while (TRUE)
        {
            bzero(child_buf, BUFFLEN);
            if ((rval = read(joiner_to_crea, child_buf, BUFFLEN)) < 0)
            {
                perror("read");
                exit(EXIT_FAILURE);
            }
            if (rval != 0)
            {
                if (write(to_python_client, child_buf, rval) < 0) //transmiting data
                {
                    perror("Writing to to_python_client fifo");
                    exit(EXIT_FAILURE);
                } //transmiting data
            }
        }
        close(to_python_client);
        close(joiner_to_crea);
        break;

    default:
        // Parent process : listening to python client
        puts("[+] Starting the crea client ...\n");

        if ((from_python_descriptor = open(fifo_output_path, O_RDONLY)) == -1)
        {
            perror("open");
            exit(EXIT_FAILURE);
        }
        if ((from_crea_to_joiner = open(crea_to_joiner_path, O_WRONLY)) == -1)
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
                buf[rval] = '\0';
                // puts(buf);
                if (write(from_crea_to_joiner, buf, BUFFLEN) < 0)
                {
                    perror("Writing to crea_to_joiner fifo");
                    exit(EXIT_FAILURE);
                } //transmiting data
            }
        }

        close(from_python_descriptor);
        close(from_crea_to_joiner);
    }
    exit(EXIT_SUCCESS);
}
