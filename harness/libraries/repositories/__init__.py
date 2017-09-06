# NCCS Test Harness imports
import minimal_version

# Check that we have at least a minimal version of python
# to provide proper functionality of this package.
minimal_version.check_valid_python_version()

# Only these things are public from this package
# in this package.
from .repository_factory import RepositoryFactory
from .common_repository_utility_functions import get_type_of_repository
from .common_repository_utility_functions import get_location_of_repository

types_of_repositories = {"git" : "git",
                         "svn" : "svn"}
