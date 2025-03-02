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

#define MIN(a,b) ((a) < (b) ? (a) : (b))
#define MAX(a,b) ((a) > (b) ? (a) : (b))

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

int readInput2(char* filename, double* data)
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
    	return -2; 
	}
}

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
    	return -3; 
	}
}

void initCentroids(const double *data, double* centroids, int* centroidPos, int samples, int K)
{
	int i;
	int idx;
	for(i=0; i<K; i++)
	{
		idx = centroidPos[i];
		memcpy(&centroids[i*samples], &data[idx*samples], (samples*sizeof(double)));
	}
}

__device__ double d_euclideanDistance(double *point, double *center, int samples)
{
	double dist=0.0;
	for(int i=0; i<samples; i++) 
	{
		dist += (point[i]-center[i]) * (point[i]-center[i]);
	}
  sqrt(dist);
  return(dist);
}

void zeroFloatMatriz(double *matrix, int rows, int columns)
{
	int i,j;
	for (i=0; i<rows; i++)
		for (j=0; j<columns; j++)
			matrix[i*columns+j] = 0.0;	
}

void zeroIntArray(int *array, int size)
{
	int i;
	for (i=0; i<size; i++)
		array[i] = 0;	
}

__constant__ int d_samples;
__constant__ int d_K;
__constant__ int d_lines;

__global__ void assign_centroids(double* d_data, double* d_centroids, int* d_classMap, int* d_changes, int* d_pointsPerClass, double* d_auxCentroids){
	  int id = (blockIdx.x * blockDim.x) + threadIdx.x;

    if (id < d_lines) {
        int vclass = 1;
        double minDist = DBL_MAX;
        double dist = 0.0;
        for (int j = 0; j < d_K; j++) {
            double sum = 0.0;
            for (int i = 0; i < d_samples; ++i) {
              double diff = d_data[id * d_samples + i] - d_centroids[j * d_samples + i];
              sum += diff * diff;
            }
            dist = sqrt(sum);

            if (dist < minDist) {
                minDist = dist;
                vclass = j + 1;
            }
        }
        if (d_classMap[id] != vclass) {
            atomicAdd(d_changes, 1);
        }
        d_classMap[id] = vclass;

        atomicAdd(&d_pointsPerClass[vclass-1], 1);
        for(int j=0; j<d_samples; j++){
            atomicAdd(&d_auxCentroids[(vclass-1)*d_samples+j], d_data[id*d_samples+j]);
        }
    }
}

