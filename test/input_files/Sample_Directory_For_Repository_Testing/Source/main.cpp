#include <iostream>
#include <fstream>
#include <mpi.h>

using namespace std;

int main(int argc, char *argv[]) 
{

    MPI_Init(&argc, &argv);
    
    int numprocs, rank, namelen;
    char processor_name[MPI_MAX_PROCESSOR_NAME];
    
    MPI_Comm_size(MPI_COMM_WORLD, &numprocs);
    MPI_Comm_rank(MPI_COMM_WORLD, &rank);
    MPI_Get_processor_name(processor_name, &namelen);
    
    printf("Process %d on %s out of %d\n", rank, processor_name, numprocs);
    
    
    // Create an array to broadcast.
    int array_size=numprocs;
    int * iarray = new int [array_size];
    if (rank == 0)
    {
        for (int ip=0; ip <array_size; ip++)
        {
            iarray[ip] = ip;
        }
    }
    else
    {
        for (int ip=0; ip <array_size; ip++)
        {
            iarray[ip] = -1;
        }

    }

    // Time a single broadcast.
    double start_time;
    double end_time;
    double elapsed_bcast_time;

    MPI_Barrier(MPI_COMM_WORLD);

    //Start the timer.
    start_time = MPI_Wtime();    

    // Broadcast the array.
    MPI_Bcast(iarray,numprocs,MPI_INT,0,MPI_COMM_WORLD);

    //Stop the timer.
    end_time = MPI_Wtime();    

    elapsed_bcast_time = end_time - start_time;

    delete [] iarray; 
   
    if (rank==0)
    {
        ofstream data_file;
        data_file.open("bcast_time");
        data_file << elapsed_bcast_time << endl;
        data_file.close();
    } 

    MPI_Finalize();
    
    printf("Success\n");
    
    return 0; 

}
