#include <stdio.h>
#include <stdlib.h>
#include <mpi.h>
#include <time.h>

void generate_polynomials(int n, int* P);
void multiply_serial(int n, const int* P1, const int* P2, int* result);

int main(int argc, char* argv[]) {

    MPI_Init(&argc, &argv);

    int rank, size;
    MPI_Comm_rank(MPI_COMM_WORLD, &rank);
    MPI_Comm_size(MPI_COMM_WORLD, &size);

    if (argc != 2) {
        if (rank == 0)
            fprintf(stderr, "Usage: %s <degree_of_polynomials>\n", argv[0]);
        MPI_Finalize();
        return -1;
    }

    int n = atoi(argv[1]);  

    double t_total_start, t_total_end;
    double t_send_start, t_send_end;
    double t_compute_start, t_compute_end;
    double t_recv_start, t_recv_end;

    t_total_start = MPI_Wtime();

    int *P1 = NULL, *P2 = NULL;

    if (rank == 0) {
        P1 = malloc((n+1) * sizeof(int));
        P2 = malloc((n+1) * sizeof(int));

        generate_polynomials(n, P1);
        generate_polynomials(n, P2);
    }

    if (rank == 0) t_send_start = MPI_Wtime();

    if (rank != 0) P2 = malloc((n+1) * sizeof(int));
    MPI_Bcast(P2, n+1, MPI_INT, 0, MPI_COMM_WORLD);

    int base = (n+1) / size;
    int rem = (n+1) % size;

    int local_n = base + (rank < rem ? 1 : 0);

    int *sendcounts = malloc(size * sizeof(int));
    int *displs = malloc(size * sizeof(int));

    int offset = 0;
    for (int i = 0; i < size; i++) {
        sendcounts[i] = base + (i < rem ? 1 : 0);
        displs[i] = offset;
        offset += sendcounts[i];
    }

    int *localP1 = malloc(local_n * sizeof(int));
    MPI_Scatterv(P1, sendcounts, displs, MPI_INT,
                 localP1, local_n, MPI_INT,
                 0, MPI_COMM_WORLD);

    if (rank == 0) t_send_end = MPI_Wtime();

    t_compute_start = MPI_Wtime();

    int *localC = calloc(2*n+1, sizeof(int));
    int start_i = displs[rank];

    for (int i = 0; i < local_n; i++) {
        for (int j = 0; j <= n; j++) {
            localC[start_i + i + j] += localP1[i] * P2[j];
        }
    }

    t_compute_end = MPI_Wtime();

    int *result_parallel = NULL;
    if (rank == 0) {
        result_parallel = calloc(2*n+1, sizeof(int));
        t_recv_start = MPI_Wtime();
    }

    MPI_Reduce(localC, result_parallel, 2*n+1, MPI_INT, MPI_SUM, 0, MPI_COMM_WORLD);

    if (rank == 0) {
        t_recv_end = MPI_Wtime();
        t_total_end = MPI_Wtime();

        printf("Time sending data: %f\n", t_send_end - t_send_start);
        printf("Time computing: %f\n", t_compute_end - t_compute_start);
        printf("Time receiving results: %f\n", t_recv_end - t_recv_start);
        printf("Total time: %f\n", t_total_end - t_total_start);

        
        /////////////// SERIAL MULTIPLICATION ///////////////
        int *result_serial = malloc((2*n+1) * sizeof(int));
        multiply_serial(n, P1, P2, result_serial);

        ////////////// VERIFY CORRECTNESS ///////////////
        int flag = 1;
        for (int i = 0; i <= 2*n; i++) {
            if (result_serial[i] != result_parallel[i]) {
                flag     = 0;
                break;
            }
        }
        printf("Parallel multiplication correctness: %s\n", flag ? "OK" : "Mismatch");


        free(result_serial);
        free(P1);
        free(P2);
        free(result_parallel);
    }

    // Free the allocated memory
    free(localP1);
    free(localC);
    free(sendcounts);
    free(displs);

    MPI_Finalize();
    return 0;
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