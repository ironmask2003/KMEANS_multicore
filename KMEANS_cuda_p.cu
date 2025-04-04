/*
 * k-Means clustering algorithm
 *
 * CUDA version
 *
 * Parallel computing (Degree in Computer Engineering)
 * 2022/2023
 *
 * Version: 1.0
 *
 * (c) 2022 Diego García-Álvarez, Arturo Gonzalez-Escribano
 * Grupo Trasgo, Universidad de Valladolid (Spain)
 *
 * This work is licensed under a Creative Commons Attribution-ShareAlike 4.0 International License.
 * https://creativecommons.org/licenses/by-sa/4.0/
 */
#include <stdio.h>
#include <stdlib.h>
#include <ctype.h>
#include <math.h>
#include <time.h>
#include <string.h>
#include <float.h>
#include <omp.h>
#include <cuda.h>


#define MAXLINE 2000
#define MAXCAD 200

//Macros
#define MIN(a,b) ((a) < (b) ? (a) : (b))
#define MAX(a,b) ((a) > (b) ? (a) : (b))

/*
 * Macros to show errors when calling a CUDA library function,
 * or after launching a kernel
 */
#define CHECK_CUDA_CALL( a )	{ \
	cudaError_t ok = a; \
	if ( ok != cudaSuccess ) \
		fprintf(stderr, "-- Error CUDA call in line %d: %s\n", __LINE__, cudaGetErrorString( ok ) ); \
	}
#define CHECK_CUDA_LAST()	{ \
	cudaError_t ok = cudaGetLastError(); \
	if ( ok != cudaSuccess ) \
		fprintf(stderr, "-- Error CUDA last in line %d: %s\n", __LINE__, cudaGetErrorString( ok ) ); \
	}

/* 
Function showFileError: It displays the corresponding error during file reading.
*/
void showFileError(int error, char* filename)
{
	printf("Error\n");
	switch (error)
	{
		case -1:
			fprintf(stderr,"\tFile %s has too many columns.\n", filename);
			fprintf(stderr,"\tThe maximum number of columns has been exceeded. MAXLINE: %d.\n", MAXLINE);
			break;
		case -2:
			fprintf(stderr,"Error reading file: %s.\n", filename);
			break;
		case -3:
			fprintf(stderr,"Error writing file: %s.\n", filename);
			break;
	}
	fflush(stderr);	
}

/* 
Function readInput: It reads the file to determine the number of rows and columns.
*/
int readInput(char* filename, int *lines, int *samples)
{
    FILE *fp;
    char line[MAXLINE] = "";
    char *ptr;
    const char *delim = "\t";
    int contlines, contsamples = 0;
    
    contlines = 0;

    if ((fp=fopen(filename,"r"))!=NULL)
    {
        while(fgets(line, MAXLINE, fp)!= NULL) 
		{
			if (strchr(line, '\n') == NULL)
			{
				return -1;
			}
            contlines++;       
            ptr = strtok(line, delim);
            contsamples = 0;
            while(ptr != NULL)
            {
            	contsamples++;
				ptr = strtok(NULL, delim);
	    	}	    
        }
        fclose(fp);
        *lines = contlines;
        *samples = contsamples;  
        return 0;
    }
    else
	{
    	return -2;
	}
}

/* 
Function readInput2: It loads data from file.
*/
int readInput2(char* filename, float* data)
{
    FILE *fp;
    char line[MAXLINE] = "";
    char *ptr;
    const char *delim = "\t";
    int i = 0;
    
    if ((fp=fopen(filename,"rt"))!=NULL)
    {
        while(fgets(line, MAXLINE, fp)!= NULL)
        {         
            ptr = strtok(line, delim);
            while(ptr != NULL)
            {
            	data[i] = atof(ptr);
            	i++;
				ptr = strtok(NULL, delim);
	   		}
	    }
        fclose(fp);
        return 0;
    }
    else
	{
    	return -2; //No file found
	}
}

/* 
Function writeResult: It writes in the output file the cluster of each sample (point).
*/
int writeResult(int *classMap, int lines, const char* filename)
{	
    FILE *fp;
    
    if ((fp=fopen(filename,"wt"))!=NULL)
    {
        for(int i=0; i<lines; i++)
        {
        	fprintf(fp,"%d\n",classMap[i]);
        }
        fclose(fp);  
   
        return 0;
    }
    else
	{
    	return -3; //No file found
	}
}

