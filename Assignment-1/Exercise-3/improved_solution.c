#include <pthread.h>
#include <stdio.h>
#include <errno.h>
#include <time.h>
#include <stdlib.h>
#include <sys/time.h>
typedef struct array_stats_s{
    long long int info_array;
    char padding[56];
}array_stats_s;
array_stats_s* array_stats; 
array_stats_s* array_stats_serial; 
int** arrays;
long size;
void *Count_Non_Zero(void* rank){
    long my_rank = (long) rank;
    for(long i = 0; i < size; i++){
        if(arrays[my_rank][i] != 0){
            array_stats[my_rank].info_array++;
        }
    }
    return NULL;
}

void Count_Non_Zero_Serial(){
    for(int i = 0; i< size; i++){
        if(arrays[0][i] != 0){
            array_stats_serial[0].info_array++;
        }
        if(arrays[1][i] != 0){
            array_stats_serial[1].info_array++;
        }
        if(arrays[2][i] != 0){
            array_stats_serial[2].info_array++;
        }
        if(arrays[3][i] != 0){
            array_stats_serial[3].info_array++;
        }
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
    srand((unsigned) time(NULL));
    arrays = malloc(4 * sizeof(int*));
    array_stats = malloc(4 * sizeof(array_stats_s));
    array_stats_serial = malloc(4 * sizeof(array_stats_s));
    for(int i = 0; i < 4; i++){
        arrays[i] = malloc(size * sizeof(int));
        array_stats[i].info_array = 0;
        array_stats_serial[i].info_array = 0;
        for(int j = 0; j < size ; j++){
            arrays[i][j] = rand() % 10;
        }
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
    if( array_stats[0].info_array == array_stats_serial[0].info_array &&
        array_stats[1].info_array == array_stats_serial[1].info_array &&
        array_stats[2].info_array == array_stats_serial[2].info_array &&
        array_stats[3].info_array == array_stats_serial[3].info_array){
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