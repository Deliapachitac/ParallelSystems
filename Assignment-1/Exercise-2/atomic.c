#include <stdio.h>
#include <stdlib.h>
#include <pthread.h>
#include <sys/time.h>

// Global counter 
int counter=0; 


//
struct thread_info {
    int thread_id;
    int iterations;
};
typedef struct thread_info* Thread_info;

void* thread_function(void* arg);


int main(int argc, char* argv[]){
           
    // We check if the user  provided the correct number of arguments and we save them in variables 
    if (argc != 3) {   
        fprintf(stderr, "Wrong number of arguments. Usage: %s <degree_of_polynomials> <number_of_threads>\n", argv[0]);
        return -1; 
    }
    int thread_number =atoi(argv[1]);
    int iterations = atoi(argv[2]);

    //Initialize the threads 
    pthread_t threads[thread_number];
    Thread_info thread_data[thread_number];

    // Variables for measuring time
    struct timeval start, end;
    double time_taken;

    // Start measuring initialization time 
    gettimeofday(&start, NULL);

    // 
    for (int i=0; i < thread_number; i++){
        thread_data[i] = (Thread_info) malloc(sizeof(struct thread_info));
        thread_data[i]->thread_id = i;
        thread_data[i]->iterations = iterations;
        pthread_create(&threads[i], NULL, thread_function, thread_data[i]);
    }

    // Wait for all threads to finish
    for (int i=0; i < thread_number; i++){
        pthread_join(threads[i], NULL);
    }

    // End measuring time
    gettimeofday(&end, NULL);
    time_taken = (end.tv_sec - start.tv_sec) + (end.tv_usec - start.tv_usec) / 1e6;
    printf("Time taken for atomic increment: %f seconds\n", time_taken);
    printf("Final counter value: %d\n", counter);

}

void* thread_function(void* arg){

    Thread_info info = (Thread_info)arg;
    
    for (int i=0; i < info->iterations; i++){

        // Add 1 to counter atomically and return the new value
        __atomic_add_fetch(&counter, 1, __ATOMIC_SEQ_CST);
    }

    pthread_exit(NULL);
}