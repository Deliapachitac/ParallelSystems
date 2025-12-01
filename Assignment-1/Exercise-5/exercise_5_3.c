#include <stdio.h>
#include <stdlib.h>
#include <pthread.h>
#include <sys/time.h>

struct barrier_args{
    int barrier_count ; // Number of threads that have reached the barrier
    int n;     
    int num_threads;   
    int sense;   // 0 or 1 if we are using sense reversal  
    pthread_mutex_t mutex;
} ;
typedef struct barrier_args* BarrierArgs;

void* thread_function(void* arg);
void barrier_init(BarrierArgs b,int n, int num_threads) ;


int main(int argc, char* argv[]) {
    if (argc != 3) {
        fprintf(stderr, "Usage: %s NUM_THREADS N\n", argv[0]);
        return 1;
    }

    int num_threads = atoi(argv[1]);
    int n = atoi(argv[2]);

    //Start measuring time
    struct timeval start, end;
    double time_taken;
    gettimeofday(&start, NULL);


    pthread_t threads[num_threads];
    BarrierArgs args= malloc(sizeof(struct barrier_args));
    barrier_init(args, n, num_threads);

    for (int i = 0; i < num_threads; i++) {
        pthread_create(&threads[i], NULL, thread_function, (void*)args);
    }

    for (int i = 0; i < num_threads; i++) {
        pthread_join(threads[i], NULL);
    }

    pthread_mutex_destroy(&args->mutex);
    free(args);

    //End measuring time
    gettimeofday(&end, NULL);
    time_taken = (end.tv_sec - start.tv_sec) + (end.tv_usec - start.tv_usec) / 1e6;
    printf("Time taken: %f seconds\n", time_taken);


    return 0;
}

void* thread_function(void* arg) {
    
    BarrierArgs args = (BarrierArgs)arg;

    
    // barrier implementation using sense reversal
    for (int i = 0; i < args->n; i++) {

        int local_sense = 1 - args->sense; // flip local sense
        pthread_mutex_lock(&args->mutex);

        args->barrier_count++;
        
        if (args->barrier_count == args->num_threads) {
            args->barrier_count = 0;
            args->sense = local_sense; // flip the sense
            pthread_mutex_unlock(&args->mutex);
        } else {
            pthread_mutex_unlock(&args->mutex);
            while (args->sense != local_sense) {
                // busy wait
            }
        }
    
        
        
    }
    
    return NULL;
}

void barrier_init(BarrierArgs b, int n, int num_threads) {
    b->barrier_count = 0;
    b->n = n;
    b->num_threads = num_threads;
    b->sense = 0;
    pthread_mutex_init(&b->mutex, NULL);
}