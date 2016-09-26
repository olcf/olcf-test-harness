import sys
import shutil
import os
import subprocess
import contextlib
import io
import tempfile

# NCCS Tesst Harness packages
from libraries.repositories.common_repository_utility_functions import run_as_subprocess_command
from libraries.repositories.common_repository_utility_functions import run_as_subprocess_command_return_stdout_stderr
from libraries.repositories.abstract_repository import BaseRepository


class GitRepository(BaseRepository):
    """ This class is encapsulates the behavoir of a git repository.
    """
    def __init__(self,
                 location_of_repository=None,
                 internal_repo_path_to_applications=None):

        
        self.__binaryName = "git" #:ivar __binaryName: The name of the git binary.
        self.__locationOfRepository = location_of_repository
        self.__internalPathToApplications = internal_repo_path_to_applications
        self.__checkedOutDirectories = []

        # git rev-parse --is-inside-work-tree

        return


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
        

        # Change to the hidden directory and do an empty clone of the repository.
        starting_directory = os.getcwd()

        path_to_hidden_directory = os.path.join(root_path_to_checkout_directory,
                                                ".hidden_git_repository")
        
        self.__doAnEmptyClone(path_to_local_directory = path_to_hidden_directory,
                              url_path_to_repository = path_to_repository)


        self.__doEnableSparseCheckout(path_to_local_directory = path_to_hidden_directory) 

        path_to_application_dir = \
        self.__defineDirectoryToSparseApplicationCheckout(files_to_sparsely_checkout = directory_to_checkout,
                                                          path_to_hidden_repo = path_to_hidden_directory)
        
        files_to_checkout = self.__defineFilesToCheckout(path_to_local_directory = path_to_hidden_directory,
                                                         files_to_sparsely_checkout = directory_to_checkout)

        
        self.__doCheckout(path_to_local_directory = path_to_hidden_directory)

        self.__formSymbolicLinksToDirectory(root_path_to_checkout_directory,
                                            path_to_application_dir)

        self.__defineFilesForVerifying(root_path_to_checkout_directory,
                                       directory_to_checkout)

        return


        # Verify git sparse checkout is enabled.
        self.__verifySparseCheckoutEnabled()

    def verifySparseCheckout(self):
        test_result = True
        message = ""
        for dirpath in self.__checkedOutDirectories:
            if not os.path.exists(dirpath):
                test_result = False
                message += "Directory/file {0} did not checkout.".format(dirpath)
        return (message, test_result)

    def removeRepository(self):
        shutil.rmtree(self.__locationOfRepository)
        return

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
                    message = "Unexpected error! " + git_command

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

        
        initial_dir = os.getcwd()

        if os.path.exists(path_to_local_directory):

            os.chdir(path_to_local_directory)

            if not self.__directoryUnderGitControl():
                git_init_command = "{my_bin} {my_options}".format(my_bin=self.__binaryName,
                                                                  my_options='init')
                run_as_subprocess_command(git_init_command)

                git_do_sparse_clone_command = "{my_bin} {my_options} {my_url}".format(my_bin=self.__binaryName,
                                                                                     my_options = 'remote add -f origin',
                                                                                     my_url = url_path_to_repository)
                run_as_subprocess_command(git_do_sparse_clone_command)
            os.chdir(initial_dir)

        else:
            os.mkdir(path_to_local_directory)
            
            os.chdir(path_to_local_directory)

            git_init_command = "{my_bin} {my_options}".format(my_bin=self.__binaryName,
                                                              my_options='init')
            run_as_subprocess_command(git_init_command)

            git_do_sparse_clone_command = "{my_bin} {my_options} {my_url}".format(my_bin=self.__binaryName,
                                                                                 my_options = 'remote add -f origin',
                                                                                 my_url = url_path_to_repository)
            run_as_subprocess_command(git_do_sparse_clone_command)
            
            os.chdir(initial_dir)

        return

    def __doEnableSparseCheckout(self,
                                 path_to_local_directory):
        initial_dir = os.getcwd()

        os.chdir(path_to_local_directory)

        # Enable sparse checkouts.
        git_enable_sparse_checkouts_command = "{my_bin} {my_options}".format(my_bin=self.__binaryName,
                                                                             my_options='config core.sparseCheckout true')

        run_as_subprocess_command(git_enable_sparse_checkouts_command)

        os.chdir(initial_dir)

        return

    def __defineFilesToCheckout(self,
                                path_to_local_directory,
                                files_to_sparsely_checkout):
        
        a_record = "{entry}\n"

        path_to_sparse_checkout_file = os.path.join(path_to_local_directory,".git","info","sparse-checkout")

        if not os.path.exists(path_to_sparse_checkout_file):
            self.__touch(path_to_sparse_checkout_file)

        # Read all entries in file sparse-checkout.
        sparse_checkout = []
        with open(path_to_sparse_checkout_file,'r') as file_obj:
            tmp_sparse_checkout = file_obj.readlines()
            for tmp_record in tmp_sparse_checkout:
                sparse_checkout += [tmp_record.strip()]
            
        
        # Remove duplicate entries in files_to_sparsely_checkout as compared
        # to sparse_checkout file.

        # Remove duplicated source.
        tmp_record = files_to_sparsely_checkout['source']
        if not (tmp_record in sparse_checkout) : 
            sparse_checkout += [tmp_record.strip()]

        # Remove duplicated tests.
        for tmp_record in files_to_sparsely_checkout['test']:
            if not (tmp_record in sparse_checkout):
                sparse_checkout += [tmp_record.strip()]

        # Now write new sparse-checkout file.
        with open(path_to_sparse_checkout_file,'w') as file_obj:
            for tmp_record in sparse_checkout:
                file_obj.write(a_record.format(entry = tmp_record))

        return sparse_checkout

    def __doCheckout(self,
                     path_to_local_directory):
        initial_dir = os.getcwd()

        os.chdir(path_to_local_directory)

        # Do checkout
        git_checkout_command = "{my_bin} {my_options}".format(my_bin=self.__binaryName,
                                                                             my_options='checkout master')
        run_as_subprocess_command(git_checkout_command)
        os.chdir(initial_dir)
        return

    def __defineDirectoryToSparseApplicationCheckout(self,
                                                     files_to_sparsely_checkout,
                                                     path_to_hidden_repo):
        path_to_source = files_to_sparsely_checkout['source']
        (path_to_application,source_name) = os.path.split(path_to_source ) 

        (root_path_to_application,application_name) = os.path.split(path_to_application)

        unormalized_path = path_to_hidden_repo + root_path_to_application 

        tmp_path = \
            os.path.normpath(unormalized_path)

        path_to_application_dir = os.path.join(tmp_path,application_name)

        return path_to_application_dir

    def __defineFilesForVerifying(self,
                                  root_path_to_checkout_directory,
                                  files_to_sparsely_checkout):

        # Define path to application.
        path_to_source = files_to_sparsely_checkout['source']
        (path_to_application,source_name) = os.path.split(path_to_source ) 
        (root_path_to_application,application_name) = os.path.split(path_to_application)
        path_to_application_dir = os.path.join(root_path_to_checkout_directory,application_name)
        if not ( path_to_application_dir in self.__checkedOutDirectories):
            self.__checkedOutDirectories += [path_to_application_dir]

        # Define path to source. 
        src_path = os.path.join(path_to_application_dir,source_name)
        if not ( src_path in self.__checkedOutDirectories):
            self.__checkedOutDirectories += [src_path]
        
        # Define path to tests. 
        for a_test in files_to_sparsely_checkout['test']:
            (path_to_test,test_name) = os.path.split(a_test)
            test_path = os.path.join(path_to_application_dir,test_name)
            if not ( test_path in self.__checkedOutDirectories):
                self.__checkedOutDirectories += [test_path]

        return

    def __formSymbolicLinksToDirectory(self,
                                       root_path_to_checkout_directory,
                                       path_to_dir):

        # Make sure that the directory exists 
        if not os.path.exists(path_to_dir):
            message = "The directory/file {} does not exist."
            message += "I therefore can not form a symbolic to it"
            sys.exit(message.format(path_to_dir))

        if not os.path.exists(root_path_to_checkout_directory):
            message = "The directory/file {} does not exist."
            message += "I therefore can not form a symbolic to it from"
            message += "within the directory {}.\n"
            sys.exit(message.format(root_path_to_checkout_directory))

        # Form the source of the symbolic link.
        src_of_symlink = path_to_dir

        # Form the destination of the symbolic link.
        application_name = os.path.basename(path_to_dir)
        dest_of_symlink = os.path.join(root_path_to_checkout_directory,application_name)

        if not os.path.exists(dest_of_symlink):
            os.symlink(src_of_symlink,dest_of_symlink) 
        return

    def __directoryUnderGitControl(self,
                                  directory_to_test=None):
        under_git_control = False
        if directory_to_test:
            initial_dir = os.getcwd()
            os.chdir(directory_to_test)

        # Do checkout
        git_rev_parse_cmd = "{my_bin} {my_options}".format(my_bin=self.__binaryName,
                                                       my_options='rev-parse --is-inside-work-tree')

        (stdout,stderr) = run_as_subprocess_command_return_stdout_stderr(git_rev_parse_cmd)
        
        if stdout[0].startswith("true"):
            under_git_control = True
        else:
            under_git_control = False

        if directory_to_test:
            os.chdir(initial_dir)

        return under_git_control

    def __touch(self,
                path):
        with open(path, 'a') as file_obj:
            os.utime(path, None)

        return
