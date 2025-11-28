#include <pthread.h>
#include <stdio.h>
#include <errno.h>
#include <time.h>
#include <stdlib.h>
#include <sys/time.h>
#include "../Shared/my_rand.h"
#define MATCHES_ZERO(a) \
    ((a).info_array_0 == array_zeroes[0]&& \
     (a).info_array_1 == array_zeroes[1] && \
     (a).info_array_2 == array_zeroes[2] && \
     (a).info_array_3 == array_zeroes[3])

typedef struct array_stats_s {
    long long int info_array_0;
    char padding1[64 - sizeof(long long int)];
    long long int info_array_1;
    char padding2[64 - sizeof(long long int)];
    long long int info_array_2;
    char padding3[64 - sizeof(long long int)];
    long long int info_array_3;
    char padding4[64 - sizeof(long long int)];
}array_stats_s;
array_stats_s array_stats, array_stats_serial;
int** arrays;
long long int* array_zeroes;
long size;
void *Count_Non_Zero(void* rank){
    long my_rank = (long) rank;
    
        
        switch(my_rank){
            case 0:
                for(int i = 0; i < size; i++){
                    if(arrays[0][i] != 0){
                        array_stats.info_array_0++;
                    }
                }
                break;
            case 1:
                for(int i = 0; i < size; i++){
                    if(arrays[1][i] != 0){
                        array_stats.info_array_1++;
                    }
                }
                break;
            case 2:
                for(int i = 0; i < size; i++){
                    if(arrays[2][i] != 0){
                        array_stats.info_array_2++;
                    }
                }
                break;
            case 3:
                for(int i = 0; i < size; i++){
                    if(arrays[3][i] != 0){
                        array_stats.info_array_3++;
                    }
                }
                break;      
            }
        
    
    
    return NULL;
}

void Count_Non_Zero_Serial(){
    for(int i = 0; i< size; i++){
        if(arrays[0][i] != 0){
            array_stats_serial.info_array_0++;
        }
        if(arrays[1][i] != 0){
            array_stats_serial.info_array_1++;
        }
        if(arrays[2][i] != 0){
            array_stats_serial.info_array_2++;
        }
        if(arrays[3][i] != 0){
            array_stats_serial.info_array_3++;
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
    array_stats.info_array_0 = 0;
    array_stats.info_array_1 = 0;
    array_stats.info_array_2 = 0;
    array_stats.info_array_3 = 0;
    unsigned int seed = time(NULL);
    array_zeroes = malloc(4*sizeof(long long int));
    arrays = malloc(4 * sizeof(int*));
    for(int i=0;i<4;i++){
        arrays[i] = malloc(size * sizeof(int));
    }
    for(int j = 0; j < size ; j++){
        //Use rand only once to reduce function call overhead
        unsigned r = my_rand(&seed);
        int v0 =  r        % 10;
        int v1 = (r >> 8)  % 10;
        int v2 = (r >> 16) % 10;
        int v3 = (r >> 24) % 10;

        arrays[0][j] = v0;
        arrays[1][j] = v1;
        arrays[2][j] = v2;
        arrays[3][j] = v3;

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
    if(MATCHES_ZERO(array_stats) && MATCHES_ZERO(array_stats_serial)){
            printf("Results are correct!\n");
        }
    else{
         printf("Results are incorrect!\n");
    }
    for(int i =0 ; i<4;i++){
        free(arrays[i]);
    }
    free(arrays);
    free(array_zeroes);
    free(thread_handles);
}