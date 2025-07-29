from mpi4py import MPI
from waveformtools.waveformtools import message, progressbar
from tqdm import tqdm


class ParallelClassTemplate:
    
    def __init__(self,
                ):

        # MPI
        self._mpi_rank = None
        self._mpi_nprocs = None
        
        # Setup engine
        # self.initialize_parallel_engine()
        self.reset_progressbar()
        
    @property
    def mpi_rank(self):
        return self._mpi_rank

    @property
    def mpi_nprocs(self):
        return self._mpi_nprocs

    @property
    def mpi_comm(self):
        return self._mpi_comm
    
    def message_root(self, *args, **kwargs):
        """A print statement for the MPI root"""

        if self.mpi_rank == 0:
            message(*args, **kwargs)
            
    def initialize_parallel_engine(self):
        """Initialize the parallel compute engine
        components for interpolation"""

        self._mpi_comm = MPI.COMM_WORLD

        self._mpi_nprocs = self.mpi_comm.Get_size()
        self._mpi_rank = self.mpi_comm.Get_rank()

        self.message_root(
            f"Engine using {self.mpi_nprocs} processors", message_verbosity=1
        )
        
    def sync(self):
        ''' Barrier '''
        self.mpi_comm.barrier()

    def reset_progressbar(self):
        ''' Reset counters '''
        self.local_counts = 0
        self.total_counts = 0
        self.njobs = None
    
    def set_progressbar(self):

        self.progress_bar = tqdm(total=self.njobs, desc="Computing")

    def progressbar(self):
        ''' A simple progressbar '''
        
        self.total_counts = self.mpi_comm.reduce(self.local_counts, root=0)

        if self.mpi_rank==0:
            #message(self.local_counts, self.total_counts, self.njobs)
            #progressbar(self.total_counts, self.njobs)
            self.progress_bar.update(self.total_counts-self.progress_bar.n)

        self.local_counts+=1
        
    def finalize(self):
        ''' Relieve the MPI workers '''
        MPI.Finalize()

