#include <stdio.h>
#include <stdlib.h>
#include <pthread.h>


struct thread_args {
    int id;
    int n;
    int num_threads;
};
typedef struct thread_args* ThreadArgs;

int barrier_count = 0;
pthread_mutex_t barrier_mutex;
pthread_cond_t barrier_cond;

void* thread_function(void* arg);

int main(int argc, char* argv[]) {
    if (argc != 3) {
        fprintf(stderr, "Usage: %s <threads> <barriers>\n", argv[0]);
        exit(EXIT_FAILURE);
    }

    int thread_count = atoi(argv[1]);
    int barrier_total = atoi(argv[2]);

    pthread_t* threads = malloc(thread_count * sizeof(pthread_t));

    pthread_mutex_init(&barrier_mutex, NULL);
    pthread_cond_init(&barrier_cond, NULL);

    for (long t = 0; t < thread_count; t++) {
        ThreadArgs data = malloc(sizeof(struct thread_args));
        data->id = t;
        data->n = barrier_total;
        data->num_threads = thread_count;
        pthread_create(&threads[t], NULL, thread_function, (void*)data);
    }

    for (int t = 0; t < thread_count; t++)
        pthread_join(threads[t], NULL);

    pthread_mutex_destroy(&barrier_mutex);
    pthread_cond_destroy(&barrier_cond);
    free(threads);

    printf("All threads completed %d barriers\n", barrier_total);
    return 0;
}

void* thread_function(void* arg) {
    ThreadArgs data = (ThreadArgs)arg;
    int id = data->id;
    int n = data->n;
    int thread_count = data->num_threads;
    free(data);
    for (int i = 0; i < n; i++) {
        pthread_mutex_lock(&barrier_mutex);
        barrier_count++;
        if (barrier_count == thread_count) {
            barrier_count = 0;           
            pthread_cond_broadcast(&barrier_cond);
        } else {
            pthread_cond_wait(&barrier_cond, &barrier_mutex);
        }
        pthread_mutex_unlock(&barrier_mutex);
    }
    return NULL;
}