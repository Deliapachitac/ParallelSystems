#include <pthread.h>
#include <stdio.h>
#include <errno.h>
#include <time.h>
#include <stdlib.h>
#include <sys/time.h>
struct array_stats_s {
    long long int info_array_0;
    long long int info_array_1;
    long long int info_array_2;
    long long int info_array_3;
} array_stats, array_stats_serial;

int** arrays;
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
    srand((unsigned) time(NULL));
    arrays = malloc(4 * sizeof(int*));
    for(int i = 0; i < 4; i++){
        arrays[i] = malloc(size * sizeof(int));
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
    if( array_stats.info_array_0 == array_stats_serial.info_array_0 &&
        array_stats.info_array_1 == array_stats_serial.info_array_1 &&
        array_stats.info_array_2 == array_stats_serial.info_array_2 &&
        array_stats.info_array_3 == array_stats_serial.info_array_3){
            printf("Results are correct!\n");
        }
    else{
         printf("Results are incorrect!\n");
    }
}