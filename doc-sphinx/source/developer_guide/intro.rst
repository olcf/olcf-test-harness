============
Introduction
============

.. toctree::
   :maxdepth: 1

Raison d'etre
=============
The NCCS_Test_Harness, hereafter referred as the Harness, is used for OLCF
machine acceptances, and is generally designed for Linux
or UNIX like operating systems. The Harness goal is to replicate users
development and production environment for machine validation and stress
testing. This is accomplished by repeatedly building applications, submitting these
application's jobs to the job scheduler (PBS, LSF, etc.), and recording the
results of the applications job builds and runs. 

Organizational Structure
========================
The Harness top-level directory contains the directory *.git* and is hereafter
referred to as *olcf-test-harness*. The Harness organization structure has 4
parts. The first part is the python files to run the application tests for
acceptance. These files are predominantly located in the directory
*olcf-test-harness/harness*.

The second part is the runtime configuration files for various OLCF machines.
The files are predominantly located in directories
*olcf-test-harness/modulefiles* and *olcf-test-harness/configs*. 

The third part is the unit tests for CI development. These files are
predominantly located in directory *olcf-test-harness/ci_testing_utilities*.

The fourth part is the Harness user and developer documentation located in the
directory *olcf-test-harness/doc-sphinx*. ::

    olcf-test-harness
        |-- ci_testing_utilities/
        |-- configs/
        |-- doc-sphinx/
        |-- harness/
        `-- modulefiles/

Prequisites
===========
The harness requires Python 3.6 or greater (needs reference), the Lmod module system (needs
reference), Git X.Y or higher, 

* Unix/Linux operation system
* Bash shell
* Sphinx for documentation
* Git for source control
* GitLab CI/CD

Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
