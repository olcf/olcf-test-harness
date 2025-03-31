NCCS Harness repositories package
=================================

.. toctree::
   :maxdepth: 2

Intoduction
-----------

This package provides the harness the functionality to clone the repositories
that contain the applications and tests. Currently only git repositories are supported, and 
the git commands be passwordless authentication.

Prerequisite Environmental Variables
------------------------------------

The following environmental variable must be set:

* **RGT_TYPE_OF_REPOSITORY** : The type of repository. Currently only git remote repositories are supported.

    Permitted values: git

* **RGT_GIT_DATA_TRANSFER_PROTOCOL** : The data transfer protocol for the git repository. Currently on the ssh protocol is supported.

    Permitted values: ssh

* **RGT_GIT_HTTPS_SERVER_URL** : The base part of the URL used in the https protocol git clone. 


* **RGT_GIT_SSH_SERVER_URL** :  The base part of the URL used in the ssh protocol git clone.


* **RGT_GIT_SERVER_APPLICATION_PARENT_DIR** : The parent part of the URL used in the ssh or https protocol git clone


* **RGT_GIT_MACHINE_NAME** : The machine name part of the application URL 


* **RGT_GIT_REPS_BRANCH** : The branch of the repository to check out.


Examples
--------

Consider the following test repository "https://gitlab.ccs.ornl.gov/olcf-system-test/applications/summit/HelloWorld"
located on the git server "https://gitlab.ccs.ornl.gov". We will use the ssh data transfer protocol and checkout 
the branch master. As given by the repository the git URL for cloning
is ::

    gitlab@gitlab.ccs.ornl.gov:olcf-system-test/applications/summit/HelloWorld.git


The above environmental variables needs the following values:

::

    RGT_TYPE_OF_REPOSITORY='git'
    RGT_GIT_REPS_BRANCH='master'
    RGT_GIT_DATA_TRANSFER_PROTOCOL='ssh'
    RGT_GIT_HTTPS_SERVER_URL=''
    RGT_GIT_SSH_SERVER_URL='gitlab@gitlab.ccs.ornl.gov'
    RGT_GIT_SERVER_APPLICATION_PARENT_DIR='olcf-system-test/applications'
    RGT_GIT_MACHINE_NAME='summit'

Modules
-------

:ref:`git_repository_module`

