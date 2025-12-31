//TODO: Add option to perform this on special types of arrays

#ifdef _OPENMP
#include <omp.h>
#endif
#include <stdio.h>
#include <errno.h>
#include <time.h>
#include <stdlib.h>
#include <sys/time.h>
#include "../Shared/my_rand.h"

long numThreads;     // Number of threads to be created, global so functions can use it freely

/// @brief Perform sparse Matrix-Vector multiplication with matrix represented in CSR format
/// @param V Non-zero values of sparse matrix
/// @param colIdx The column index where the non-zero value is
/// @param rowIdx The number of non-null values before this row
/// @param vector The vector we are multiplying with
/// @param rowNum The number of rows/columns of the matrix
/// @return Vector with result
int *matVecMultCSR(const int *restrict V, const int *restrict colIdx, const int *restrict rowIdx, const int *restrict vector, int rowNum)
{
    int i,j;
    int *retVec = malloc(rowNum * sizeof(int));
    if (retVec == NULL)
    {
        fprintf(stderr, "Couldn't allocate memory for vector\n");
        return NULL;
    }
    // Only execute with OpenMP if there is compiler support, otherwise fall back to serial execution
    #ifdef _OPENMP
    #  pragma omp parallel for num_threads(numThreads)  \
      default(none) private(i, j)  shared(V,colIdx, rowIdx, retVec, vector, rowNum)
    #endif
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
    return retVec;
}
/// @brief Multiply a matrix by a vector
/// @param denseMatrix the matrix
/// @param vector the vector being multiplied by denseMatrix
/// @param numRows the number of rows/columns of the matrix
/// @return The resulting vector after the multiplication
int* Mat_vect_mult(int *denseMatrix, int *vector, int numRows)
{
    int i, j;
    int* retVec = malloc(numRows * sizeof(int));
    if (retVec == NULL)
    {
        fprintf(stderr, "Couldn't allocate memory for vector\n");
        return NULL;
    }
    #ifdef _OPENMP
    #  pragma omp parallel for num_threads(numThreads)  \
      default(none) private(i, j)  shared(denseMatrix, retVec, vector, numRows)
    #endif
    for (i = 0; i < numRows; i++)
    {
        retVec[i] = 0;
        for (j = 0; j < numRows; j++)
            retVec[i] += denseMatrix[i * numRows + j] * vector[j];
    }
    return retVec;
}

int main(int argc, char *argv[])
{
    long numColumns;     // Number of columns/rows
    long zeroPercentage; // Percentage of zeroes in matrix
    long numLoops;       // Number of multiplications to be done
    long numNonZero = 0;
    struct timeval start, end;
    double elapsed;
    if (argc != 5)
    {
        fprintf(stderr, "Correct Usage: ./CSR_Multiplication [Number of Columns/Rows] [Percentage of zeroes in matrix] [Number of loops in multiplication] [Number of threads]\n");
        return 1;
    }
    errno = 0;
    numColumns = strtol(argv[1], NULL, 10);
    if (errno != 0)
    {
        fprintf(stderr, "First argument should be a 10-base number\n");
        return 1;
    }

    zeroPercentage = strtol(argv[2], NULL, 10);
    if (errno != 0 || (zeroPercentage < 0 || zeroPercentage > 100))
    {
        fprintf(stderr, "Second argument argument should be a 10-base number between 0 and 100\n");
        return 1;
    }

    numLoops = strtol(argv[3], NULL, 10);
    if (errno != 0)
    {
        fprintf(stderr, "Third argument should be an integer\n");
        return 1;
    }

    numThreads = strtol(argv[4], NULL, 10);
    if (errno != 0)
    {
        fprintf(stderr, "Third argument should be an integer\n");
        return 1;
    }
    // Create denseArray, we will use this later
    int *denseArray = malloc(numColumns * numColumns * sizeof(int));

    if (denseArray == NULL)
    {
        fprintf(stderr, "Something went wrong, couldn't allocate memory\n");
        return 1;
    }

    int *vector = malloc(numColumns * sizeof(int));
    
    if (vector == NULL)
    {
        fprintf(stderr, "Couldn't allocate memory for vector\n");
        return 1;
    }
    // We make 2 vectors with the same contents, this is done so we can check the validity of the result against the dense matrix multiplication, which is considered correct
    int* denseVector = malloc(numColumns *sizeof(int));
    if (denseVector == NULL)
        {
            fprintf(stderr, "Couldn't allocate memory for vector\n");
            return 1;
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
    

    // Convert Dense array to CSR sparse array format, count time taken
    gettimeofday(&start, NULL);
    int *V = malloc(numNonZero * sizeof(int));            // Values of non zero values
    int *colIdx = malloc(numNonZero * sizeof(int));       // Column index of non-zero value
    int *rowIdx = malloc((numColumns + 1) * sizeof(int)); // Encodes the index in V and COL_INDEX where the given row starts
    numNonZero = 0;
    rowIdx[0] = 0;
    //Try to make this parallel
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
    gettimeofday(&start, NULL);
    for (int i = 0; i < numLoops; i++)
    {
        int *newVec = matVecMultCSR(V, colIdx, rowIdx, vector, numColumns);
        if(newVec == NULL){
            return 1;
        }
        free(vector);
        vector = newVec;
    }
    gettimeofday(&end, NULL);
    elapsed = (end.tv_sec - start.tv_sec) + (end.tv_usec - start.tv_usec) / 1e6;
    printf("Matrix-vector multiplication with CSR format took: %f seconds\n", elapsed);

    gettimeofday(&start, NULL);
    for(int i = 0; i < numLoops; i++){
        int *newVec = Mat_vect_mult(denseArray, denseVector, numColumns);
        if(newVec == NULL){
            return 1;
        }
        free(denseVector);
        denseVector = newVec;
    }
    gettimeofday(&end, NULL);
    elapsed = (end.tv_sec - start.tv_sec) + (end.tv_usec - start.tv_usec) / 1e6;
    printf("Matrix-vector multiplication with dense matrix took: %f seconds\n", elapsed);

    for(int i = 0; i < numColumns ; i++){
        if(vector[i] != denseVector[i]){
            fprintf(stderr, "Results are incorrect!\n");
            return 1;
        }
    }
    printf("Results are correct!\n");
}