#include <stdio.h>
#include <stdlib.h>
#include <time.h>
#include <sys/time.h>
#include <immintrin.h>

void generate_polynomials(int n, int *P);
void multiply_serial(int n, const int *P1, const int *P2, int *result);
void multiply_simd(int n, const int *P1, const int *P2, int *result);

int main(int argc, char *argv[]) {

    // We check if the user provided the correct number of arguments and we save them in variables
    if (argc != 2) {
        fprintf(stderr, "Wrong number of arguments.Usage: %s <degree_of_polynomials>\n", argv[0]);
        return -1;
    }

    //Convert degree argument to integer
    int n = atoi(argv[1]);


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

    ///////////////// SIMD MULTIPLICATION ///////////////
    gettimeofday(&start, NULL);
    multiply_simd(n, P1, P2, result_parallel);
    gettimeofday(&end, NULL);
    parallel_time = (end.tv_sec - start.tv_sec) + (end.tv_usec - start.tv_usec) / 1e6;
    printf("SIMD multiplication time: %f seconds\n", parallel_time );

    ////////////// VERIFY CORRECTNESS ///////////////
    int flag = 1;
    for (int i = 0; i <= 2*n; i++) {
        if (result_serial[i] != result_parallel[i]) {
            flag     = 0;
            break;
        }
    }
    printf("Parallel multiplication correctness: %s\n", flag ? "OK" : "Mismatch");
    
    if (parallel_time > 0.0) {
        printf("Speedup (serial / SIMD): %.2fx\n", serial_time / parallel_time);
    }

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



void multiply_simd(int n, const int *P1, const int *P2, int *result) {
    
    //initialize result array to zero
    for (int i = 0; i <= 2 * n; i++) {
        result[i] = 0;
    }

    //We iterate over each element of the P1 polynomial
    for (int i = 0; i <= n; i++) {
        int a = P1[i];
        __m256i va = _mm256_set1_epi32(a); // creates a vector containing 8 copies of a

        int j = 0;
        
        // Process 8 elements of P2 at a time 
        for (; j + 7 <= n; j += 8) {
            __m256i vb = _mm256_loadu_si256((const __m256i *)(P2+ j)); // load 8 consecutive elements from P2
            __m256i vc = _mm256_loadu_si256((__m256i*)(result +i +j )); // load 8 consecutive result values from result

            //Multiply and add to the vector rerult 
            __m256i  vmul= _mm256_mullo_epi32(va , vb); 
            vc = _mm256_add_epi32(vc , vmul);

            _mm256_storeu_si256((__m256i *)(result + i + j), vc); //store the updated result back to memory
        }

        // Handle remaining elements
        for (; j <= n; j++) {
            result[i + j] += a * P2[j];
        }
    }
}
