#! /usr/bin/env python3
import shutil
import os
import subprocess

# NCCS Test Harness package imports
from libraries.repositories.svn_repository import SVNRepository 
from libraries.repositories.git_repository import GitRepository 

class RepositoryFactory:
    """ This class is a factory that creates repository objects.

    This class creates a repository object by calling the class method
    create. Currently only git and svn repository objects are supported.
    """
    @classmethod
    def create(cls,
               type_of_repository,
               location_of_repository,
               internal_repo_path_to_applications):
        """ Creates a repository object that encapuslates the repository behavoir. 

        This class method will a Repository object if the type_of_repository is 
        supported, othewise a value of None will be returned. 

        :param type_of_repository: The type of repositiory
        :type type_of_repository: string

        :param location_of_repository: The fully qualified path to an existing repository.
        :type location_of_repository: string

        :param internal_repo_path_to_applications: The internal path within the repository to the Application
                                                   directory
        :type internal_repo_path_to_applications: string

        :returns: my_repository
        :rtype: A Repository object - currently only GitRepository or SVNRepository objects 
                are returned. 
        """

        # Check if the repository string value in type_of_repository 
        # matches one of the supported types.  
        my_repository = None
        if type_of_repository == "git":
            my_repository = GitRepository(location_of_repository,
                                          internal_repo_path_to_applications)
        elif type_of_repository == "svn":
            my_repository = SVNRepository(location_of_repository,
                                          internal_repo_path_to_applications)
        else:
            # No supporting repository if program reaches this branch.
            my_repository = None

        return my_repository
    
    @classmethod
    def createLocalSVNRepoFromExistingDirectory(cls,
                                             path_to_sample_directory,
                                             path_to_local_dir,
                                             internal_repo_path_to_applications):


        completed_svn_init = subprocess.run(["svnadmin","create",path_to_local_dir])
        svn_url = "file://" + path_to_local_dir
        subprocess.run(["svn","import",path_to_sample_directory,svn_url,"-m 'Initial svn commit'"])
        return RepositoryFactory.create("svn",
                                         svn_url,
                                         internal_repo_path_to_applications)
    
    @classmethod
    def createLocalGitRepoFromExistingDirectory(cls,
                                                path_to_sample_directory,
                                                path_to_local_dir,
                                                internal_repo_path_to_applications):
        starting_directory = os.getcwd()

        if os.path.exists(path_to_local_dir) :
            shutil.rmtree(path_to_local_dir)

        shutil.copytree(path_to_sample_directory,path_to_local_dir)
        
        os.chdir(path_to_local_dir)

        completed_git_init = subprocess.run(["git","init"])

        completed_git_add = subprocess.run(["git","add","."])

        completed_git_commit = subprocess.run(["git","commit","-m", "My git commit"])

        os.chdir(starting_directory )

        return RepositoryFactory.create("git",
                                         path_to_local_dir,
                                         internal_repo_path_to_applications)