/*

Function initCentroids: This function copies the values of the initial centroids, using their 
position in the input data structure as a reference map.
*/
void initCentroids(const float *data, float* centroids, int* centroidPos, int samples, int K)
{
	int i;
	int idx;
	for(i=0; i<K; i++)
	{
		idx = centroidPos[i];
		memcpy(&centroids[i*samples], &data[idx*samples], (samples*sizeof(float)));
	}
}

/*
Function euclideanDistance: Euclidean distance
This function could be modified
*/
__device__ float d_euclideanDistance(float *point, float *center, int samples)
{
	float dist=0.0;
	for(int i=0; i<samples; i++) 
	{
		dist = fmaf((point[i]-center[i]), (point[i]-center[i]), dist);
	}
  dist = sqrt(dist);
  return(dist);
}

/*
Function zeroFloatMatriz: Set matrix elements to 0
This function could be modified
*/
void zeroFloatMatriz(float *matrix, int rows, int columns)
{
	int i,j;
	for (i=0; i<rows; i++)
		for (j=0; j<columns; j++)
			matrix[i*columns+j] = 0.0;	
}

/*
Function zeroIntArray: Set array elements to 0
This function could be modified
*/
void zeroIntArray(int *array, int size)
{
	int i;
	for (i=0; i<size; i++)
		array[i] = 0;	
}

// Costants used in the kernel
__constant__ int d_samples;
__constant__ int d_K;
__constant__ int d_lines;

// Kernle used to assign to each point the nearest cluster
__global__ void assign_centroids(float* d_data, float* d_centroids, int* d_classMap, int* d_changes, int* d_pointsPerClass, float* d_auxCentroids){
	  
    // Thread ID
    int id = (blockIdx.x * blockDim.x) + threadIdx.x;

    // Check if the thread is in the range of the data and assign the point to the nearest centroid
    if (id < d_lines) {
        int vclass = 1;
        float minDist = FLT_MAX;
        float dist = 0.0;

        // Assign the point to the nearest cluster
        for (int j = 0; j < d_K; j++) {
            dist = d_euclideanDistance(&d_data[id*d_samples], &d_centroids[j*d_samples], d_samples);
            if (dist < minDist) {
                minDist = dist;
                vclass = j + 1;
            }
        }

        // Check if the point changes its cluster and increment the number of changes
        if (d_classMap[id] != vclass) {
            atomicAdd(d_changes, 1);
        }

        // Assign the point to the new cluster
        d_classMap[id] = vclass;

        // Increment the number of points in the cluster and calculate the new centroid
        atomicAdd(&d_pointsPerClass[vclass-1], 1);
        for(int j=0; j<d_samples; j++){
            atomicAdd(&d_auxCentroids[(vclass-1)*d_samples+j], d_data[id*d_samples+j]);
        }
    }
}

__global__ void prova(float* d_auxCentroids, int* d_pointsPerClass, int* id_K){

  // ID of the thread
  int id = (blockIdx.x * blockDim.x) + threadIdx.x;
  int id_K_val = *id_K;

  if (id < d_samples) {
    d_auxCentroids[id_K_val * d_samples + id] /= d_pointsPerClass[id_K_val];
  }
}

// Kernel functino used to calculate the maximum distance between the older centroids and the new ones
__global__ void max_step(float* d_auxCentroids, int* d_pointsPerClass, float* d_centroids, float* d_maxDist, float* d_distCentroids){
	  
    // ID of the thread
    int id = (blockIdx.x * blockDim.x) + threadIdx.x;

    // Check if the thread is in the range data and calculate the maxDist bewteen the older centroids with the new one
    if (id < d_K){

        // Configure thread/block setup for child kernel
        int threadsPerBlock = 128;
        int blocksPerGrid = (d_samples + threadsPerBlock - 1) / threadsPerBlock;

        // Launch child kernel
        prova<<<blocksPerGrid, threadsPerBlock>>>(d_auxCentroids, d_pointsPerClass, &id);

        // Calculate the distance between the older centroid and the new one
        d_distCentroids[id]=d_euclideanDistance(&d_centroids[id*d_samples], &d_auxCentroids[id*d_samples], d_samples);
        if(d_distCentroids[id]>*d_maxDist){
            *d_maxDist = d_distCentroids[id];
        }
    }
}

