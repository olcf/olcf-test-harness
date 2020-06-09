#!/usr/bin/env python3

import copy
import os
import sys
from pathlib import Path
from string import Template
from libraries.repositories.repository_factory import RepositoryFactory
from libraries.rgt_utilities import try_symlink



class  apptest_layout(object):

    # define specific file names
    app_info_filename = 'application_info.txt'
    test_info_filename = 'test_info.txt'
    test_input_txt_filename = 'rgt_test_input.txt'
    test_input_ini_filename = 'rgt_test_input.ini'
    test_kill_filename = '.kill_test'
    test_rc_filename = '.testrc'
    test_status_filename = 'rgt_status.txt'
    test_summary_filename = 'rgt_summary.txt'
    job_status_filename = 'job_status.txt'
    job_id_filename = 'job_id.txt'

    # define specific directory names
    app_source_dirname = 'Source'
    test_build_dirname = 'build_directory'
    test_correct_results_dirname = 'Correct_Results'
    test_run_dirname = 'workdir'
    test_run_archive_dirname = 'Run_Archive'
    test_scripts_dirname = 'Scripts'
    test_status_dirname = 'Status'
    test_performance_dirname = 'Performance'

    # define special file suffixes
    suffix_for_ignored_tests = '.ignore_test'
    suffix_for_ignored_apps  = '.ignore_app'

    directory_structure_template = {
        'app'             : os.path.join("${pdir}", "${app}"),
        'app_info'        : os.path.join("${pdir}", "${app}", app_info_filename),
        'app_source'      : os.path.join("${pdir}", "${app}", app_source_dirname),
        'test'            : os.path.join("${pdir}", "${app}", "${test}"),
        'test_info'       : os.path.join("${pdir}", "${app}", "${test}", test_info_filename),
        'test_rc'         : os.path.join("${pdir}", "${app}", "${test}", test_rc_filename),
        'test_correct'    : os.path.join("${pdir}", "${app}", "${test}", test_correct_results_dirname),
        'test_perf'       : os.path.join("${pdir}", "${app}", "${test}", test_performance_dirname),
        'runarchive_dir'  : os.path.join("${pdir}", "${app}", "${test}", test_run_archive_dirname, "${id}"),
        'scripts_dir'     : os.path.join("${pdir}", "${app}", "${test}", test_scripts_dirname),
        'test_input_ini'  : os.path.join("${pdir}", "${app}", "${test}", test_scripts_dirname, test_input_ini_filename),
        'test_input_txt'  : os.path.join("${pdir}", "${app}", "${test}", test_scripts_dirname, test_input_txt_filename),
        'kill_file'       : os.path.join("${pdir}", "${app}", "${test}", test_scripts_dirname, test_kill_filename),
        'status_dir'      : os.path.join("${pdir}", "${app}", "${test}", test_status_dirname, "${id}"),
        'job_id_file'     : os.path.join("${pdir}", "${app}", "${test}", test_status_dirname, "${id}", job_id_filename),
        'job_status_file' : os.path.join("${pdir}", "${app}", "${test}", test_status_dirname, "${id}", job_status_filename),
        'status_file'     : os.path.join("${pdir}", "${app}", "${test}", test_status_dirname, test_status_filename)
    }

    #
    # Constructor
    #
    def __init__(self,
                 applications_rootdir,
                 name_of_application,
                 name_of_subtest,
                 harness_id=None):
        self.__applications_root = applications_rootdir
        self.__appname = name_of_application
        self.__testname = name_of_subtest
        self.__testid = harness_id
        self.__workspace = None

        # Set the application and test layout
        self.__apptest_layout = copy.deepcopy(apptest_layout.directory_structure_template)
        self.__setApplicationTestLayout()

    # Return the harness id for the test (may be None)
    def get_harness_id(self):
        return self.__testid

    #
    # Debug function.
    #
    def debug_layout(self):
        print ("\n\n")
        print ("================================================================")
        print ("Debugging local layout " + self.__appname + self.__testname)
        print ("================================================================")
        for key in self.__apptest_layout.keys():
            print ("%-20s = %-20s" % (key, self.__apptest_layout[key]))
        print ("================================================================\n\n")

    #
    # Returns the path to the application directory.
    #
    def get_path_to_application(self):
        return self.__apptest_layout['app']

    #
    # Returns the path to the application source directory.
    #
    def get_path_to_source(self):
        return self.__apptest_layout['app_source']

    #
    # Returns the path to the test directory.
    #
    def get_path_to_test(self):
        return self.__apptest_layout['test']

    #
    # Returns the path to the test scripts directory.
    #
    def get_path_to_scripts(self):
        return self.__apptest_layout['scripts_dir']

    #
    # Returns the path to the test run archive directory.
    #
    def get_path_to_runarchive(self):
        return self.__apptest_layout['runarchive_dir']

    #
    # Returns the path to the test status directory.
    #
    def get_path_to_status(self):
        return self.__apptest_layout['status_dir']

    #
    # Returns the path to the test workspace directory.
    #
    def get_path_to_workspace(self):
        return self.__workspace

    #
    # Returns the path to the test workspace build directory.
    #
    def get_path_to_workspace_build(self):
        if self.__workspace is None:
            return None
        return os.path.join(self.__workspace, apptest_layout.test_build_dirname)

    #
    # Returns the path to the test workspace run directory.
    #
    def get_path_to_workspace_run(self):
        if self.__workspace is None:
            return None
        return os.path.join(self.__workspace, apptest_layout.test_run_dirname)

    #
    # Returns the path to the test status directory.
    #
    def create_test_status(self):
        """
        Get Status directory for test instance.
        Create directory if it does not exist.
        """
        spath = self.get_path_to_status()
        if not os.path.exists(spath):
            os.makedirs(spath)

        #
        # Create convenience link to latest status dir
        #
        apptest_dir = self.get_path_to_test()
        latest_lnk = os.path.join(apptest_dir, apptest_layout.test_status_dirname, 'latest')
        if os.path.exists(latest_lnk):
            os.unlink(latest_lnk)
        try_symlink(spath, latest_lnk)

        return spath

    def create_test_runarchive(self):
        """
        Get Run_Archive directory for test instance.
        Create directory if it does not exist.
        """
        #
        # rpath = apptest_dir/Run_Archive/id_string
        # This path should be unique.
        #
        rpath = self.get_path_to_runarchive()
        if not os.path.exists(rpath):
            os.makedirs(rpath)

            #
            # Create convenience link to latest Run_Archive dir
            #
            apptest_dir = self.get_path_to_test()
            latest_lnk = os.path.join(apptest_dir, apptest_layout.test_run_archive_dirname, 'latest')
            if os.path.exists(latest_lnk):
                os.unlink(latest_lnk)
            try_symlink(rpath, latest_lnk)

        return rpath

    def create_workspace_links(self):
        """
        Create convenience links from/to this workspace to associated
        Status and Run_Archive directories.
        """
        st_dir = self.get_path_to_status()
        ra_dir = self.get_path_to_runarchive()
        ws_dir = self.get_path_to_workspace()
        build_dir = self.get_path_to_workspace_build()
        run_dir = self.get_path_to_workspace_run()

        try_symlink(st_dir, os.path.join(ws_dir, apptest_layout.test_status_dirname))
        try_symlink(ra_dir, os.path.join(ws_dir, apptest_layout.test_run_archive_dirname))
        try_symlink(build_dir, os.path.join(ra_dir, apptest_layout.test_build_dirname))
        try_symlink(run_dir, os.path.join(ra_dir, apptest_layout.test_run_dirname))

    def create_test_workspace(self, path_to_workspace):
        """
        Create temporary workspace for apptest instance if it does not exist.
        """
        # Create workspace dir
        wspace_dir = Path(path_to_workspace, self.__appname, self.__testname, self.__testid)
        wspace_dir.mkdir(parents=True, exist_ok=True)

        # Do not create the build directory. We use shutil.copytree() to create it by
        # copying the application source directory.

        # Create run directory
        run_dir = Path(wspace_dir, apptest_layout.test_run_dirname)
        run_dir.mkdir(parents=False, exist_ok=True)

        self.__workspace = str(wspace_dir)
        self.create_workspace_links()

        return self.__workspace

    # Returns the path to the top level of the Tests.
    def get_path_to_application_tests(self):
        return self.__applications_root

    # Returns the path to kill file
    def get_path_to_kill_file(self):
        return self.__apptest_layout['kill_file']

    # Returns the path to rc file
    def get_path_to_rc_file(self):
        return self.__apptest_layout['test_rc']

    # Returns the path to the status file.
    def get_path_to_status_file(self):
        return self.__apptest_layout['status_file']

    # Returns the path to the job status file.
    def get_path_to_job_status_file(self):
        return self.__apptest_layout['job_status_file']

    # Returns the path to the job id file.
    def get_path_to_job_id_file(self):
        return self.__apptest_layout['job_id_file']

    def get_path_to_performance_dir(self):
        return self.__apptest_layout['test_perf']

    def get_path_to_start_binary_time(self,uniqueid):
        path = None
        tmppath = os.path.join(self.__apptest_layout['status_dir'],
                               "start_binary_execution_timestamp.txt")

        if os.path.exists(tmppath):
           path = tmppath

        return path

    def get_path_to_end_binary_time(self,uniqueid):
        path = None
        tmppath = os.path.join(self.__apptest_layout['status_dir'],
                               "final_binary_execution_timestamp.txt")

        if os.path.exists(tmppath):
           path = tmppath

        return path

    #
    # Sets the application and test directory structure.
    #
    def __setApplicationTestLayout(self):
        # Initialize template substitutions dictionary
        subs = dict(pdir=self.__applications_root,
                    app=self.__appname,
                    test=self.__testname,
                    id=self.__testid)

        # Create __apptest_layout by applying substitutions to the directory structure template
        for (key, val_template) in apptest_layout.directory_structure_template.items():
            path_template = Template(val_template)
            self.__apptest_layout[key] = path_template.substitute(subs)


