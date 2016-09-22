from abc import ABCMeta
from abc import abstractmethod
import sys
import shutil
import os
import subprocess
import contextlib
import io
import tempfile

class SVNRepository:
    """ This class is encapsulates the behavoir of a svn repository.

    """

    def __init__(self,
                 location_of_repository=None,
                 internal_repo_path_to_applications=None):
        self.__binaryName = "svn"
        self.__locationOfRepository = location_of_repository
        self.__internalPathToApplications = internal_repo_path_to_applications
        self.__checkedOutDirectories = []

        return

    @classmethod
    def createLocalRepoFromExistingDirectory(cls,
                                             path_to_sample_directory,
                                             path_to_local_dir,
                                             internal_repo_path_to_applications):


        completed_svn_init = subprocess.run(["svnadmin","create",path_to_local_dir])
        svn_url = "file://" + path_to_local_dir
        subprocess.run(["svn","import",path_to_sample_directory,svn_url,"-m 'Initial svn commit'"])
        return RepositoryFactory.create("svn",
                                         svn_url,
                                         internal_repo_path_to_applications)
    def getLocationOfRepository(self):
        return self.__locationOfRepository

    def getLocationOfFile(self,
                          file):
        path_to_file = os.path.join(self.__locationOfRepository,
                                    self.__internalPathToApplications,
                                    file)
        return path_to_file

    def doSparseCheckout(self,
                         stdout_file_handle,
                         stderr_file_handle,
                         path_to_repository,
                         root_path_to_checkout_directory,
                         directory_to_checkout):
        """ Performs a sparse checkout of directory from the repository.

            :param stdout_file_handle: A file object to write standard out
            :type stdout_file_handle: A file object

            :param stderr_file_handle: A file object to write standard error
            :type stderr_file_handle: A file object

            :param path_to_repository: The url to the repository.
            :type path_to_repository: string

            :param root_path_to_checkout_directory: The fully qualified path the the to level of the sparse checkout directory.
            :type root_path_to_checkout_directory: string

            :param directory_to_checkout: A dictionary of directories or files to sparsely checkout.
            :type directories: a dictionary of strings of directory or file names.

            :returns: a tuple (message,exit_status) 
            :rtype:  message is a string, exit_status is an integer
        """
        message = ""
        exit_status = 0

        # Check if file handles are open
        if stdout_file_handle.closed:
            message +=  "Error! In sparse checkout the stdout file handle is closed"
            exit_status = 1
            return (message,exit_status)

        if stderr_file_handle.closed:
            message +=  "Error! In sparse checkout the stderr file handle is closed"
            exit_status = 1
            return (message,exit_status)

        # Define the svn options for a sparse checkout.
        svn_options = 'checkout -N'
       
        # Define the full qualified path the checkout location of the folder.
        tail_dir = os.path.basename(directory_to_checkout['application'])
        path_to_local_dir = os.path.join(root_path_to_checkout_directory,tail_dir)

        # Form the sparse checkout command for the application
        if not os.path.exists(path_to_local_dir):
            self.__checkedOutDirectories += [path_to_local_dir]
            sparse_checkout_command = "{my_bin} {my_options} {my_svn_path} {my_local_path}".format(
                                                my_bin = self.__binaryName, 
                                                my_options = svn_options, 
                                                my_svn_path = directory_to_checkout['application'],
                                                my_local_path = path_to_local_dir)

            exit_status = subprocess.call(sparse_checkout_command,
                                          shell=True,
                                          stdout=stdout_file_handle,
                                          stderr=stderr_file_handle)

            if exit_status > 0:
                message += "Sparse checkout of command failed: " + sparse_checkout_command
                return (message,exit_status)


        # Form the update command for the source
        application_dir = os.path.basename(directory_to_checkout['application'])
        tail_dir = os.path.basename(directory_to_checkout['source'])
        path_to_local_dir = os.path.join(root_path_to_checkout_directory,application_dir,tail_dir)
        
        self.__checkedOutDirectories += [path_to_local_dir]
        svn_options = 'update'
        svn_update_command = "{my_bin} {my_options} {my_local_path}".format(
                                            my_bin = self.__binaryName, 
                                            my_options = svn_options, 
                                            my_local_path = path_to_local_dir)
        
        exit_status = subprocess.call(svn_update_command,
                                      shell=True,
                                      stdout=stdout_file_handle,
                                      stderr=stderr_file_handle)

        if exit_status > 0:
            message += "svn update command failed: " + sparse_checkout_command
            return (message,exit_status)

        # Form the update command for the test.
        application_dir = os.path.basename(directory_to_checkout['application'])
        for a_test in directory_to_checkout['test']:
            tail_dir = os.path.basename(a_test)
            path_to_local_dir = os.path.join(root_path_to_checkout_directory,application_dir,tail_dir)
            self.__checkedOutDirectories += [path_to_local_dir]
            svn_options = 'update'
            svn_update_command = "{my_bin} {my_options} {my_local_path}".format(
                                                my_bin = self.__binaryName, 
                                                my_options = svn_options, 
                                                my_local_path = path_to_local_dir)
            
            exit_status = subprocess.call(svn_update_command,
                                          shell=True,
                                          stdout=stdout_file_handle,
                                          stderr=stderr_file_handle)

            if exit_status > 0:
                message += "svn update command failed: " + sparse_checkout_command
                return (message,exit_status)

        return (message,exit_status)

    def verifySparseCheckout(self):
        """ Verifies that the directories exist for a sparse checkout.

            :returns: a tuple (message,exit_status) 
            :rtype:  message is a string, exit_status is an integer
        """

        test_result = True
        message = ""
        for dirpath in self.__checkedOutDirectories:
            if not os.path.exists(dirpath):
                test_result = False
                message += "Directory/file {0} did not checkout.".format(dirpath)
        return (message, test_result)

