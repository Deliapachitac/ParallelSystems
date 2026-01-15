#include <stdio.h>
#include <stdlib.h>
#include <mpi.h>

void generate_polynomials(int n, int* P);
void multiply_serial(int n, const int* P1, const int* P2, int* result);

int main(int argc, char* argv[]) {
    
    // Activate the  MPI environment  
    MPI_Init(&argc, &argv);

    int my_rank, comm_size;
    MPI_Comm_rank(MPI_COMM_WORLD, &my_rank); //number of current process
    MPI_Comm_size(MPI_COMM_WORLD, &comm_size);// total number  of  processes

    // We check if the user provided the correct number of arguments and we save them in variables
    if (argc !=2 ) {
        if (my_rank == 0){
            fprintf(stderr, "Wrong number of arguments. Usage: %s <degree_of_polynomials>\n", argv[0]);
            
        }
        MPI_Finalize();
        return  -1;
    }
    
             
    //Convert degree argument to integer
    int n = atoi(argv[1]);
    
    // Variables for measuring time
    double start_total, end_total;
    double send_start,send_end;
    double comp_start,comp_end;
    double recv_start, recv_end;
    double serial_start, serial_end;

    
    // The two polynomials will be stored in arrays
    int *P1 = NULL, *P2 = NULL;

    // Local arrays for each process
    int *temp_P1, *local_result;

    // Master process generates the polynomials
    if (my_rank == 0) {
        P1 = malloc((n+1) * sizeof(int));
        P2 =malloc((n+1 ) *sizeof(int)) ;

        generate_polynomials(n, P1);
        generate_polynomials(n, P2);

        //////////////// SERIAL MULTIPLICATION ////////////////
        int *serial_res = malloc((2 * n + 1) * sizeof(int));
        serial_start = MPI_Wtime();
        multiply_serial(n, P1, P2, serial_res);
        serial_end = MPI_Wtime();
        printf("Serial multiplication time: %.6f seconds\n", serial_end - serial_start);
        free(serial_res);

    } else{
    //All the processes need P2 so we allocate memory for it and we broadcast it
        P2 = malloc((n+1)*sizeof(int));
    }  
    
    start_total = MPI_Wtime();//start total time    

    send_start = MPI_Wtime(); //start the sending time
    
    // Broadcast P2 to all processes
    MPI_Bcast(P2, n+1, MPI_INT,0, MPI_COMM_WORLD);

    //Now we need to distribute the P1 among all processes(scatterv)
    // beacause we dont know teh if the array can be evenly divided we use scatterv instead of scatter
    int *total_elements = NULL; // the total number of elements that the processes will  receive 
    int *start_indx = NULL; // the starting index in P1 where the process will start receiving data


    if (my_rank == 0) {
        total_elements = malloc(comm_size * sizeof(int));
        start_indx = malloc(comm_size * sizeof(int));

        int temp_minim =(n+1)/comm_size; // how many elements each process will receive at least
        int temp_extra = (n+1) % comm_size; //how many procecces will receive one extra element


        int offset = 0;
        for (int p = 0;p< comm_size;p++  ){   
            total_elements[p] = temp_minim +(p < temp_extra ? 1 : 0);
            start_indx[p] = offset;
            offset += total_elements[p];
        }
    }

    // Broadcast the total_elements so all ranks know their chunk size
    if (my_rank != 0){
        total_elements = malloc(comm_size * sizeof(int));
    }  
    MPI_Bcast(total_elements, comm_size, MPI_INT, 0, MPI_COMM_WORLD);

    //Allocate memory for the array that will contain the local part of P1
    temp_P1 = malloc(total_elements[my_rank]* sizeof(int));

    // Scatterv P1array to all processes
    MPI_Scatterv(P1, total_elements, start_indx, MPI_INT,
                 temp_P1,total_elements[my_rank], MPI_INT,
                 0,MPI_COMM_WORLD);
    
    send_end = MPI_Wtime(); //end the sending time
  
    // A temporary array to store local result of each proccess 
    //it needs to be of size 2*n+1 because in the worst case a process can contribute to all coefficients
    //also the array   must be filled with zeros 
    local_result = calloc(2*n+1, sizeof(int));

    //calculate the starting index in the result array for each process
    int start_i = 0;
    for (int i =0; i<my_rank; i++)
        start_i +=total_elements[ i ];

    // MULTIPLICATION (independent work for each process)
    comp_start = MPI_Wtime(); //start computation time
    for (int i =0; i< total_elements[ my_rank]; i++) {
        for (int j =0; j<=n; j++) {
            local_result[start_i +i+j] += temp_P1[i]*P2[j];
        }
    }
    comp_end = MPI_Wtime(); //end computation time
   
    // GATHERING RESULTS TO MASTER PROCESS
    if (my_rank == 0) {
        
        int *final_result = calloc(2*n+1, sizeof(int));

        recv_start = MPI_Wtime(); //start receiving time

        //First add the master's local result 
        for (int i = 0; i < 2*n+1; i++){
            final_result[i] += local_result[i];
        }

        MPI_Status status;
        for (int i = 1; i < comm_size; i++) {

            // Receive local result from each process
            int *temporary = malloc((2*n+1) * sizeof(int));
            MPI_Recv(temporary, 2*n+1, MPI_INT, i, 0, MPI_COMM_WORLD, &status);
            
            // Combine the received local result into the final result
            for (int j = 0; j < 2*n+1; j++){
                final_result[j] += temporary[j];
            }
            free(temporary);
        }

        recv_end = MPI_Wtime(); //end receiving time
        end_total = MPI_Wtime();//end total time
        printf("Total multiplication time: %.6f seconds\n",  end_total - start_total);
        printf("Sending data time: %.6f seconds\n", send_end - send_start);
        printf("Parallel computation time: %.6f seconds\n", comp_end - comp_start);
        printf("Receiving data time: %.6f seconds\n", recv_end - recv_start);

    
        // Free allocated memory
        free(P1);
        free(P2);
        free(final_result);
        free(start_indx);
    } else {
        //if we are not in the master process we just send our local result to the master
        MPI_Send(local_result, 2*n+1, MPI_INT, 0, 0, MPI_COMM_WORLD);
        free(P2);
    }

    // Free the allocated memory
    free(temp_P1);
    free(total_elements);
    free(local_result);

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