def get_layout_from_scriptdir(scripts_path):
    """
    Convert given scripts directory path into apps_root, app name, and test name,
    after checking that it is actually a scripts directory
      <apps_root>/<app>/<test>/Scripts
    """
    apps_root = None
    app = None
    test = None

    scriptdir = Path(scripts_path).resolve(strict=True)
    num_parent_dirs = len(scriptdir.parents)
    if num_parent_dirs < 3:
        message = f'The scripts directory {scriptdir} is ill-formed. It has less than 3 parent directories.'
        sys.exit(message)

    test = scriptdir.parents[0].name
    app = scriptdir.parents[1].name
    apps_root = str(scriptdir.parents[2])

    return apps_root, app, test

def get_layout_from_runarchivedir(archive_path):
    """
    Convert given scripts directory path into apps_root, app name, and test name,
    after checking that it is actually a scripts directory
      <apps_root>/<app>/<test>/Run_Archive/<id>
    """
    apps_root = None
    app = None
    test = None
    testid = None

    radir = Path(archive_path).resolve(strict=True)
    num_parent_dirs = len(radir.parents)
    if num_parent_dirs < 4:
        message = f'The run archive directory {radir} is ill-formed. It has less than 4 parent directories.'
        sys.exit(message)

    testid = radir.name
    test = radir.parents[1].name
    app = radir.parents[2].name
    apps_root = str(radir.parents[3])

    return apps_root, app, test, testid