class GitRepository:
    """ This class is encapsulates the behavoir of a git repository.

    """
    def __init__(self,
                 location_of_repository=None,
                 internal_repo_path_to_applications=None):
        self.__binaryName = "git"
        self.__locationOfRepository = location_of_repository
        self.__internalPathToApplications = internal_repo_path_to_applications

        return

    @classmethod
    def createLocalRepoFromExistingDirectory(cls,
                                             path_to_sample_directory,
                                             path_to_local_dir,
                                             internal_repo_path_to_applications):
        starting_directory = os.getcwd()
        shutil.copytree(path_to_sample_directory,path_to_local_dir)
        
        os.chdir(path_to_local_dir)
        completed_git_init = subprocess.run(["git","init"])

        completed_git_add = subprocess.run(["git","add","."])

        completed_git_commit = subprocess.run(["git","commit","-m", "My git commit"])

        os.chdir(starting_directory )

        return RepositoryFactory.create("git",
                                         path_to_local_dir,
                                         internal_repo_path_to_applications)

    def getLocationOfRepository(self):
        return self.__locationOfRepository

    def getLocationOfFile(self,
                          file):
        path_to_file = os.path.join(self.__locationOfRepository,
                                    self.__internalPathToApplications,
                                    file)
        return path_to_file

    def doSparseCheckout(self,
                         stdout_file_handle,
                         stderr_file_handle,
                         path_to_repository,
                         root_path_to_checkout_directory,
                         directory_to_checkout):
        """ Performs a sparse checkout of directory from the repository.

            :param stdout_file_handle: A file object to write standard out
            :type stdout_file_handle: A file object

            :param stderr_file_handle: A file object to write standard error
            :type stderr_file_handle: A file object

            :param path_to_repository: The url to the repository.
            :type path_to_repository: string

            :param root_path_to_checkout_directory: The fully qualified path the the to level of the sparse checkout directory.
            :type root_path_to_checkout_directory: string

            :param directory_to_checkout: A list of directories or files to sparsely checkout.
            :type directories: a string list of directory or file names.

            :returns: a tuple (message,exit_status) 
            :rtype:  message is a string, exit_status is an integer
        """
        
        # Check if file handles are open
        message = ""
        if stdout_file_handle.closed:
            message =  "Error! In sparse checkout the stdout file handle is closed"
            exit_status = 1
            return (message,exit_status)

        if stderr_file_handle.closed:
            message =  "Error! In sparse checkout the stderr file handle is closed"
            exit_status = 1
            return (message,exit_status)
        
        # Define the full qualified path the checkout location of the folder.
        tail_dir = os.path.basename(directory_to_checkout)
        path_to_local_dir = os.path.join(root_path_to_checkout_directory,tail_dir)


        # Change to the hidden directory and do an empty clone of the repository.
        path_to_hidden_directory = os.path.join(root_path_to_checkout_directory,".hidden_git_repository")
        self.__doAnEmptyClone(path_to_local_directory = path_to_hidden_directory,
                              url_path_to_repository = path_to_repository)

        return


        # Verify git sparse checkout is enabled.
        self.__verifySparseCheckoutEnabled()

    def verifySparseCheckout(self):
        message = "Stud error meesage"
        test_result = False
        return (message, test_result)

    def __verifySparseCheckoutEnabled(self):
        """ Verifies that git the user has enabled sparse git checkouts. 

            If sparse git checkouts are not enabled, the program will 
            print a warning to stderr and exit.
        """

        # Define the git command to check if sparse checkouts are enabled
        git_command = "{my_bin} {my_options} {keyvalue}".format(my_bin = self.__binaryName,
                                                                my_options = "config --get",
                                                                keyvalue="core.sparsecheckout")
    
        # Run the git command and write the command's 
        # stderr and stdout results to 
        # unique temp files. The stdout tempfile has only one record which 
        # is searched for true or false. If true is found then
        # sparse checkout is enabled, otherwise sparse checkouts are
        # not enabled and we exit program.
        exit_status = 0
        with tempfile.NamedTemporaryFile("w",delete=False) as tmpfile_stdout:
            with tempfile.NamedTemporaryFile("w",delete=False) as tmpfile_stderr:
                exit_status = None
                message = None
                try:
                    exit_status = subprocess.check_call(git_command,
                                                        shell=True,
                                                        stdout=tmpfile_stdout,
                                                        stderr=tmpfile_stderr)
                except subprocess.CalledProcessError as exc :
                    exit_status = 1
                    message = "Error in subprocess command: " + exc.cmd
                except:
                    exit_status = 1
                    message = "Unexpected error!"

                # Close the file objects of the temporary files.
                tmpfile_stdout_path = tmpfile_stdout.name
                tmpfile_stderr_path = tmpfile_stderr.name
                tmpfile_stdout.close()
                tmpfile_stderr.close()

                # Remove the temporary files if the subprocess fails.
                if  exit_status > 0:
                    os.remove(tmpfile_stdout_path) 
                    os.remove(tmpfile_stderr_path) 
                    sys.exit(message)

                # Search for 'true' in the temp stdout file.
                tmpfile_stdout_contents = None
                with open(tmpfile_stdout_path,"r") as tmpfile_file_obj:
                    tmpfile_stdout_contents = tmpfile_file_obj.readlines()
                    if not ( 'true' in tmpfile_stdout_contents[0].lower() ) : 
                        error_message  =  "Error! Sparse checkout of git repositories is not enabled.\n"
                        error_message +=  "Please enable sparse checkout of git repositories." 
                        sys.exit(error_message)

                # Remove the temporary files before we return.
                os.remove(tmpfile_stdout_path) 
                os.remove(tmpfile_stderr_path) 
        return

    def __doAnEmptyClone(self,
                         path_to_local_directory,
                         url_path_to_repository):

        if not os.path.exists(path_to_local_directory):
            os.mkdir(path_to_local_directory)

        initial_dir = os.getcwd()
        os.chdir(path_to_local_directory)
        git_init_command = "{my_bin} {my_options}".format(my_bin=self.__binaryName,
                                                          my_options='init')
        run_as_subprocess_command(git_init_command)
        git_do_sparse_clone_command = "{my_bin} {my_options} {my_url}".format(my_bin=self.__binaryName,
                                                                             my_options = 'add -f origin',
                                                                             my_url = url_path_to_repository)
        run_as_subprocess_command(git_do_sparse_clone_command)
        os.chdir(initial_dir)

        return

