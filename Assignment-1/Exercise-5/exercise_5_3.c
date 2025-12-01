#include <stdio.h>
#include <stdlib.h>
#include <pthread.h>
#include <stdbool.h>
#include <sys/time.h>

typedef struct  {
    int barrier_count; //  Number of threads that have reached the barrier     
    int num_threads;   
    bool sense;          // current sense of the barrier(0 or 1)
    pthread_mutex_t mutex;
}thread_barier ;

void barrier_init(thread_barier* b, int num_threads);        
void barrier_destroy(thread_barier* b);
void barrier_wait(thread_barier* b, int* local_sense);  
void* thread_function(void* arg);

thread_barier barrier;

int main(int argc, char* argv[]) {
    
    // Check for correct number of command-line arguments
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

    // Allocate barrier and create threads
    pthread_t threads[num_threads];
    barrier_init(&barrier, num_threads);

    // Send the numbers of iterations through thread function argument
    for (int i = 0; i < num_threads; i++) {
        pthread_create(&threads[i], NULL, thread_function, &n);
    }

    //wait for all threads to finish         
    for (int i = 0; i < num_threads; i++) {
        pthread_join(threads[i], NULL);
    }

    pthread_mutex_destroy(&barrier.mutex);

    // End measuring time
    gettimeofday(&end, NULL);
    time_taken = (end.tv_sec - start.tv_sec) + (end.tv_usec - start.tv_usec) / 1e6;
    printf("Time taken: %f seconds\n", time_taken);

    return 0;
}

void* thread_function(void* arg) {
    int n = *((int*)arg);
    int local_sense = 0;

    for (int i = 0; i <n; i++) {
        barrier_wait(&barrier, &local_sense);
    }
    
    return NULL;
}

void barrier_init(thread_barier* b, int num_threads) {
    b->barrier_count = 0;
    b->num_threads = num_threads;
    b->sense = 0;
    pthread_mutex_init(&b->mutex, NULL);
}

void barrier_wait(thread_barier* b, int* local_sense) {

    //Flip the local sense for this thread to indicate its arrival at the barrier
    *local_sense = !(*local_sense); 

    //Lock mutex before updating the shared barrier count
    pthread_mutex_lock(&b->mutex);
    b->barrier_count++;

    //If this is the last thread to reach the barrier  reset the count for next use , 
    // update the global sense to signal and wake up all the threads  to continue 
    if (b->barrier_count == b->num_threads) {
        b->barrier_count = 0;
        b->sense = *local_sense;
        pthread_mutex_unlock(&b->mutex);

    //if we are not on the last thread then unlock the mutex and wait until the global sense changes
    //this means that the last thread has arrived and changed the global sense
    } else {
        pthread_mutex_unlock(&b->mutex);
        
        while (b->sense != *local_sense) {
            // busy wait
        }
    }
}