#include <stdio.h>
#include <stdlib.h>
#include <time.h>

#define KEYSIZE 16

void main()
{
    int i;
    char key[KEYSIZE];
    
    printf("Current time (seconds since epoch): %lld\n", (long long) time(NULL));
    srand(time(NULL)); // Line 1 - comment this out for second test
    
    for (i = 0; i < KEYSIZE; i++){
        key[i] = rand() % 256;
        printf("%.2x", (unsigned char)key[i]);
    }
    printf("\n");
}
