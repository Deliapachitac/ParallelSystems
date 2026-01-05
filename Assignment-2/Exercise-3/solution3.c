#include <stdio.h>
#include <stdlib.h>
#include <time.h>   
#include <string.h> 
#include <omp.h>
#include "../Shared/my_rand.h"

void merge(int *array,int  n, int  *temp) {

    int i = 0; // Pointer for the left half        
    int j = n / 2;  // Pointer for the right half    
    int k = 0;  // Pointer for the temp array         

    // copy elements from both halves into temp in sorted order
    while (i < n / 2 && j < n) {
        if (array[i] < array[j]) {
            temp[k++] = array[i++];
        } else {
            temp[k++] = array[j++];
        }
    }

    // Copy any  remaining elements  from the left half
    while (i < n / 2){ 
        temp[k++] = array[i++];
    }
    // Copy any remaining elements from the right half
    while (j < n){    
        temp[k++] = array[j++];
    }

    // Copy the sorted elements back into the original array
    memcpy(array, temp, n * sizeof(int));
}


void mergesort_serial(int *array, int n, int *temp) {
    
    //if the array has one or no elements  it is already sorted 
    if (n < 2){
        return;
    }

    // Divide and work on each half separately 
    mergesort_serial(array, n/2, temp);                 
    mergesort_serial(array + n/2, n- n/2 , temp+ n/2); 

    //Merge the two results
    merge(array, n, temp);
}

void mergesort_parallel(int *array, int n, int *temp) {
    
    //if the array has one or no elements  it is already sorted 
    if (n< 2){
        return ; 
    }

    // Divide and work on each half separately using tasks
    #pragma omp task
    mergesort_parallel(array, n/2 ,temp);
          
    #pragma omp task        
    mergesort_parallel(array + n/2, n - n/2 , temp+ n/2);

    // Wait for both tasks to complete
    #pragma omp taskwait

    //Merge the two results
    merge(array, n, temp);
}

void mergesort_parallel_optimal(int *array, int n, int *temp) {
    
    //if the array has one or no elements  it is already sorted 
    if (n< 2){
        return ; 
    }

    //The condition if(n > 1000) prevents the creation of too many tasks for small segments of the array (overhead)
    #pragma omp task shared(array, temp) if(n > 1000)
    mergesort_parallel_optimal(array, n/2, temp);

    #pragma omp task shared(array, temp) if(n > 1000)
    mergesort_parallel_optimal(array + n/2, n - n/2, temp + n/2);
    
    // We wait for both tasks to complete
    #pragma omp taskwait
    merge(array, n, temp);


}

int main(int argc, char *argv[]) {

    if (argc != 4 && argc!= 3) {  
        fprintf(stderr, "Wrong number of arguments. Usage: %s <number_of_elements> <mode : s/p> <number_of_threads>\n", argv[0]);
        return -1; 
    }

    int n = atoi(argv[1]);
    char mode = argv[2][0]; // 's' for serial, 'p' for parallel we take only the first character
    int num_threads  = atoi(argv[3]);

    // Allocate memory for the array and a temporary array
    int *array = (int *)malloc(n * sizeof(int));
    int *temp =(int *)malloc(n * sizeof(int));
    int *backup = (int *)malloc(n * sizeof(int));

    // Initialize the array with random integers
    unsigned seed = time(NULL);
    for (int i = 0; i < n; i++) {
        array[i] = my_rand(&seed);
        backup[i] = array[i];
    }

    double start, end;

    /////////////// SERIAL MERGESORT ///////////////
    if (mode == 's') {
        start = omp_get_wtime();
        mergesort_serial(array, n, temp);
        end = omp_get_wtime();
        printf("Serial mergesort time: %f seconds\n", end - start);
    
    /////////////// PARALLEL MERGESORT ///////////////    
    }else if (mode == 'p') {
    
        
        start = omp_get_wtime();
        omp_set_num_threads(num_threads);
        
        #pragma omp parallel
        {
            #pragma omp single
            mergesort_parallel(array, n, temp);
        }

        end = omp_get_wtime();
        printf("Parallel mergesort time: %f seconds\n", end - start);  
        

        start = omp_get_wtime();
        #pragma omp parallel
        {
            #pragma omp single
            mergesort_parallel_optimal(backup, n, temp); 
        }
        end = omp_get_wtime();
        printf("Parallel mergesort optimal time: %f seconds\n", end - start);
        

    }

    
    ////////////// VERIFY CORRECTNESS ///////////////
    int flag  = 1;
    for (int i = 0; i < n-1;i++) {
        if (array[i] > array[i+1]) {
            flag = 0;
            break;
        }
    }
    printf("Mergesort correctness: %s\n", flag ? "OK" : "Wrong Result");

    int flag_optimal  = 1;
    for (int i = 0; i < n-1;i++) {       
        if (backup[i] > backup[i+1]) {
            flag_optimal = 0;
            break;
        }
    }
    printf("Mergesort optimal correctness: %s\n", flag_optimal ? "OK" : "Wrong Result");

    // Free allocated memory 
    free(array);
    free(temp);
    free(backup);

    return 0;
}