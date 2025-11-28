#include <stdio.h>
#include <stdlib.h>
#include <pthread.h>
#include <sys/time.h>
#include <string.h>

// Global counter
int counter = 0;   
                 
// Mutex and rwlock declarations    
pthread_mutex_t mutexcounter;
pthread_rwlock_t  rwlock;

//Thread info struct
struct thread_info {
    int  thread_id;
    int  iterations ;            
};          
typedef struct thread_info* Thread_info;
          
//A way to specify the mode of synchronization 
typedef enum { ATOMIC, MUTEX, RWLOCK } Mode;
Mode mode;

void* thread_function(void* arg);

int main(int argc, char* argv[]) {
    if (argc != 4) {
        fprintf(stderr, "Usage: %s <mode: atomic|mutex|rwlock> <threads> <iterations>\n", argv[0]);
        return -1;
    }

    //determine the mode based on user input      
    if (strcmp(argv[1], "atomic") == 0) {
        mode = ATOMIC; 
    } else if (strcmp(argv[1],"mutex") == 0) {
        mode = MUTEX;   
        pthread_mutex_init(&mutexcounter, NULL);
    } else if (strcmp(argv[1],"rwlock") == 0) {
        mode = RWLOCK;
        pthread_rwlock_init(&rwlock, NULL);
    } else {
        fprintf(stderr, "Invalid mode. Choose atomic, mutex, or rwlock.\n");
        return -1;
    }

    int thread_number = atoi(argv[2]);
    int iterations = atoi(argv[3]);


    pthread_t threads[thread_number];
    Thread_info thread_data[thread_number];


    // Start measuring time
    struct timeval start, end;
    double time_taken;
    gettimeofday(&start, NULL);

    //create the threads and pass them the necessary argumnts
    for (int i = 0; i < thread_number; i++) {
        thread_data[i] = (Thread_info)malloc(sizeof(struct thread_info));
        thread_data[i]->thread_id = i;
        thread_data[i]->iterations = iterations;
        pthread_create(&threads[i], NULL, thread_function, thread_data[i]);
    }

    // Wait for all threads to finish     
    for (int i = 0; i < thread_number; i++) {
        pthread_join(threads[i], NULL);
        free(thread_data[i]);
    }

    // End measuring time
    gettimeofday(&end, NULL);
    time_taken = (end.tv_sec - start.tv_sec) + (end.tv_usec - start.tv_usec) / 1e6;

    const char* mode_str = (mode == ATOMIC) ? "atomic" :
                           (mode == MUTEX)  ? "mutex"  : "rwlock";

    printf("Time taken for %s increment: %f seconds\n", mode_str, time_taken);
    printf("Final counter value: %d\n", counter);


    if (mode == MUTEX) {
        pthread_mutex_destroy(&mutexcounter);   
    }
    if (mode == RWLOCK) {
        pthread_rwlock_destroy(&rwlock);
    }

    return 0;
}


           
void* thread_function(void* arg) {
    Thread_info info = (Thread_info)arg;

    for (int i = 0; i < info->iterations; i++) {
        switch (mode) {
            case ATOMIC:        
                __atomic_add_fetch(&counter, 1, __ATOMIC_SEQ_CST);
                break;
         
            case  MUTEX:
                pthread_mutex_lock(&mutexcounter); 
                counter++;  
                pthread_mutex_unlock(&mutexcounter);
                break;
       
            case  RWLOCK:
                pthread_rwlock_wrlock(&rwlock);
                counter++;  
                pthread_rwlock_unlock(&rwlock);
                break;
        }
    }

    pthread_exit(NULL);
}