#! /usr/bin/env python3

import os

def get_path_to_sample_directory():
    """ Returns the fully qualified path to the directory 'Sample_Directory_For_Repository_Testing'

        :returns: path_to_dir, The path to the directory which is used for creating the test repository.    
        :rtype:  string
    """
    path_head = os.getenv('PATH_TO_HARNESS_TOP_LEVEL')
    path_to_dir = os.path.join(
        path_head, 'test', 'input_files', 'Sample_Directory_For_Repository_Testing')
    return path_to_dir

def get_path_to_application_directory(tag):
    """ Returns the fully qualified path to the directory which will serve as the root for the checkedout applications. 

        :returns:  path_to_dir, The path to the directory which will serve as the root for the checkedout applications. 
        :rtype:  string
    """
    path_head = os.path.abspath('.')
    path_to_dir = os.path.join(path_head,tag)
    return path_to_dir

def create_application_directory(my_unit_test):
    if os.path.exists(my_unit_test.pathToApplications) :
        shutil.rmtree(my_unit_test.pathToApplications)
    os.makedirs(my_unit_test.pathToApplications)
    return

