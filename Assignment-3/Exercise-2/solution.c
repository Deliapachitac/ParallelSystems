#include <stdio.h>
#include <errno.h>
#include <time.h>
#include <stdlib.h>
#include <sys/time.h>
#include <mpi.h>
#include "../Shared/my_rand.h"

/// @brief Perform sparse Matrix-Vector multiplication with matrix represented in CSR format
/// @param V Non-zero values of sparse matrix
/// @param colIdx The column index where the non-zero value is
/// @param rowIdx The number of non-null values before this row
/// @param vector The vector we are multiplying with
/// @param rowNum The number of rows/columns of the matrix
/// @return Vector with result
void matVecMultCSR(const int *restrict V, const int *restrict colIdx, const int *restrict rowIdx, const int *restrict vector, int *restrict retVec, int rowNum)
{
    int i, j;
    for (i = 0; i < rowNum; i++)
    {
        // Get row indices and loop over non-zero elements and place them in the correct index
        int rowStart = rowIdx[i];
        int rowEnd = rowIdx[i + 1];
        int res = 0;
        for (j = rowStart; j < rowEnd; j++)
        {
            res += V[j] * vector[colIdx[j]];
        }
        retVec[i] = res;
    }
}
/// @brief Multiply a matrix by a vector
/// @param denseMatrix the matrix
/// @param vector the vector being multiplied by denseMatrix
/// @param numRows the number of rows/columns of the matrix
/// @return The resulting vector after the multiplication
void Mat_vect_mult(const int *restrict denseMatrix, const int *restrict vector, int *restrict retVec, int numRows, int myRows)
{
    int i, j;
    for (i = 0; i < myRows; i++)
    {
        retVec[i] = 0;
        for (j = 0; j < numRows; j++)
            retVec[i] += denseMatrix[i * numRows + j] * vector[j];
    }
}

int *create_diagonal_matrix(int n)
{
    int *matrix = (int *)calloc(n * n, sizeof(int));
    if (matrix == NULL)
        return NULL;
    unsigned seed = time(NULL);
    for (int i = 0; i < n; i++)
    {
        matrix[i * n + i] = my_rand(&seed) % 10;
    }
    return matrix;
}

int *create_block_sparse_int(int n, int block_size, int num_blocks)
{
    int *matrix = (int *)calloc(n * n, sizeof(int));
    if (!matrix)
        return NULL;
    unsigned seed = time(NULL);
    for (int b = 0; b < num_blocks; b++)
    {
        // Randomly pick top-left corner aligned to block boundaries
        int row_start = (my_rand(&seed) % (n / block_size)) * block_size;
        int col_start = (my_rand(&seed) % (n / block_size)) * block_size;

        for (int i = 0; i < block_size; i++)
        {
            for (int j = 0; j < block_size; j++)
            {
                matrix[(row_start + i) * n + (col_start + j)] = my_rand(&seed) % 100 + 1;
            }
        }
    }
    return matrix;
}

int *create_power_law_int(int n, int hub_density)
{
    int *matrix = (int *)calloc(n * n, sizeof(int));
    if (!matrix)
        return NULL;

    unsigned seed = time(NULL);
    for (int i = 0; i < n; i++)
    {
        // Every 20th row is a "hub" with many entries
        int entries_to_fill = (i % 20 == 0) ? (n / hub_density) : (my_rand(&seed) % 5);

        for (int k = 0; k < entries_to_fill; k++)
        {
            int j = my_rand(&seed) % n;
            matrix[i * n + j] = my_rand(&seed) % 100 + 1;
        }
    }
    return matrix;
}

int *create_banded_int(int n, int bandwidth)
{
    int *matrix = (int *)calloc(n * n, sizeof(int));
    if (!matrix)
        return NULL;
    unsigned seed = time(NULL);
    for (int i = 0; i < n; i++)
    {
        int start = (i - bandwidth < 0) ? 0 : i - bandwidth;
        int end = (i + bandwidth >= n) ? n - 1 : i + bandwidth;

        for (int j = start; j <= end; j++)
        {
            matrix[i * n + j] = my_rand(&seed) % 100 + 1;
        }
    }
    return matrix;
}

