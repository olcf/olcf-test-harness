Git Unit Test Framework
=================================

.. .. toctree::
..    :maxdepth: 1

The Harness unit testing framework uses Python's pytest module
to implement the unit tests, and GitLab's CI/CD service to run 
the tests. The unit tests can also be ran without GitLabs CI/CD 
service.

Organizational Structure
------------------------

The source for the Harness unit tests are located in directory
*olcf-test-harness/ci_testing_utilities*. The main driver scripts to run the
generic and machine specific tests are located in directory
*olcf-test-harness/ci_testing_utilities/bin*.  

The python unit tests are located in directory 
*olcf-test-harness/ci_testing_utilities/harness_unit_tests*. The machine
specific unit tests are located in an eponymous subdirectory.
For machine *Ascent*, its machine specific tets are located in
*olcf-test-harness/ci_testing_utilities/harness_unit_tests/Ascent*.
The directory *olcf-test-harness/ci_testing_utilities/input_files* 
contains input files for running tests. These files are sometimes
required by the test fixtures for setting up tests. Lastly,
the directory *olcf-test-harness/ci_testing_utilities/harness_unit_tests/runtime_environment*
contains files that set up the runtime environment for the 
generic and machine specific tests. ::

    ci_testing_utilities
    |-- __init__.py
    |-- bin/
    |   |-- run_generic_unit_tests.py*
    |   `-- run_machine_specific_unit_tests.py*
    |-- harness_unit_tests/
    |   |-- Ascent/
    |   |-- __init__.py
    |   |-- __pycache__/
    |   |-- harness_unittests_exceptions.py
    |   |-- harness_unittests_logging.py
    |   |-- test_concurrency.py
    |   `-- test_runtests.py
    |-- input_files/
    `-- runtime_environment/
        |-- Ascent-olcf5_acceptance.unit_tests.lua
        `-- GenericMachine-GenericConfigTag.unit_tests.lua


Setting Up the Harness Unit Testing Runtime Environment
-------------------------------------------------------

Generic Tests
~~~~~~~~~~~~~

To set up the runtime environment to run the generic 
Harness unit tests, within directory *olcf-test-harness* 
one needs to do following commands: 

    **export OLCF_HARNESS_DIR=$(pwd)**

    **module \\-\\-ignore-cache use modulefiles**

    **module load olcf_harness**

Machine Specific Tests
~~~~~~~~~~~~~~~~~~~~~~

To set up the runtime environment to run the machine specific 
Harness unit tests, within directory *olcf-test-harness* 
one needs to do following commands: 

    **export OLCF_HARNESS_DIR=$(pwd)**

    **module \\-\\-ignore-cache use modulefiles**

    **module load olcf_harness**

    **export HUT_MACHINE_NAME <The machine name>**

    **export HUT_CONFIG_TAG <The config tag for the machine>**


Running the Harness Unit Tests
------------------------------

Generic Tests
~~~~~~~~~~~~~

To run the generic unit tests run the command:

    **run_generic_unit_tests.py** 

Machine Specific Tests
~~~~~~~~~~~~~~~~~~~~~~

To run the machine specific unit tests, appropiately define the environmental
variables *HUT_MACHINE_NAME* and *HUT_CONFIG_TAG*, then run the command:

    **run_machine_specific_unit_tests.py** 

See ?? for a list of machine names and config tags.

Harness Unit Testing API
------------------------

.. toctree::
   :maxdepth: 1

   unit_test_framework/git_ci_test_framework.rst
   unit_test_framework/pytest_test_framework.rst
