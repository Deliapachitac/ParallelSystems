#include <stdio.h>
#include <stdlib.h>
#include <omp.h>
#include <time.h>

void generate_polynomials(int n, int* P);
void multiply_serial(int n, const int* P1, const int* P2, int* result);

int main(int argc, char* argv[]) {
    
    // We check if the user  provided the correct number of arguments and we save them in variables 
    if (argc != 3) {   
        fprintf(stderr, "Wrong number of arguments. Usage: %s <degree_of_polynomials> <number_of_threads>\n", argv[0]);
        return -1; 
    } 
    int n =atoi(argv[1]);
    int number_of_threads = atoi(argv[2]);


    // Set the number of threads for OpenMP
    omp_set_num_threads(number_of_threads);

    // Variables for measuring time
    double start, end;
    double initialization_time, serial_time, parallel_time;

    start = omp_get_wtime();

    // The two polynomials will be stored in arrays that we dynamically allocate 
    int* P1 = (int*)malloc((n+1) * sizeof(int));
    int* P2 = (int*)malloc((n+1) * sizeof(int));

    //Generate the two polynomials  
    generate_polynomials( n , P1);
    generate_polynomials( n , P2);

    //Allocate memory for the result of the multiplication
    int* result_serial = (int*)malloc((2*n+1) * sizeof(int));
    int* result_parallel = (int*)malloc((2*n+1) * sizeof(int));
    
    end = omp_get_wtime();
    initialization_time = end - start;
    printf("Initialization time: %f seconds\n", initialization_time);
    
    
    /////////////// SERIAL MULTIPLICATION ///////////////
    start = omp_get_wtime();
    multiply_serial(n, P1, P2, result_serial);
    end = omp_get_wtime();
    serial_time = end - start;
    printf("Serial multiplication time: %f seconds\n", serial_time);

    
    /////////////// PARALLEL MULTIPLICATION ///////////////         
    
    start = omp_get_wtime();
    
    // Initialize parallel result
    for (int i = 0; i <= 2*n; i++) {
        result_parallel[i] = 0;
    }

    //Creates a parallel block and distributes the iterations of the for loop amogn the threads
    // The usage of schedule(static)  divides the iterations into equal sized chunks
    #pragma omp parallel for  schedule( static)
    for (int i = 0; i <= 2*n; i++ ) {

        // Calculate the starting and ending index for the inner loop based on the current value of i
        int start=(i > n) ?(i-n):0 ;  
        int end =(i <n) ? i :n ;     
          
        for (int j =start; j<= end; j++ ){  
            result_parallel[i] += P1[j] *P2[i-j];
        }
       
    }

    end = omp_get_wtime();
    parallel_time = end - start;  
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
    free(P2) ;
    free(result_serial);
    free(result_parallel);

    return  0;
}

void generate_polynomials(int n, int* P) {
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

void multiply_serial(int n, const int* P1, const int* P2, int* result) {
    
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