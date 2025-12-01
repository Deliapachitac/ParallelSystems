#include <stdio.h>
#include <stdlib.h>
#include <pthread.h>
#include <sys/time.h>

         
pthread_barrier_t barrier;

void* thread_function(void* arg);

int main(int argc, char* argv[]){
           
    // We check if the user  provided the correct number of arguments and we save them in variables 
    if (argc != 3) {   
        fprintf(stderr, "Wrong number of arguments. Usage: %s <degree_of_polynomials> <number_of_threads>\n", argv[0]);
        return -1; 
    }
    int thread_number =atoi(argv[1]);
    int n = atoi(argv[2]);
    
    // Start measuring time
    struct timeval start, end;
    double time_taken;
    gettimeofday(&start, NULL);
    
    // Initialize threads and barrier       
    pthread_t tid[thread_number];
    pthread_barrier_init(&barrier, NULL, thread_number); 
    
          
    for (int i = 0; i < thread_number; i++)  {
        pthread_create(&tid[i],  NULL, thread_function ,&n) ;
    }
                
    // Wait for all threads to finish
    for (int i = 0; i < thread_number; i++)
        pthread_join(tid[i] , NULL);  
    
        

    pthread_barrier_destroy(&barrier);

    
    // End measuring time
    gettimeofday(&end, NULL);
    time_taken = (end.tv_sec - start.tv_sec) + (end.tv_usec - start.tv_usec) / 1e6;
    printf("Time taken: %f seconds\n", time_taken);

    
    return 0;
}

void* thread_function(void* arg) {
    int n = *((int*) arg);
    
    // This is the iteration from the exercise
    for (int i = 0; i < n; i++) {
        pthread_barrier_wait(&barrier);
    }

    return NULL;
}