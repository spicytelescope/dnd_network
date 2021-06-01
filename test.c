
#include <stdio.h>


int main(){
    char message[32];
    message[0]="a";
    message[4]=(char) 3;
    message[16]= (char) 2;
    printf("%d", (int) *(message+16));
}