#include <stdio.h>
#include <stdlib.h>
#include <pthread.h>
#include <stdatomic.h>

// Shared variables
atomic_int count;
atomic_int global_sense;

struct thread_args {
    int id;
    int n;
    int num_threads;
};
typedef struct thread_args* ThreadArgs;

void* thread_function(void* arg);

int main(int argc, char* argv[]){
           
    // We check if the user  provided the correct number of arguments and we save them in variables 
    if (argc != 3) {   
        fprintf(stderr, "Wrong number of arguments. Usage: %s <degree_of_polynomials> <number_of_threads>\n", argv[0]);
        return -1; 
    }
    int n =atoi(argv[1]);
    int number_of_threads = atoi(argv[2]);

    pthread_t threads[number_of_threads];
    atomic_init(&count, 0);
    atomic_init(&global_sense, 0);

    for (int i = 0; i < number_of_threads; i++) {
        ThreadArgs data = malloc(sizeof(struct thread_args));
        data->id = i;
        data->n = n;
        data->num_threads = number_of_threads;
        pthread_create(&threads[i], NULL, thread_function, (void*)data);
    }

    for (int i = 0; i < number_of_threads; i++)
        pthread_join(threads[i], NULL);

    printf("Finished barrier test with %d threads and %d iterations\n", number_of_threads, n);
    return 0;
}


void* thread_function(void* arg) {
    ThreadArgs data = (ThreadArgs)arg;
    int local_sense = 0;   // must start same as global_sense

    for (int i = 0; i < data->n; i++) {
        local_sense = !local_sense; 
        int position = atomic_fetch_add(&count, 1);

        if (position == data->num_threads - 1) {
            atomic_store(&count, 0);
            atomic_store(&global_sense, local_sense);
        } else {
            while (atomic_load(&global_sense) != local_sense) {
                // busy wait
            }
        }
    }

    return NULL;
}
