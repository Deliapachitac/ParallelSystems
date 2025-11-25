#include <stdio.h>
#include <stdlib.h>
#include <pthread.h>
#include <time.h>
#include <sys/time.h>

// Data structure to hold information for each thread
struct data{
    int id;
    int n;
    int num_threads;
    const int *P1;
    const int *P2;
    int *result;
} ;
typedef struct data* Thread_data;

void generate_polynomials(int n, int*P);
void multiply_serial(int n,const int* P1,const int* P2, int* result);
void* multiply_parallel(void* arg);


int main(int argc, char* argv[]){
           
    // We check if the user  provided the correct number of arguments and we save them in variables 
    if (argc != 3) {   
        fprintf(stderr, "Wrong number of arguments. Usage: %s <degree_of_polynomials> <number_of_threads>\n", argv[0]);
        return -1; 
    }
    int n =atoi(argv[1]);
    int number_of_threads = atoi(argv[2]);

    // Variables for measuring time
    struct timeval start, end;
    double initialization_time, serial_time, parallel_time;

    // Start measuring initialization time 
    gettimeofday(&start, NULL);

    // The two polynomials will be stored in arrays that we dynamically allocate 
    int* P1 = (int*)malloc((n+1) * sizeof(int));
    int* P2 = (int*)malloc((n+1) * sizeof(int));

    //Generate the two polynomials  
    generate_polynomials( n , P1);
    generate_polynomials( n , P2);

    //Allocate memory for the result of the multiplication
    int* result_serial = (int*)malloc((2*n+1) * sizeof(int));
    int* result_parallel = (int*)malloc((2*n+1) * sizeof(int));
    
    // End measuring initialization time
    gettimeofday(&end, NULL);
    initialization_time = (end.tv_sec - start.tv_sec) + (end.tv_usec - start.tv_usec) / 1e6;
    printf("Initialization time: %f seconds\n", initialization_time);
    
    /////////////// SERIAL MULTIPLICATION ///////////////

    // Start measuring serial multiplication time
    gettimeofday(&start, NULL);
    // Calculate the serial multiplication
    multiply_serial(n, P1, P2, result_serial);
    // End measuring serial multiplication time
    gettimeofday(&end, NULL);
    serial_time = (end.tv_sec - start.tv_sec) + (end.tv_usec - start.tv_usec) / 1e6;
    printf("Serial multiplication time: %f seconds\n", serial_time);


    /////////////// PARALLEL MULTIPLICATION ///////////////

    // Start measuring parallel multiplication time
    gettimeofday(&start, NULL);
    
    // Initialize parallel result
    for (int i = 0; i <= 2*n; i++) {
        result_parallel[i] = 0;
    }

    // Create threads and perform parallel multiplicatio
    pthread_t threads[number_of_threads];
    Thread_data data_thread[number_of_threads];

    // For each thread we create a data structure that  contains all the necessary information  
    for (int i = 0; i < number_of_threads; i++) {
        data_thread[i] = (Thread_data)malloc(sizeof(struct data));
        data_thread[i]->id = i;
        data_thread[i]->n = n;
        data_thread[i]->num_threads = number_of_threads;
        data_thread[i]->P1 = P1;
        data_thread[i]->P2 = P2;
        data_thread[i]->result = result_parallel;
        pthread_create(&threads[i], NULL, multiply_parallel, data_thread[i]);
    }

    // Wait for all threads to finish and free their data structures
    for(int i=0; i < number_of_threads; i++) {
        pthread_join(threads[i], NULL);
        free(data_thread[i] );       
    }

    // End measuring parallel multiplication time
    gettimeofday(&end, NULL);
    parallel_time = (end.tv_sec - start.tv_sec) + (end.tv_usec - start.tv_usec) / 1e6;
    printf("Parallel multiplication time: %f seconds\n", parallel_time);


    ////////////// VERIFY CORRECTNESS ///////////////
    int flag = 1;
    for (int i = 0; i <= 2*n; i++) {
        if (result_serial[i] != result_parallel[i]) {
            flag     = 0;
            break;
        }
    }
    printf("Parallel multiplication correctness: %s\n", flag ? "OK" : "Mismatch");


    // Free the allocated memory
    free(P1);
    free(P2);
    free(result_serial);
    free(result_parallel);

    return 0;
}

void generate_polynomials(int n , int*P){

    for (int i = 0; i <= n; i++) {

        int non_zero_value = 0;
        // Ensure the generated value is non-zero
        while (non_zero_value == 0) {
    
            // Generate a random value between -n and n
            non_zero_value = (rand() % (2*n+1)) -n;
        }
        P[i] = non_zero_value; 
    }

}

void multiply_serial(int n,const int* P1,const int* P2, int* result){

    // Initialize the result array to zero
    for (int i = 0; i <= 2*n; i++) {
        result[i] = 0;
    }

    // Perform polynomial multiplication
    for (int i = 0; i <= n; i++) {
        for (int j = 0; j <= n; j++) {
            result[i + j] += P1[i] * P2[j];
        }
    }

}


void *multiply_parallel(void* arg){

    Thread_data data = (Thread_data)arg;
    int id = data->id;
    int n = data->n;
    int num_threads = data->num_threads;
    const int* P1 = data->P1;
    const int* P2 = data->P2;
    int* result = data->result;

    //Each thread will compute a portion of the result array
    int strart_index = id * (2*n + 1) /num_threads;
    int end_index = (id + 1)* (2*n + 1)/num_threads;
              
    for (int i= strart_index; i < end_index; i++){

        for (int j=0; j <= n; j++){
            int k = i-j;
            if (k >= 0 && k <=n){
                result[i]+= P1[j]* P2[k];
            }
        }
    }

    pthread_exit(NULL);
}