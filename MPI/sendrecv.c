#include <mpi.h>
#include <stdio.h>
int main(int argc, char **argv) {
    int rank, nproc, tag = 0;
    MPI_Status stat;
    int message_size = 128;
    char buffer[128];
    MPI_Init(&argc, &argv);
    MPI_Comm_rank(MPI_COMM_WORLD, &rank);
    MPI_Comm_size(MPI_COMM_WORLD, &nproc);
    if (nproc != 2) {
        if (rank == 0)
            fprintf(stderr, "sendrecv only runs with two processors\n");
        MPI_Abort(MPI_COMM_WORLD, 1);
    }
    if (rank == 0) {
        MPI_Send(buffer, message_size, MPI_CHAR, 1, tag, MPI_COMM_WORLD);
        MPI_Recv(buffer, message_size, MPI_CHAR, 1, tag, MPI_COMM_WORLD, &stat);
    } else if (rank == 1) {
        MPI_Recv(buffer, message_size, MPI_CHAR, 0, tag, MPI_COMM_WORLD, &stat);
        MPI_Send(buffer, message_size, MPI_CHAR, 0, tag, MPI_COMM_WORLD);
    }
    MPI_Finalize();
    return 0;
}
