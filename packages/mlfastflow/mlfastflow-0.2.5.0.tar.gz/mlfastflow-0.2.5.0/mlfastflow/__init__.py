"""MLFastFlow - packages for fast dataflow and workflow processing."""

__version__ = "0.2.5.0"

# Import core components
from mlfastflow.core import Flow

# Import sourcing functionality
import mlfastflow.sourcing as sourcing
from mlfastflow.sourcing import Sourcing

# Import fastKNN functionality  
import mlfastflow.fastKNN as fastKNN
from mlfastflow.fastKNN import fastKNN
 
# Import BigQueryClient
import mlfastflow.bigqueryclient as bigqueryclient
from mlfastflow.bigqueryclient import BigQueryClient
import mlfastflow.bigqueryclientpolars as bigqueryclientpolars
from mlfastflow.bigqueryclientpolars import BigQueryClientPolars

# Import utils module (functions accessible via utils.function_name)
import mlfastflow.utils as utils

# Import utility functions directly
from mlfastflow.utils import timer_decorator, concat_files, profile, csv2parquet

# Make these classes and modules available at the package level
__all__ = [
    'Flow',
    'bigqueryclient',  # module
    'BigQueryClient',  # class
    'BigQueryClientPolars',  # class
    'bigqueryclientpolars',  # module
    'sourcing',        # module
    'Sourcing',        # class
    'fastKNN',         # module
    'fastKNN',         # class
    'utils',           # module
    'timer_decorator', # function
    'concat_files',    # function
    'profile',         # function
    'csv2parquet',     # function
]