__global__ void max_step(double* d_auxCentroids, int* d_pointsPerClass, double* d_centroids, double* d_maxDist, double* d_distCentroids){
	  int id = (blockIdx.x * blockDim.x) + threadIdx.x;

    if (id < d_K){
        for(int j=0; j<d_samples; j++){
            d_auxCentroids[id*d_samples+j] /= d_pointsPerClass[id];
        }

        d_distCentroids[id]=d_euclideanDistance(&d_centroids[id*d_samples], &d_auxCentroids[id*d_samples], d_samples);
        if(d_distCentroids[id]>*d_maxDist){
            *d_maxDist = d_distCentroids[id];
        }
    }
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
	* */
	if(argc !=  7)
	{
		fprintf(stderr,"EXECUTION ERROR K-MEANS: Parameters are not correct.\n");
		fprintf(stderr,"./KMEANS [Input Filename] [Number of clusters] [Number of iterations] [Number of changes] [Threshold] [Output data file]\n");
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
	
	double *data = (double*)calloc(lines*samples, sizeof(double));
if (data == NULL)
{
	fprintf(stderr,"Memory allocation error.\n");
	exit(-4);
}
error = readInput2(argv[1], data);  // Assumendo che readInput2 sia modificata per leggere double
if(error != 0)
{
	showFileError(error, argv[1]);
	exit(error);
}

double maxThreshold = atof(argv[5]);

double *centroids = (double*)calloc(K*samples, sizeof(double));
double *auxCentroids = (double*)malloc(K*samples * sizeof(double));
double *distCentroids = (double*)malloc(K * sizeof(double));

if (centroidPos == NULL || centroids == NULL || classMap == NULL)
{
	fprintf(stderr,"Memory allocation error.\n");
	exit(-4);
}

// CUDA - dichiarazione delle variabili su device
double *d_data;
double *d_centroids;
double *d_auxCentroids;
double *d_distCentroids;

// Allocazione memoria su device
CHECK_CUDA_CALL(cudaMalloc(&d_data, lines*samples*sizeof(double)));
CHECK_CUDA_CALL(cudaMalloc(&d_centroids, K*samples*sizeof(double)));
CHECK_CUDA_CALL(cudaMalloc(&d_auxCentroids, K*samples*sizeof(double)));
CHECK_CUDA_CALL(cudaMalloc(&d_distCentroids, K*sizeof(double)));

// Copia dei dati iniziali
CHECK_CUDA_CALL(cudaMemcpy(d_data, data, lines*samples*sizeof(double), cudaMemcpyHostToDevice));
CHECK_CUDA_CALL(cudaMemcpy(d_classMap, classMap, lines*sizeof(int), cudaMemcpyHostToDevice));
CHECK_CUDA_CALL(cudaMemcpy(d_centroids, centroids, K*samples*sizeof(double), cudaMemcpyHostToDevice));
CHECK_CUDA_CALL(cudaMemcpy(d_pointsPerClass, pointsPerClass, K*sizeof(int), cudaMemcpyHostToDevice));
CHECK_CUDA_CALL(cudaMemcpy(d_auxCentroids, auxCentroids, K*samples*sizeof(double), cudaMemcpyHostToDevice));
CHECK_CUDA_CALL(cudaMemcpy(d_distCentroids, distCentroids, K*sizeof(double), cudaMemcpyHostToDevice));
    // Set of the grid and block dimensions
    dim3 blockSize(1024);
	  dim3 numBlocks(ceil(static_cast<float>(lines) / blockSize.x));
    dim3 numBlocks2(ceil(static_cast<float>(K) / blockSize.x));

	do{
		it++;
	
		//1. Calculate the distance from each point to the centroid
		//Assign each point to the nearest centroid.
    CHECK_CUDA_CALL( cudaMemset(d_changes, 0, sizeof(int)) );
    CHECK_CUDA_CALL( cudaMemset(d_maxDist, DBL_MIN, sizeof(double)) );
		CHECK_CUDA_CALL( cudaMemset(d_pointsPerClass, 0, K*sizeof(int)) );
    CHECK_CUDA_CALL( cudaMemset(d_auxCentroids, 0, K*samples*sizeof(double)) );

		// Syncronize the device
		CHECK_CUDA_CALL( cudaDeviceSynchronize() );

        assign_centroids<<<numBlocks, blockSize>>>(d_data, d_centroids, d_classMap, d_changes, d_pointsPerClass, d_auxCentroids);
        CHECK_CUDA_LAST();

        // Syncronize the device
        CHECK_CUDA_CALL( cudaDeviceSynchronize() );

		    max_step<<<numBlocks2, blockSize>>>(d_auxCentroids, d_pointsPerClass, d_centroids, d_maxDist, d_distCentroids);
        CHECK_CUDA_LAST();
    
    // Syncronize the device
    CHECK_CUDA_CALL( cudaDeviceSynchronize() );

    CHECK_CUDA_CALL( cudaMemcpy(&changes, d_changes, sizeof(int), cudaMemcpyDeviceToHost) )
    CHECK_CUDA_CALL( cudaMemcpy(&maxDist, d_maxDist, sizeof(double), cudaMemcpyDeviceToHost) )
    CHECK_CUDA_CALL( cudaMemcpy(d_centroids, d_auxCentroids, K*samples*sizeof(double), cudaMemcpyHostToDevice) );
		
		sprintf(line,"\n[%d] Cluster changes: %d\tMax. centroid distance: %f", it, changes, maxDist);
		outputMsg = strcat(outputMsg,line);

	} while((changes>minChanges) && (it<maxIterations) && (maxDist>maxThreshold));

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

	//END CLOCK*****************************************
	end = omp_get_wtime();
	printf("\n\nMemory deallocation: %f seconds\n", end - start);
	fflush(stdout);
	//***************************************************/
	return 0;
}
