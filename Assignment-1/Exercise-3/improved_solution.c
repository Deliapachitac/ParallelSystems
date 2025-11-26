#include <pthread.h>
#include <stdio.h>
#include <errno.h>
#include <time.h>
#include <stdlib.h>
#include <sys/time.h>
#include "../Shared/my_rand.h"
#define MATCHES_ZERO(a) \
    ((a)[0]->info_array == array_zeroes[0]&& \
     (a)[1]->info_array == array_zeroes[1] && \
     (a)[2]->info_array == array_zeroes[2] && \
     (a)[3]->info_array == array_zeroes[3])

typedef struct array_stats_s{
    long long int info_array;
}array_stats_s __attribute__((aligned(64)));
array_stats_s** array_stats; 
array_stats_s** array_stats_serial; 
int** arrays;
int array_zeroes[4] = {0, 0, 0, 0};
long size;
void *Count_Non_Zero(void* rank){
    long my_rank = (long) rank;
    array_stats_s* stat = array_stats[my_rank];
    int* array = arrays[my_rank];
    for(long i = 0; i < size; i++){
        stat->info_array += (array[i] != 0);
    }
    return NULL;
}

void Count_Non_Zero_Serial(){
    int* array0 = arrays[0];
    int* array1 = arrays[1];
    int* array2 = arrays[2];
    int* array3 = arrays[3];
    array_stats_s* stat0 = array_stats_serial[0];
    array_stats_s* stat1 = array_stats_serial[1];
    array_stats_s* stat2 = array_stats_serial[2];
    array_stats_s* stat3 = array_stats_serial[3];
    for(int i = 0; i< size; i++){
        stat0->info_array += (array0[i] != 0);
        stat1->info_array += (array1[i] != 0);
        stat2->info_array += (array2[i] != 0);
        stat3->info_array += (array3[i] != 0);
    }
}

int main(int argc, char* argv[]){
    if(argc != 2){
        fprintf(stderr, "Correct Usage: ./solution [Size of array]\n");
        return 1;
    }
    errno = 0;
    size = strtol(argv[1], NULL, 10);
    if(errno != 0){
        fprintf(stderr, "Size of array argument should be a number\n");
    }
    struct timeval start, end;
    double elapsed;
    pthread_t* thread_handles;
    gettimeofday(&start, NULL);
    thread_handles = malloc(4 * sizeof(pthread_t));
    arrays = malloc(4 * sizeof(int*));
    array_stats = malloc(4 * sizeof(array_stats_s*));
    array_stats_serial = malloc(4 * sizeof(array_stats_s*));
    
    for (int i = 0; i < 4; i++) {
        arrays[i] = malloc(size * sizeof(int));
        array_stats[i] = malloc(sizeof(array_stats_s));
        array_stats_serial[i] = malloc(sizeof(array_stats_s));
        array_stats[i]->info_array = 0;
        array_stats_serial[i]->info_array = 0;
    }
    unsigned int seed = time(NULL);
    //Avoid dereferncing pointer
    int *a0 = arrays[0];
    int *a1 = arrays[1];
    int *a2 = arrays[2];
    int *a3 = arrays[3];
    for(int j = 0; j < size ; j++){
        //Use rand only once to reduce function call overhead
        unsigned r = my_rand(&seed);
        int v0 =  r        % 10;
        int v1 = (r >> 8)  % 10;
        int v2 = (r >> 16) % 10;
        int v3 = (r >> 24) % 10;

        a0[j] = v0;
        a1[j] = v1;
        a2[j] = v2;
        a3[j] = v3;

        // Branchless zero detection
        array_zeroes[0] += (v0 != 0);
        array_zeroes[1] += (v1 != 0);
        array_zeroes[2] += (v2 != 0);
        array_zeroes[3] += (v3 != 0);
    }
    
    gettimeofday(&end,NULL);
    elapsed = (end.tv_sec - start.tv_sec) + (end.tv_usec - start.tv_usec) / 1e6;
    printf("Initializing structs needed took: %f seconds\n", elapsed);
    gettimeofday(&start, NULL);
    for(long thread = 0; thread < 4; thread++ ){
        pthread_create(&thread_handles[thread], NULL, Count_Non_Zero, (void*) thread);
    }
    for(long thread = 0; thread < 4; thread++){
        pthread_join(thread_handles[thread], NULL);
    }
    gettimeofday(&end,NULL);
    elapsed = (end.tv_sec - start.tv_sec) + (end.tv_usec - start.tv_usec) / 1e6;
    printf("Parallel execution for array size of %ld took: %f seconds\n",size, elapsed);
    gettimeofday(&start, NULL);
    Count_Non_Zero_Serial();
    gettimeofday(&end,NULL);
    elapsed = (end.tv_sec - start.tv_sec) + (end.tv_usec - start.tv_usec) / 1e6;
    printf("Serial execution for array size of %ld took: %f seconds\n",size, elapsed);
    if( MATCHES_ZERO(array_stats) && MATCHES_ZERO(array_stats_serial)){
            printf("Results are correct!\n");
        }
    else{
         printf("Results are incorrect!\n");
    }
    for(int i =0 ; i<4;i++){
        free(arrays[i]);
    }
    free(arrays);
    free(array_stats);
    free(array_stats_serial);
    free(thread_handles);

}