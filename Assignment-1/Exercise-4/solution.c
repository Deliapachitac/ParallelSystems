#include <pthread.h>
#include <stdio.h>
#include <errno.h>
#include <stdlib.h>
#include <time.h>
#include <sys/time.h>
long int* Account_Balances;

int main(int argc, char* argv[]){
    if(argc != 6){
        fprintf(stderr, "Correct usage: ./solution [Number of items] [Transactions per thread] [Percentage of balance questions] [Granularity of locks(0 for fine grained 1 for coarse grained)] [Number of threads]\n");
    }
    errno = 0;
    long num_of_items = strtol(argv[1],NULL,10);
    if(errno != 0){
        fprintf(stderr, "Number of items should be a 10-base number");
    }

    long trans_per_thread = strtol(argv[2], NULL,10);
    if(errno != 0){
        fprintf(stderr, "Number of transactions per thread should be a 10-base number");
    }

    long perc_questions = strtol(argv[3], NULL,10);
    if(errno != 0 || perc_questions < 0 || perc_questions > 100){
        fprintf(stderr, "Percentage of questions should be a number between 0 and 100");
    }

    long granularity = strtol(argv[4], NULL,10);
    if(errno != 0 || (granularity != 0 && granularity != 1)){
        fprintf(stderr, "Granularity should be 0 for fine-grained and 1 for coarse-grained locks");
    }
    long trans_per_thread = strtol(argv[5], NULL,10);
    if(errno != 0){
        fprintf(stderr, "Number of threads should be a 10-base number");
    }

    Account_Balances = malloc(num_of_items * sizeof(long int));
    srand((unsigned) time(NULL));

    for(int i = 0; i < num_of_items; i++){
        Account_Balances[i] = rand() % 100000; //We set an upper limit for starting balances to make sure there are no overflow errors
    }
}