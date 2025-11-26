#include <pthread.h>
#include <stdio.h>
#include <errno.h>
#include <stdlib.h>
#include <time.h>
#include <sys/time.h>
#include "../Shared/my_rand.h"
long int* Account_Balances;
float trans_per_thread;
long perc_questions;
long num_of_items;
//TODO: Add locks
void *Transactions(void* my_rank){
    long rank = (long) my_rank;
    unsigned seed = (unsigned) rank + 1; //Seed for the rng, non 0 so we don't get 0 all the time and unique to each thread
    double r;
    unsigned acc1;
    unsigned acc2;
    unsigned ammount;
    long long int total_balance;
    for(int trans = 0; trans < trans_per_thread; trans++){
        r = my_drand(&seed);
        //Balance question;
        if(r < perc_questions){
            acc1 = my_rand(&seed) % num_of_items;
            //Critical section
            total_balance += Account_Balances[acc1];
            //Critical section end
        }
        //Transfer money
        else{
            acc1 = my_rand(&seed) % num_of_items;
            acc2 = my_rand(&seed) % num_of_items;
            while(acc2 == acc1) acc2 = my_rand(&seed) % num_of_items;
            //Critical section start
            ammount = my_rand(&seed) % Account_Balances[acc1]; //Make sure we accounts don't reach negative money
            Account_Balances[acc2] += ammount;
            Account_Balances[acc1] -= ammount;
            //Critical section end
        }
    }
}




int main(int argc, char* argv[]){
    if(argc != 6){
        fprintf(stderr, "Correct usage: ./solution [Number of items] [Transactions per thread] [Percentage of balance questions] [Granularity of locks(0 for fine grained 1 for coarse grained)] [Number of threads]\n");
        return 1;
    }
    errno = 0;
    num_of_items = strtol(argv[1],NULL,10);
    if(errno != 0){
        fprintf(stderr, "Number of items should be a 10-base number");
        return 1;
    }

    trans_per_thread = strtol(argv[2], NULL,10);
    if(errno != 0){
        fprintf(stderr, "Number of transactions per thread should be a 10-base number");
        return 1;
    }

    perc_questions = strtof(argv[3], NULL);
    if(errno != 0 || perc_questions < 0 || perc_questions > 1){
        fprintf(stderr, "Percentage of questions should be a floating point number between 0 and 1");
        return 1;
    }

    long granularity = strtol(argv[4], NULL,10);
    if(errno != 0 || (granularity != 0 && granularity != 1)){
        fprintf(stderr, "Granularity should be 0 for fine-grained and 1 for coarse-grained locks");
        return 1;
    }
    long thread_number = strtol(argv[5], NULL,10);
    if(errno != 0){
        fprintf(stderr, "Number of threads should be a 10-base number");
        return 1;
    }

    Account_Balances = malloc(num_of_items * sizeof(long int));
    srand((unsigned) time(NULL));

    for(int i = 0; i < num_of_items; i++){
        Account_Balances[i] = rand() % 1000; //We set an upper limit for starting balances to make sure there are no overflow errors
    }
    pthread_t* thread_handles;
    thread_handles = malloc(thread_number * sizeof(pthread_t));
    struct timeval start, end;
    double elapsed;
    gettimeofday(&start, NULL);
    for(long thread = 0; thread < thread_number; thread++ ){
        pthread_create(&thread_handles[thread], NULL, Transactions, (void*) thread);
    }
    for(long thread = 0; thread < thread_number; thread++){
        pthread_join(thread_handles[thread], NULL);
    }
    gettimeofday(&end,NULL);
    elapsed = (end.tv_sec - start.tv_sec) + (end.tv_usec - start.tv_usec) / 1e6;
    printf("Execution took: %f seconds\n", elapsed);
    return 0;

}