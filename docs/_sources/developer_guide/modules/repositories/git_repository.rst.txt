.. _git_repository_module:

git_repository Module Documentation
===================================

.. toctree::
   :maxdepth: 1

.. py:module:: git_repository 

.. py:class:: GitRepository(git_remote_repository_url=None,my_repository_branch="master")

    This class encapsulates the data transfer from the remote git repository

    :param str git_remote_repository_url: A string that is URL for cloning the repository.
    :param str my_repository_branch: A string that is the branch of the remote repository.


    .. py:method:: binaryName
        :property:
     
        A property for the name of the git binary. 

    .. py:method:: repository_branch
        :property:

        A property for the name of the remote repository branch
 
    .. py:method:: remote_repository_URL
        :property:

        A property for the name of the remote repository URL.
     
    .. py:method:: cloneRepository(destination_directory=".") 

        Clones remote repository to *destination_dir*. The clone repository must not 


.. py:function:: get_type_of_repository 

.. py:function:: get_application_parent_directory

.. py:function:: get_fully_qualified_url_of_application_parent_directory

.. py:function:: get_repository_url_of_application

.. py:function:: get_repository_git_branch
