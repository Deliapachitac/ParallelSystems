#include <stdio.h>
#include <stdlib.h>
#include <pthread.h>

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

    // 
    pthread_t tid[thread_number];
    pthread_barrier_init(&barrier, NULL, thread_number);

    for (int i = 0; i < thread_number; i++)
        pthread_create(&tid[i], NULL, thread_function, &n);

    for (int i = 0; i < thread_number; i++)
        pthread_join(tid[i], NULL);

    pthread_barrier_destroy(&barrier);
    return 0;
}

void* thread_function(void* arg) {
    int n = *((int*) arg);
    for (int i = 0; i < n; i++) {
        
        pthread_barrier_wait(&barrier);
    }
    return NULL;
}