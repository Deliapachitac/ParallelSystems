#include <stdio.h>
#include <stdlib.h>
#include <pthread.h>
#include <sys/time.h>



struct barrier_args {
    int barrier_count ; // Number of threads that have reached the barrier
    pthread_mutex_t barrier_mutex; 
    pthread_cond_t barrier_cond;
    int n;
    int num_threads;
    int cycle; // for reusable barrier
};
typedef struct barrier_args* BarrierArgs;


void* thread_function(void* arg);
void barrier_init(BarrierArgs args, int n, int num_threads);


int main(int argc, char* argv[]) {
    if (argc != 3) {
        fprintf(stderr, "Usage: %s <threads> <barriers>\n", argv[0]);
        exit(EXIT_FAILURE);
    }

    int thread_count = atoi(argv[1]);
    int n = atoi(argv[2]);

    //Start measuring time
    struct timeval start, end;
    double time_taken;
    gettimeofday(&start, NULL);

    pthread_t threads[thread_count];

    BarrierArgs args = malloc(sizeof(struct barrier_args));
    barrier_init(args, n, thread_count);

    for (int t = 0; t < thread_count; t++) {
        
        pthread_create(&threads[t], NULL, thread_function, (void*)args);
    }

    for (int t = 0; t < thread_count; t++){
        pthread_join(threads[t], NULL);
    }

    pthread_mutex_destroy(&args->barrier_mutex);
    pthread_cond_destroy(&args->barrier_cond);
    free(args);


    // End measuring time
    gettimeofday(&end, NULL);
    time_taken = (end.tv_sec - start.tv_sec) + (end.tv_usec - start.tv_usec) / 1e6;
    printf("Time taken: %f seconds\n", time_taken);

    return 0;
}

void* thread_function(void* arg) {
    
    BarrierArgs args = (BarrierArgs)arg;
    
    // Barrier implementation
    for (int i = 0; i < args->n; i++) {

        //First we lock the mutex before accessing the  shared varibles       
        pthread_mutex_lock(&args->barrier_mutex);

        int my_cycle = args->cycle;
        args->barrier_count++;

        //If this is the last thread to reach the barrier  reset the count for next use , 
        // increment cycle and wake up all the waiting threads tocontinue
        if (args->barrier_count == args->num_threads) {
            args->barrier_count = 0;
            args->cycle++;
            pthread_cond_broadcast(&args->barrier_cond);

        //if we are not on the last thread then we wait until the cycle changes
        // this means that all threads will be synchronised  
        } else {
            while (my_cycle == args->cycle) {
                pthread_cond_wait(&args->barrier_cond, &args->barrier_mutex);
            }
        }

        pthread_mutex_unlock(&args->barrier_mutex);
    }

    return NULL;
}

void barrier_init(BarrierArgs args, int n, int num_threads) {
    args->barrier_count = 0;
    args->n = n;
    args->num_threads = num_threads;
    args->cycle = 0;
    pthread_mutex_init(&args->barrier_mutex, NULL);
    pthread_cond_init(&args->barrier_cond, NULL);
    
}