class BaseRepository(metaclass=ABCMeta):
    """ This class define the comman behavoir of a repository as expected by the NCCS Test Harness.

    """
    def __init__(self):
        print("In base repository")
        return

    @classmethod
    @abstractmethod
    def createLocalRepoFromExistingDirectory(cls):
        return

    @abstractmethod
    def doSparseCheckout(self):
        return

    @abstractmethod
    def verifySparseCheckout(self):
        return

    @abstractmethod
    def getLocationOfRepository(self):
        return

    @abstractmethod
    def getLocationOfFile(self):
        return

BaseRepository.register(SVNRepository)
BaseRepository.register(GitRepository)

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

def run_as_subprocess_command(cmd):
    """ Runs the command in the string cmd by subprocess.

            :param cmd: A string containing the command to run
            :type cmd: string
    """
    # Run the git command and write the command's 
    # stderr and stdout results to 
    # unique temp files. The stdout tempfile has only one record which 
    # is searched for true or false. If true is found then
    # sparse checkout is enabled, otherwise sparse checkouts are
    # not enabled and we exit program.
    exit_status = 0
    with tempfile.NamedTemporaryFile("w",delete=False) as tmpfile_stdout:
        with tempfile.NamedTemporaryFile("w",delete=False) as tmpfile_stderr:
            exit_status = None
            message = None
            try:
                exit_status = subprocess.check_call(git_command,
                                                    shell=True,
                                                    stdout=tmpfile_stdout,
                                                    stderr=tmpfile_stderr)
            except subprocess.CalledProcessError as exc :
                exit_status = 1
                message = "Error in subprocess command: " + exc.cmd
            except:
                exit_status = 1
                message = "Unexpected error!"
    
            # Close the file objects of the temporary files.
            tmpfile_stdout_path = tmpfile_stdout.name
            tmpfile_stderr_path = tmpfile_stderr.name
            tmpfile_stdout.close()
            tmpfile_stderr.close()
    
            # Remove the temporary files if the subprocess fails.
            if  exit_status > 0:
                os.remove(tmpfile_stdout_path) 
                os.remove(tmpfile_stderr_path) 
                sys.exit(message)
    
            # Remove the temporary files before we return.
            os.remove(tmpfile_stdout_path) 
            os.remove(tmpfile_stderr_path) 
    return