int main(int argc, char *argv[])
{
    long numColumns;     // Number of columns/rows
    long zeroPercentage; // Percentage of zeroes in matrix
    long numLoops;       // Number of multiplications to be done
    long numNonZero = 0;
    long params[3];
    struct timeval start, end;
    double elapsed;
    int myRank;
    int commSz;
    MPI_Init(&argc, &argv);
    MPI_Comm_size(MPI_COMM_WORLD, &commSz);
    MPI_Comm_rank(MPI_COMM_WORLD, &myRank);
    // Process 0 will process the input arguments and broadcast them to the other processes, this is to ensure all processes have the same data
    if (myRank == 0)
    {

        if (argc != 4)
        {
            fprintf(stderr, "Correct Usage: ./CSR_Multiplication [Number of Columns/Rows] [Percentage of zeroes in matrix] [Number of loops in multiplication]\n");
            MPI_Abort(MPI_COMM_WORLD, 1);
        }
        errno = 0;
        params[0] = strtol(argv[1], NULL, 10);
        if (errno != 0)
        {
            fprintf(stderr, "First argument should be a 10-base number\n");
            MPI_Abort(MPI_COMM_WORLD, 1);
        }

        params[1] = strtol(argv[2], NULL, 10);
        if (errno != 0 || (params[1] < 0 || params[1] > 100))
        {
            fprintf(stderr, "Second argument argument should be a 10-base number between 0 and 100\n");
            MPI_Abort(MPI_COMM_WORLD, 1);
        }

        params[2] = strtol(argv[3], NULL, 10);
        if (errno != 0)
        {
            fprintf(stderr, "Third argument should be an integer\n");
            MPI_Abort(MPI_COMM_WORLD, 1);
        }
    }
    MPI_Bcast(&params, 3, MPI_LONG, 0, MPI_COMM_WORLD);
    numColumns = params[0];
    zeroPercentage = params[1];
    numLoops = params[2];
    int *vector;
    int *denseArray;
    int *denseVector;
    int *V;      // Values of non zero values
    int *colIdx; // Column index of non-zero value
    int *rowIdx; // Encodes the index in V and COL_INDEX where the given row starts
    int sendCounts[commSz];
    int displs[commSz];
    int denseSendCounts[commSz];
    int denseDispls[commSz];
    int dataSendCounts[commSz];
    int dataDispls[commSz];
    // We make 2 vectors with the same contents, this is done so we can check the validity of the result against the dense matrix multiplication, which is considered correct
    vector = malloc(numColumns * sizeof(int));

    if (vector == NULL)
    {
        fprintf(stderr, "Couldn't allocate memory for vector\n");
        MPI_Abort(MPI_COMM_WORLD, 1);
    }

    denseVector = malloc(numColumns * sizeof(int));

    if (denseVector == NULL)
    {
        fprintf(stderr, "Couldn't allocate memory for vector\n");
        MPI_Abort(MPI_COMM_WORLD, 1);
    }
    if (myRank == 0)
    {
        // Create denseArray, we will use this later
        denseArray = malloc(numColumns * numColumns * sizeof(int));

        if (denseArray == NULL)
        {
            fprintf(stderr, "Something went wrong, couldn't allocate memory\n");
            MPI_Abort(MPI_COMM_WORLD, 1);
        }

        unsigned seed = time(NULL);
        for (int i = 0; i < numColumns; i++)
        {
            unsigned randNum = my_rand(&seed);
            vector[i] = randNum;
            denseVector[i] = randNum;
            for (int j = 0; j < numColumns; j++)
            {
                int randNumber = my_rand(&seed) % 100;
                if (randNumber < zeroPercentage)
                {
                    denseArray[i * numColumns + j] = 0;
                }
                else
                {
                    denseArray[i * numColumns + j] = randNumber;
                    numNonZero++;
                }
            }
        }
    }
    MPI_Bcast(&numNonZero, 1, MPI_INT, 0, MPI_COMM_WORLD);

    if (myRank == 0)
    {
        V = malloc(numNonZero * sizeof(int));      // Values of non zero values
        colIdx = malloc(numNonZero * sizeof(int)); // Column index of non-zero value
        // Convert Dense array to CSR sparse array format, count time taken
        gettimeofday(&start, NULL);
        rowIdx = malloc((numColumns + 1) * sizeof(int)); // Encodes the index in V and COL_INDEX where the given row starts
        numNonZero = 0;
        rowIdx[0] = 0;
        for (int i = 0; i < numColumns; i++)
        {
            for (int j = 0; j < numColumns; j++)
            {
                int value = denseArray[i * numColumns + j];
                if (value != 0)
                {
                    V[numNonZero] = value;
                    colIdx[numNonZero] = j;
                    numNonZero++;
                }
            }
            rowIdx[i + 1] = numNonZero;
        }
        gettimeofday(&end, NULL);
        elapsed = (end.tv_sec - start.tv_sec) + (end.tv_usec - start.tv_usec) / 1e6;
        printf("Matrix-vector Initialization with CSR format took: %f seconds\n", elapsed);
        int totalDspls = 0;
        int sz = numColumns / commSz;
        int mod = numColumns % commSz;
        // Share extra work equally, and scatter rowIdx with overlapping
        // We do this so the processes have access to the end of their respective row
        for (int i = 0; i < commSz; i++)
        {
            int workForThisRank = sz + (i < mod ? 1 : 0);

            displs[i] = totalDspls;

            sendCounts[i] = workForThisRank + 1;

            denseSendCounts[i] = workForThisRank * numColumns;

            denseDispls[i] = totalDspls * numColumns;

            dataDispls[i] = rowIdx[totalDspls]; 
                
            dataSendCounts[i] = rowIdx[totalDspls + workForThisRank] - rowIdx[totalDspls];

            totalDspls += workForThisRank;

        }
    }
    if (myRank == 0) gettimeofday(&start, NULL);
        
    int myRows = (numColumns / commSz) + (myRank < (numColumns % commSz) ? 1 : 0);
    int myRecvCount = myRows + 1;
    int *localRowIdx = malloc(myRecvCount * sizeof(int));
    int *localDenseMatrix = malloc(myRows * numColumns * sizeof(int));
    MPI_Bcast(dataSendCounts, commSz, MPI_INT, 0, MPI_COMM_WORLD);
    int *localV = malloc(dataSendCounts[myRank] * sizeof(int));
    int *localColIdx = malloc(dataSendCounts[myRank] * sizeof(int));
    MPI_Bcast(vector, numColumns, MPI_INT, 0, MPI_COMM_WORLD);
    MPI_Scatterv(V, dataSendCounts, dataDispls, MPI_INT, localV, dataSendCounts[myRank], MPI_INT, 0,MPI_COMM_WORLD);
    MPI_Scatterv(colIdx, dataSendCounts, dataDispls, MPI_INT, localColIdx, dataSendCounts[myRank], MPI_INT, 0,MPI_COMM_WORLD);
    // We use scatterv so we can assign rowIdx with overlapping last element and to make sure work gets scattered correctly even with row sizes that are not divisible by commSz
    MPI_Scatterv(rowIdx, sendCounts, displs, MPI_INT, localRowIdx, myRecvCount, MPI_INT, 0, MPI_COMM_WORLD);
    // Shift localRowIdx
    int offset = localRowIdx[0];
    for (int i = 0; i < myRecvCount; i++) {
        localRowIdx[i] -= offset;
    }
    if (myRank == 0)
    {
        gettimeofday(&end, NULL);
        elapsed = (end.tv_sec - start.tv_sec) + (end.tv_usec - start.tv_usec) / 1e6;
        printf("Scattering the necessary data for CSR took: %f seconds\n", elapsed);
        free(V);
        free(colIdx);
        free(rowIdx);
        gettimeofday(&start, NULL);
    }
    MPI_Bcast(denseVector, numColumns, MPI_INT, 0, MPI_COMM_WORLD);
    MPI_Scatterv(denseArray, denseSendCounts, denseDispls, MPI_INT, localDenseMatrix, myRows * numColumns, MPI_INT, 0, MPI_COMM_WORLD);

    if (myRank == 0)
    {
        gettimeofday(&end, NULL);
        elapsed = (end.tv_sec - start.tv_sec) + (end.tv_usec - start.tv_usec) / 1e6;
        printf("Scattering the necessary data for dense Matrix took: %f seconds\n", elapsed);
        free(denseArray);
        gettimeofday(&start, NULL);
    }

    int *gatherCounts = malloc(commSz * sizeof(int));
    int *gatherDispls = malloc(commSz * sizeof(int));

    int total = 0;
    int sz = numColumns / commSz;
    int mod = numColumns % commSz;

    for (int i = 0; i < commSz; i++)
    {
        int work = sz + (i < mod ? 1 : 0);
        gatherCounts[i] = work;
        gatherDispls[i] = total;
        total += work;
    }
    int *localVec = malloc(myRows * sizeof(int));
    for (int i = 0; i < numLoops; i++)
    {
        matVecMultCSR(localV, localColIdx, localRowIdx, vector, localVec, myRows);
        // Use Allgather to avoid broadcasting vector again
        MPI_Allgatherv(localVec, myRows, MPI_INT, vector, gatherCounts, gatherDispls, MPI_INT, MPI_COMM_WORLD);
    }

    if (myRank == 0)
    {
        gettimeofday(&end, NULL);
        elapsed = (end.tv_sec - start.tv_sec) + (end.tv_usec - start.tv_usec) / 1e6;
        printf("Matrix-vector multiplication with CSR format took: %f seconds\n", elapsed);
    }

    free(localRowIdx);
    free(localV);
    free(localColIdx);

    if (myRank == 0)
        gettimeofday(&start, NULL);
    for (int i = 0; i < numLoops; i++)
    {
        Mat_vect_mult(localDenseMatrix, denseVector, localVec, numColumns, myRows);
        MPI_Allgatherv(localVec, myRows, MPI_INT, denseVector, gatherCounts, gatherDispls, MPI_INT, MPI_COMM_WORLD);
    }
    free(localVec);
    free(localDenseMatrix);
    if (myRank == 0)
    {
        gettimeofday(&end, NULL);
        elapsed = (end.tv_sec - start.tv_sec) + (end.tv_usec - start.tv_usec) / 1e6;
        printf("Matrix-vector multiplication with dense matrix took: %f seconds\n", elapsed);
    }
    if (myRank == 0)
    {
        for (int i = 0; i < numColumns; i++)
        {
            if (vector[i] != denseVector[i])
            {
                fprintf(stderr, "Results are incorrect!\n");
                printf("vector[%d] = %d != denseVector[%d] = %d \n", i, vector[i], i, denseVector[i]);
                MPI_Abort(MPI_COMM_WORLD, 1);
            }
        }
    }
    free(gatherCounts);
    free(gatherDispls);
    free(vector);
    free(denseVector);
    if (myRank == 0)
        printf("Results are correct!\n");
    MPI_Finalize();
    return 0;
}
