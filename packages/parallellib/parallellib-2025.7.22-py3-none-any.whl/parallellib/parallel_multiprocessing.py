import multiprocessing
import os
from multiprocessing import Pool, TimeoutError, cpu_count
import numpy as np
from waveformtools.waveformtools import message
from warnings import warn

#
class MultiprocessingClassTemplate:
    """Evaluate the spin weighted spherical harmonics
    asynchronously on multiple processors at any precision
    required

    Attributes
    ----------
    ell_max : int
              The max :math:`\\ell` to use to evaluate the harmonic coefficients.
    Grid : Grid
                An object of the Grid class, that is used to setup
                the coordinate grid on which to evaluate the spherical
                harmonics.
    prec : int
           The precision to maintain in order to evaluate the spherical
           harmonics.
    nprocs : int
             The number of processors to use. Defaults to half the available.
    """

    def __init__(
        self,
        nprocs=None,
        *args,
        **kwargs
    ):

        self._nprocs = nprocs
        self.setup_env()
        self._job_list = None
        self._result_list = []

    @property
    def nprocs(self):
        return self._nprocs

    @property
    def job_list(self):
        return self._job_list

    @property
    def result_list(self):
        return self._result_list

    def setup_env(self):
        """Imports"""
        from multiprocessing import Pool, TimeoutError, cpu_count

    def get_max_nprocs(self):
        """Get the available number of processors on the system"""
        max_ncpus = cpu_count()
        return max_ncpus

    def create_job_list(self, *args, **kwargs):
        """Create a list of jobs (modes) for distributing
        computing to different processors"""

        job_list = []
        raise NotImplementedError
        self._job_list = job_list
 
    def log_results(self, result):
        """Save result to memory"""
        self._result_list.append(result)

    def initialize(self, *args, **kwargs):
        """Initialize the workers / pool"""

        if self.nprocs is None:
            max_ncpus = self.get_max_nprocs()
            self._nprocs = int(max_ncpus / 2)

        self.create_job_list(*args, **kwargs)
        self.pool = multiprocessing.Pool(processes=self.nprocs)

    def run(self, *args, **kwargs):
        """Compute the SHSHs, cache results, and create modes"""

        self.initialize(*args, **kwargs)
        multiple_results = self.pool.map(self.compute_main, self.job_list)
        self._result_list = multiple_results
        self.pool.close()
        self.pool.join()
        self.pool.close()

    def compute_main(self, task):
        """ The main compute function """
        
        raise NotImplementedError

    def test_mp(self, mode_number):
        """Print a simple test output message"""
        message(
            f"This is process {os.getpid()} processing mode {mode_number}\n",
            message_verbosity=1,
        )
        return 1

    def __getstate__(self):
        """Refresh Pool state"""
        self_dict = self.__dict__.copy()
        del self_dict["pool"]
        return self_dict

    def __setstate__(self, state):
        """Set Pool state"""
        self.__dict__.update(state)
