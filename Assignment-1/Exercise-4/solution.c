#include <pthread.h>
#include <stdio.h>
#include <errno.h>
#include <stdlib.h>
#include <time.h>
#include <sys/time.h>
#include <unistd.h>
#include "../Shared/my_rand.h"
#define SLEEPING 0
long int* Account_Balances;
float trans_per_thread;
float perc_questions;
long num_of_items;
long granularity;
pthread_mutex_t mutex;
pthread_mutex_t* mutexes;
void *Transactions(void* my_rank){
    long rank = (long) my_rank;
    unsigned seed = (unsigned) rank + 1; //Seed for the rng, non 0 so we don't get 0 all the time and unique to each thread
    double r;
    unsigned acc1;
    unsigned acc2;
    unsigned ammount;
    long long int total_balance;
    if(granularity){
        for(int trans = 0; trans < trans_per_thread; trans++){
            r = my_drand(&seed);
            //Balance question
            if(r < perc_questions){
                acc1 = my_rand(&seed) % num_of_items;
                pthread_mutex_lock(&mutex);
                total_balance += Account_Balances[acc1];
                if(SLEEPING)  usleep(1);
                pthread_mutex_unlock(&mutex);
            }
            //Transfer money
            else{
                acc1 = my_rand(&seed) % num_of_items;
                acc2 = my_rand(&seed) % num_of_items;
                while(acc2 == acc1) acc2 = my_rand(&seed) % num_of_items;
                pthread_mutex_lock(&mutex);
                ammount = Account_Balances[acc1] ? my_rand(&seed) % Account_Balances[acc1]:0; //Make sure the accounts don't reach negative money
                Account_Balances[acc2] += ammount;
                Account_Balances[acc1] -= ammount;
                pthread_mutex_unlock(&mutex);
            }
        }
    }
    else{
        for(int trans = 0; trans < trans_per_thread; trans++){
            r = my_drand(&seed);
            //Balance question
            if(r < perc_questions){
                acc1 = my_rand(&seed) % num_of_items;
                pthread_mutex_lock(&mutexes[acc1]);
                total_balance += Account_Balances[acc1];
                if(SLEEPING)  usleep(1);
                pthread_mutex_unlock(&mutexes[acc1]);
            }
            //Transfer money
            else{
                acc1 = my_rand(&seed) % num_of_items;
                acc2 = my_rand(&seed) % num_of_items;
                while(acc2 == acc1) acc2 = my_rand(&seed) % num_of_items;
                //Ordering scheme to prevent circular wait from happening
                unsigned low_acc = (acc1 < acc2) ? acc1 : acc2;
                unsigned high_acc = (acc1 > acc2) ? acc1 : acc2;
                pthread_mutex_lock(&mutexes[low_acc]);
                pthread_mutex_lock(&mutexes[high_acc]);
                ammount = Account_Balances[acc1] ? my_rand(&seed) % Account_Balances[acc1]:0; //Make sure the accounts don't reach negative money
                Account_Balances[acc2] += ammount;
                Account_Balances[acc1] -= ammount;
                pthread_mutex_unlock(&mutexes[high_acc]);
                pthread_mutex_unlock(&mutexes[low_acc]);
            }
        }
    }
    return NULL;
}




int main(int argc, char* argv[]){
    if(argc != 6){
        fprintf(stderr, "Correct usage: ./solution [Number of items] [Transactions per thread] [Percentage of balance questions] [Granularity of locks(0 for fine grained 1 for coarse grained)] [Number of threads]\n");
        return 1;
    }
    errno = 0;
    num_of_items = strtol(argv[1],NULL,10);
    if(errno != 0){
        fprintf(stderr, "Number of items should be a 10-base number\n");
        return 1;
    }

    trans_per_thread = strtol(argv[2], NULL,10);
    if(errno != 0){
        fprintf(stderr, "Number of transactions per thread should be a 10-base number\n");
        return 1;
    }

    perc_questions = strtof(argv[3], NULL);
    if(errno != 0 || perc_questions < 0 || perc_questions > 1){
        fprintf(stderr, "Percentage of questions should be a floating point number between 0 and 1\n");
        return 1;
    }

    granularity = strtol(argv[4], NULL,10);
    if(errno != 0 || (granularity != 0 && granularity != 1)){
        fprintf(stderr, "Granularity should be 0 for fine-grained and 1 for coarse-grained locks\n");
        return 1;
    }
    long thread_number = strtol(argv[5], NULL,10);
    if(errno != 0){
        fprintf(stderr, "Number of threads should be a 10-base number\n");
        return 1;
    }

    Account_Balances = malloc(num_of_items * sizeof(long int));
    srand((unsigned) time(NULL));
    if(granularity){
        pthread_mutex_init(&mutex,NULL);
    }
    else{
        mutexes = malloc(num_of_items * sizeof(pthread_mutex_t));
        for(int i = 0; i < num_of_items; i++){
            Account_Balances[i] = rand() % 1000; //We set an upper limit for starting balances to make sure there are no overflow errors
            pthread_mutex_init(&mutexes[i],NULL);
        }
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
    if(granularity){
        pthread_mutex_destroy(&mutex);
    }
    else{
        for(int i = 0; i < num_of_items; i++){
            pthread_mutex_destroy(&mutexes[i]);
            
        }
        free(mutexes);
        
    }
    free(Account_Balances);
    free(thread_handles);
    return 0;

}