// Function used to write the computation time to a file
void writeCompTimeToFile(char *filename, float value) {
  // Write value in the last line of the file
  FILE *fp = fopen(filename, "a");
  if (fp == NULL) {
    fprintf(stderr, "Error opening file %s\n", filename);
    return;
  }
  fprintf(fp, "%f\n", value);
  fclose(fp);
}

int main(int argc, char* argv[])
{

	//START CLOCK***************************************
	double start, end;
	start = omp_get_wtime();
	//**************************************************
	/*
	* PARAMETERS
	*
	* argv[1]: Input data file
	* argv[2]: Number of clusters
	* argv[3]: Maximum number of iterations of the method. Algorithm termination condition.
	* argv[4]: Minimum percentage of class changes. Algorithm termination condition.
	*          If between one iteration and the next, the percentage of class changes is less than
	*          this percentage, the algorithm stops.
	* argv[5]: Precision in the centroid distance after the update.
	*          It is an algorithm termination condition. If between one iteration of the algorithm 
	*          and the next, the maximum distance between centroids is less than this precision, the
	*          algorithm stops.
	* argv[6]: Output file. Class assigned to each point of the input file.
  * argv[7]: File where save the computation time
	* */
	if(argc !=  8)
	{
		fprintf(stderr,"EXECUTION ERROR K-MEANS: Parameters are not correct.\n");
		fprintf(stderr,"./KMEANS [Input Filename] [Number of clusters] [Number of iterations] [Number of changes] [Threshold] [Output data file] [Computation time file] \n");
		fflush(stderr);
		exit(-1);
	}

	// Reading the input data
	// lines = number of points; samples = number of dimensions per point
	int lines = 0, samples= 0;  
	
	int error = readInput(argv[1], &lines, &samples);
	if(error != 0)
	{
		showFileError(error,argv[1]);
		exit(error);
	}
	
	float *data = (float*)calloc(lines*samples,sizeof(float));
	if (data == NULL)
	{
		fprintf(stderr,"Memory allocation error.\n");
		exit(-4);
	}
	error = readInput2(argv[1], data);
	if(error != 0)
	{
		showFileError(error,argv[1]);
		exit(error);
	}

	// Parameters
	int K=atoi(argv[2]); 
	int maxIterations=atoi(argv[3]);
	int minChanges= (int)(lines*atof(argv[4])/100.0);
	float maxThreshold=atof(argv[5]);

	int *centroidPos = (int*)calloc(K,sizeof(int));
	float *centroids = (float*)calloc(K*samples,sizeof(float));
	int *classMap = (int*)calloc(lines,sizeof(int));

    if (centroidPos == NULL || centroids == NULL || classMap == NULL)
	{
		fprintf(stderr,"Memory allocation error.\n");
		exit(-4);
	}

	// Initial centrodis
	srand(0);
	int i;
	for(i=0; i<K; i++) 
		centroidPos[i]=rand()%lines;
	
	// Loading the array of initial centroids with the data from the array data
	// The centroids are points stored in the data array.
	initCentroids(data, centroids, centroidPos, samples, K);


  //pointPerClass: number of points classified in each class
	//auxCentroids: mean of the points in each class
	int *pointsPerClass = (int *)malloc(K*sizeof(int));
	float *auxCentroids = (float*)malloc(K*samples*sizeof(float));
	float *distCentroids = (float*)malloc(K*sizeof(float)); 
	if (pointsPerClass == NULL || auxCentroids == NULL || distCentroids == NULL)
	{
		fprintf(stderr,"Memory allocation error.\n");
		exit(-4);
	}


	printf("\n\tData file: %s \n\tPoints: %d\n\tDimensions: %d\n", argv[1], lines, samples);
	printf("\tNumber of clusters: %d\n", K);
	printf("\tMaximum number of iterations: %d\n", maxIterations);
	printf("\tMinimum number of changes: %d [%g%% of %d points]\n", minChanges, atof(argv[4]), lines);
	printf("\tMaximum centroid precision: %f\n", maxThreshold);

  //**************************************************
  // CUDA memory allocation***************************
  
  // Copy costant on device
    CHECK_CUDA_CALL( cudaMemcpyToSymbol(d_samples, &samples, sizeof(int)) );
    CHECK_CUDA_CALL( cudaMemcpyToSymbol(d_K, &K, sizeof(int)) );
    CHECK_CUDA_CALL( cudaMemcpyToSymbol(d_lines, &lines, sizeof(int)) );

  // Creation of the variables used on the device
  float *d_data, *d_centroids, *d_maxDist, *d_distCentroids, *d_auxCentroids;
  int *d_classMap, *d_pointsPerClass, *d_changes;

  // Memory allocation on the device
    CHECK_CUDA_CALL( cudaMalloc(&d_data, lines*samples*sizeof(float)) );
    CHECK_CUDA_CALL( cudaMalloc(&d_classMap, lines*sizeof(int)) );
    CHECK_CUDA_CALL( cudaMalloc(&d_centroids, K*samples*sizeof(float)) );
    CHECK_CUDA_CALL( cudaMalloc(&d_pointsPerClass, K*sizeof(int)) );
    CHECK_CUDA_CALL( cudaMalloc(&d_auxCentroids, K*samples*sizeof(float)) );
    CHECK_CUDA_CALL( cudaMalloc(&d_maxDist, sizeof(float)) );
    CHECK_CUDA_CALL( cudaMalloc(&d_changes, sizeof(int)) );
    CHECK_CUDA_CALL( cudaMalloc(&d_distCentroids, K*sizeof(float)) );

  // Copy data to the device
    CHECK_CUDA_CALL( cudaMemcpy(d_data, data, lines*samples*sizeof(float), cudaMemcpyHostToDevice) );
    CHECK_CUDA_CALL( cudaMemcpy(d_classMap, classMap, lines*sizeof(int), cudaMemcpyHostToDevice) );
    CHECK_CUDA_CALL( cudaMemcpy(d_centroids, centroids, K*samples*sizeof(float), cudaMemcpyHostToDevice) );
    CHECK_CUDA_CALL( cudaMemcpy(d_pointsPerClass, pointsPerClass, K*sizeof(int), cudaMemcpyHostToDevice) );
    CHECK_CUDA_CALL( cudaMemcpy(d_auxCentroids, auxCentroids, K*samples*sizeof(float), cudaMemcpyHostToDevice) );
    CHECK_CUDA_CALL( cudaMemcpy(d_distCentroids, distCentroids, K*sizeof(float), cudaMemcpyHostToDevice) );

  // END memory allocation***************************
	
	//END CLOCK*****************************************
	end = omp_get_wtime();
	printf("\nMemory allocation: %f seconds\n", end - start);
	fflush(stdout);

    CHECK_CUDA_CALL( cudaSetDevice(0) );
    CHECK_CUDA_CALL( cudaDeviceSynchronize() );
	//**************************************************
	//START CLOCK***************************************
	start = omp_get_wtime();
	//**************************************************
	char *outputMsg = (char *)calloc(10000,sizeof(char));
	char line[100];

	int it=0;
	int changes = 0;
	float maxDist;

/*
 *
 * START HERE: DO NOT CHANGE THE CODE ABOVE THIS POINT
 *
 */

  // Set of the grid and block dimensions
  dim3 blockSize(1024);
  dim3 numBlocks(ceil(static_cast<double>(lines) / blockSize.x));
  dim3 numBlocks2(ceil(static_cast<double>(K) / blockSize.x));

	do {

    // Increment the iteration counter
		it++;

    /* Reset of the variables to store the number of changes,
    * the maximum distance between centroids and the number of points per cluster
    */
      CHECK_CUDA_CALL(cudaMemset(d_changes, 0, sizeof(int)));
      CHECK_CUDA_CALL(cudaMemset(d_maxDist, FLT_MIN, sizeof(float)));
      CHECK_CUDA_CALL(cudaMemset(d_pointsPerClass, 0, K * sizeof(int)));
      CHECK_CUDA_CALL(cudaMemset(d_auxCentroids, 0, K * samples * sizeof(float)));

		// Synchronize the device
      CHECK_CUDA_CALL(cudaDeviceSynchronize());

    // First kernel used to assign to each point the nearest centroid
      assign_centroids<<<numBlocks, blockSize>>>(d_data, d_centroids, d_classMap, d_changes, d_pointsPerClass, d_auxCentroids);
      CHECK_CUDA_LAST();

    // Second kernel used to calculate the maximum distance between the older centroids and the new ones
      max_step<<<numBlocks2, blockSize>>>(d_auxCentroids, d_pointsPerClass, d_centroids, d_maxDist, d_distCentroids);
      CHECK_CUDA_LAST();

		// Synchronize the device
      CHECK_CUDA_CALL(cudaDeviceSynchronize());

    // Copy the number of changes and the maximum distance between the older centroids and the new ones in the local variables
      CHECK_CUDA_CALL(cudaMemcpy(&changes, d_changes, sizeof(int), cudaMemcpyDeviceToHost));
      CHECK_CUDA_CALL(cudaMemcpy(&maxDist, d_maxDist, sizeof(float), cudaMemcpyDeviceToHost));

    // Copy the new centroids in the centroids variable
      CHECK_CUDA_CALL(cudaMemcpy(d_centroids, d_auxCentroids, K * samples * sizeof(float), cudaMemcpyHostToDevice));

		sprintf(line, "\n[%d] Cluster changes: %d\tMax. centroid distance: %f", it, changes, maxDist);
		outputMsg = strcat(outputMsg, line);

	} while ((changes > minChanges) && (it < maxIterations) && (maxDist > maxThreshold));

  // Copy d_classMap in classMap
    CHECK_CUDA_CALL( cudaMemcpy(classMap, d_classMap, lines*sizeof(int), cudaMemcpyDeviceToHost) );

/*
 *
 * STOP HERE: DO NOT CHANGE THE CODE BELOW THIS POINT
 *
 */
	// Output and termination conditions
	printf("%s",outputMsg);	

    CHECK_CUDA_CALL( cudaDeviceSynchronize() );

	//END CLOCK*****************************************
	end = omp_get_wtime();
	printf("\nComputation: %f seconds", end - start);
  writeCompTimeToFile(argv[7], end - start);
  fflush(stdout);
	//**************************************************
	//START CLOCK***************************************
	start = omp_get_wtime();
	//**************************************************

	if (changes <= minChanges) {
		printf("\n\nTermination condition:\nMinimum number of changes reached: %d [%d]", changes, minChanges);
	}
	else if (it >= maxIterations) {
		printf("\n\nTermination condition:\nMaximum number of iterations reached: %d [%d]", it, maxIterations);
	}
	else {
		printf("\n\nTermination condition:\nCentroid update precision reached: %g [%g]", maxDist, maxThreshold);
	}	

	// Writing the classification of each point to the output file.
	error = writeResult(classMap, lines, argv[6]);
	if(error != 0)
	{
		showFileError(error, argv[6]);
		exit(error);
	}

	//Free memory
	free(data);
	free(classMap);
	free(centroidPos);
	free(centroids);
	free(distCentroids);
	free(pointsPerClass);
	free(auxCentroids);

  // Free cuda memory
    CHECK_CUDA_CALL( cudaFree(d_data) );
    CHECK_CUDA_CALL( cudaFree(d_classMap) );
    CHECK_CUDA_CALL( cudaFree(d_centroids) );
    CHECK_CUDA_CALL( cudaFree(d_pointsPerClass) );
    CHECK_CUDA_CALL( cudaFree(d_auxCentroids) );
    CHECK_CUDA_CALL( cudaFree(d_maxDist) );
    CHECK_CUDA_CALL( cudaFree(d_changes) );
    CHECK_CUDA_CALL( cudaFree(d_distCentroids) );

	//END CLOCK*****************************************
	end = omp_get_wtime();
	printf("\n\nMemory deallocation: %f seconds\n", end - start);
	fflush(stdout);
	//***************************************************/
	return 0;
}
