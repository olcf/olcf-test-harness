#!/usr/bin/env python3

"""Utility functions for linux operating systems.


"""

# Python imports
import re
import inspect
import os
import subprocess
import shlex
import time

class LinuxEnvRegxp:
    """
    When one does an env | less on Linux, we get results similar to the following:
     
    ForwardX11=yes
    LMOD_PKG=/sw/summit/lmod/8.2.10
    PAMI_ENABLE_STRIPING=0
    OLCF_XL_ROOT=/sw/summit/xl/16.1.1-5
    LSF_SERVERDIR=/opt/ibm/spectrumcomputing/lsf/10.1.0.9/linux3.10-glibc2.17-ppc64le-csm/etc
    BASH_FUNC_module()=() {  eval $($LMOD_CMD bash "$@") && eval $(${LMOD_SETTARG_CMD:-:} -s sh)
    }
    BASH_FUNC_ml()=() {  eval $($LMOD_DIR/ml_cmd "$@")
    }
     
    Sometimes the environmental variable values are multiline entries, or the varible name
    contains non-alphanumeric charatcers. To ensure that one parses the environmental
    variable for the correct name and value, we need a complicated compiled python regular expression
    to match the start of a new environmental variable.
    """

    _reg_expression='(?P<key>^[\w_]+|^BASH_FUNC_.*)=(?P<value>[^ \t].*$)'
    """string: The regular expression
    
    If the regular expression is matched, we have the start of a new environmental
    variable.  When matched, the regular expression has 2 groups. The first group
    is accessed by "key", and it returns the environmental variable name. The
    second group is accessed by "value", and it returns the character string after
    the first equal sign.
    """

    env_variable_regxp = re.compile(_reg_expression,flags=re.ASCII)
    """re.compile : The compiled regular expression for matching the start of an environmental variable."""

def make_batch_script_for_linux(a_machine):
    """ Creates a batch script for Linux machines.

    Notes
    -----
    Raises an OSError exception if unable to read batch template file.
    Raises an OSError exception if unable to write batch file.

    Parameters
    ----------
    a_machine : A machine object with a Linux operating system.

    Returns
    -------
    logical : bstatus
        If bstatus is True, then batch script was successfully created.
        If bstatus is False, then batch script wasn't successfully created.
        
    """
    # Get the name of the current function.
    frame = inspect.currentframe()
    function_name = inspect.getframeinfo(frame).function

    # Log that our execution location.
    messloc = "In function {functionname}:".format(functionname=function_name ) 
    message = "Making batch script for {} using file {}.".format(a_machine.machine_name,a_machine.get_scheduler_template_file_name())
    a_machine.logger.doInfoLogging(message)

    bstatus = True

    batch_template_file = a_machine.get_scheduler_template_file_name()

    batch_file_path = os.path.join(a_machine.apptest.get_path_to_runarchive(),
                                   a_machine.test_config.get_batch_file())

    message = f"{messloc} The batch scheduler template file is {batch_template_file}."
    a_machine.logger.doInfoLogging(message)
    
    # Get batch job template lines
    try :
        with open(batch_template_file, "r") as templatefileobj:
            templatelines = templatefileobj.readlines()
    except OSError as err:
        bstatus = False
        message = ( f"{messloc} Error opening bath template file '{batch_template_file}' for reading."
                    f"Handling error: {err}\n" )
        a_machine.logger.doCriticalLogging(message)
    
    if bstatus:
        message = f"{messloc} Completed reading lines of the batch template file {batch_template_file}."
        a_machine.logger.doInfoLogging(message)

        # Create test batch job script in run archive directory
        try :
            with open(batch_file_path, "w") as batch_job:
                # Replace all the wildcards in the batch job template with the values in
                # the test config
                test_replacements = a_machine.test_config.get_test_replacements()
                for record in templatelines:
                    for (replace_key,val) in test_replacements.items():
                        re_tmp = re.compile(replace_key)
                        record = re_tmp.sub(val, record)
                    batch_job.write(record)
        except OSError as err:
            bstatus = False
            message = ( f"{messloc} Error opening bath template file '{batch_file_path}' for writing.\n"
                        f"Handling error: {err}\n" )
            a_machine.logger.doCriticalLogging(message)

        message = f"{messloc} Completed regex substitutions."
        a_machine.logger.doInfoLogging(message)

    return bstatus

def check_executable(a_machine,new_env):
    """
    Parameters
    ----------
    a_machine : A machine object with a Linux operating system.

    new_env : A dictionary
        A dictionary of environmental variables to be passed to Popen.

    Returns
    -------
    int
        The value of the check command exit status.
    """

    # Get the current location of execution.
    my_current_frame = inspect.currentframe()
    my_current_frame_info = inspect.getframeinfo(my_current_frame)
    my_functioname = my_current_frame_info.function
    messloc = "In function {functionname}:".format(functionname=my_functioname ) 

    checkcmd = a_machine.check_command
    path_to_checkscript = a_machine.apptest.get_path_to_scripts()
    check_command_line = _form_proper_command_line(path_to_checkscript,checkcmd)

    message = f"{messloc} The check command line is {check_command_line}."
    a_machine.logger.doInfoLogging(message)

    check_outfile = "output_check.txt"
    check_stdout = open(check_outfile, "w")

    if new_env != None:
        p = subprocess.Popen(check_command_line,shell=True,env=new_env,stdout=check_stdout,stderr=subprocess.STDOUT)
    else:
        p = subprocess.Popen(check_command_line,shell=True,stdout=check_stdout,stderr=subprocess.STDOUT)

    p.wait()
    check_stdout.close()

    check_exit_status = p.returncode

    message = f"{messloc} The check command return code {check_exit_status}."
    a_machine.logger.doInfoLogging(message)

    return check_exit_status

def is_all_tests_passed(stest):
    """ Verify that all tests have pased.
    
    Parameters
    ----------
    stest : A subtest object
            The subtest instance is used to check if the testing cycle is complete.

    Returns
    -------
    bool
        If the bool is True, then all tests have passed. Otherwise, if 
        any test has failed False is returned.
    """
    
    from libraries.status_file_factory import StatusFileFactory
    path_to_status_file = stest.get_path_to_status_file()
    sfile = StatusFileFactory.create(path_to_status_file=path_to_status_file)
    ret_val = sfile.didAllTestsPass()
    return ret_val

def isTestCycleComplete(stest):
    """ Verify that the testing cycle for the Harness jobs are completed.
    
    Parameters
    ----------
    stest : A subtest object
            The subtest instance is used to check if the testing cycle is complete.

    Returns
    -------
    bool
        If the bool is True, then the subtest cycle is complete. Otherwise
        the cycle in progress and False is returned.
    """
    # From the test status file, verify all jobs
    # are completed and no new jobs are waiting to run.
    # Get the path to the status file
    from libraries.status_file_factory import StatusFileFactory
    path_to_status_file = stest.get_path_to_status_file()
    sfile = StatusFileFactory.create(path_to_status_file=path_to_status_file)

    # Set the time between checks for verifying all jobs are complete
    # and no new jobs have started.
    time_between_checks = 10
    time_to_wait_for_new_job = 5
    jobs_still_pending = True

    # Set the number of checks to perform.
    max_checks = 3
    for check_nm in range(max_checks):
        last_harness_id = sfile.getLastHarnessID()
        time.sleep(time_between_checks)
        if sfile.isTestFinished(last_harness_id):
            # Wait a short time in case a new job is submitted.
            time.sleep(time_to_wait_for_new_job)
            new_harness_id = sfile.getLastHarnessID()
            if new_harness_id == last_harness_id:
                # No new job was submitted so no jobs pending.
                jobs_still_pending = False
            else :
                # A new job was submitted so we set the harness_id to 
                # its new value.
                jobs_still_pending = True
                harness_id = new_harness_id
    
    if jobs_still_pending == True:
        subtest_cyle_complete = False
    else:
        subtest_cyle_complete = True

    return subtest_cyle_complete

def get_new_environment(a_machine,filename):
    """ Returns a dictionary of the environmental variables.

    The method returns a dictionary of the environment of a process that
    runs the command to set the build runtime environment. The command
    along with the env command is writen to random file. The random file is
    executed and the output is captured parsed into a dictionary. 

    Parameters
    ----------
    filename : str
        The name of the file that contains the command to set the environment.

    Returns
    -------
    dict
        A dictionary obj["env_key"] = env_value where env_key is the environmental
        variable and env_value is its value.
    """
    path_to_build_directory = a_machine.apptest.get_path_to_workspace_build()
    tmp_source_file = os.path.join(path_to_build_directory,"tmp_source_file")
    std_out_file = os.path.join(path_to_build_directory,"std.env.out.txt")
    std_err_file = os.path.join(path_to_build_directory,"std.env.err.txt")

    #-----------------------------------------------------
    # Write the current environmental variables to file. -
    #                                                    -
    #-----------------------------------------------------
    with open(tmp_source_file, 'w') as tmp_src_file:
        tmp_src_file.write('#!/usr/bin/env bash\n')
        tmp_src_file.write('source %s\n'%filename)
        tmp_src_file.write('env\n')

    # Execute the random file with Popen and capture the std output.
    os.chmod(tmp_source_file,0o755)
    with open(std_out_file, 'w') as out:
        with open(std_err_file, 'w') as err:
            with subprocess.Popen([tmp_source_file],
                                  shell=False, 
                                  cwd=path_to_build_directory, 
                                  stdout=out, stderr=err) as process1:
                process1.wait()

    if process1.returncode != 0:
        message = "The return code of the Popen process to set the environment != 0."
        raise BaseMachine.SetBuildRTEError(message)

    #-----------------------------------------------------
    # Read the file and store the in list records.       -
    #                                                    -
    #-----------------------------------------------------
    with open(std_out_file, 'r') as infile:
        records = infile.readlines()

    #-----------------------------------------------------
    # Now loop over the records and process              -
    # the environment variables.                         -
    #                                                    -
    #-----------------------------------------------------
    env_dict = {}
    current_line_nm = 0
    nm_records = len(records)
    while current_line_nm < nm_records:
        # Check that on the current line we have a new environmental
        # variable entry for this line. If a new environmental variable 
        # is not  found then proceed to the next line.
        record_decoded = records[current_line_nm]

        search = LinuxEnvRegxp.env_variable_regxp.search(record_decoded)
        if search:
            key=search.group('key')
            a_machine.logger.doInfoLogging(f"Found new env variable {key} at line: {current_line_nm}")
        else:
            message = "Error in finding the next environment variable.\n"
            message += f"The following line, #{current_line_nm}, had no matches for searches:\n"
            message += record_decoded + "\n"
            a_machine.logger.doCriticalLogging(message)
            raise BaseMachine.SetBuildRTEError(message)

        # We now get the range of entries for this environmental variable.
        start_line = current_line_nm

        # Set the pending current line number to the current
        # line number. 
        pending_current_line_nm = current_line_nm

        if ( start_line == (nm_records-1) ):

            # We are at the last line and the finish
            # line is the last line.
            finish_line = nm_records - 1

            pending_current_line_nm += 1
        else:

            search_range_begin = current_line_nm + 1 # Set the start range for 
                                                     # searching the next environmental entry

            max_search_range_end = nm_records - 1 # Set the maximum rnage of lines to search.
                                                  # Offset by 1 because records 
                                                  # list index starts at 0.

            a_machine.logger.doInfoLogging(f"Search range is {search_range_begin} to {max_search_range_end}.")

            for tmp_line_nm in range(search_range_begin,max_search_range_end+1,1):
                pending_current_line_nm += 1
                record_decoded = records[tmp_line_nm]
                search = LinuxEnvRegxp.env_variable_regxp.search(record_decoded)
                if search:
                    # We have found the next environmental variable entry
                    # so break from for loop.
                    break


            # The finish_line is 1 less than the pending_current_line_nm
            # due to the prior for loop breaking at the start of the 
            # next environmental variable.
            finish_line = pending_current_line_nm - 1

            # We now parse the range of entries for the environmental key and 
            # value.
            _parse_env_variable(records[start_line:(finish_line+1)],env_dict)

        # The current line now is now equal to pending_current_line_nm.
        current_line_nm = pending_current_line_nm

    return env_dict

def build_executable(a_machine, new_env):
    """ Return the status of the build. Runs the build command.

    Parameters
    ----------
    a_machine : A machine object with a Linux operating system.

    new_env : A dictionary
        A dictionary of environmental variables to be passed to Popen.

    Returns
    -------
    int
        The value of the build command exit status.
    """
    # Get the name of the current function.
    frame = inspect.currentframe()
    function_name = inspect.getframeinfo(frame).function
    messloc = "In function {functionname}:".format(functionname=function_name ) 

    # Update the build environment
    env_vars = a_machine.test_config.test_environment
    message = ""
    for e in env_vars:
        v = env_vars[e]
        eu = e.upper()
        #print("Setting env var", eu, "=", v)
        os.putenv(eu, v)
        message += f"Set build environment variable {eu}={v}\n"
    if new_env is not None:
        for e in new_env:
            v = new_env[e]
            eu = e.upper()
            os.putenv(eu, v)
            message += f"Set build environment variable {eu}={v}\n"
    a_machine.logger.doInfoLogging(message)

    # We get the command for bulding the binary.
    buildcmd = a_machine.test_config.get_build_command()
    message = f"{messloc} The build command: {buildcmd}"
    a_machine.logger.doInfoLogging(message)

    if a_machine.separate_build_stdio:
        build_std_out = "output_build.stdout.txt"
        build_std_err = "output_build.stderr.txt"
        with open(build_std_out,"w") as build_std_out :
            with open(build_std_err,"w") as build_std_err :
                p = subprocess.Popen(buildcmd, shell=True, stdout=build_std_out, stderr=build_std_err)
                p.wait()
                build_exit_status = p.returncode
    else:
        build_out = "output_build.txt"
        with open(build_out,"w") as build_out :
            p = subprocess.Popen(buildcmd, shell=True, stdout=build_out, stderr=subprocess.STDOUT)
            p.wait()
            build_exit_status = p.returncode

    return build_exit_status

def submit_batch_script(a_machine, new_env):
    # Get the name of the current function.
    frame = inspect.currentframe()
    function_name = inspect.getframeinfo(frame).function
    messloc = "In function {functionname}:".format(functionname=function_name) 

    # Update the batch submission environment
    env_vars = a_machine.test_config.test_environment
    message = ""
    for e in env_vars:
        v = env_vars[e]
        eu = e.upper()
        #print("Setting env var", eu, "=", v)
        os.putenv(eu, v)
        message += f"Set batch environment variable {eu}={v}\n"
    if new_env is not None:
        for e in new_env:
            v = new_env[e]
            eu = e.upper()
            os.putenv(eu, v)
            message += f"Set batch environment variable {eu}={v}\n"
    a_machine.logger.doInfoLogging(message)

    # Submit the test's batch script
    batch_script = a_machine.test_config.get_batch_file()
    submit_exit_value = a_machine.submit_to_scheduler(batch_script)

    message = f"{messloc} Submitted batch script {batch_script} with exit status of {submit_exit_value}."
    return submit_exit_value

#-----------------------------------------------------
#                                                    -
# Private methods                                    -
#                                                    -
#-----------------------------------------------------

def _form_proper_command_line(path_to_scripts,command_line):
    args = shlex.split(command_line)
    proper_command = path_to_scripts
    for ip in range(len(args)):
        if ip == 0 :
            proper_command = proper_command + "/" + args[0]
        else:
            proper_command = proper_command + " " + args[ip]
    return proper_command

def _parse_env_variable(records,new_env):
    new_record = ""
    for (ip,tmp_line) in enumerate(records):
        if ip == 0 :
            search = LinuxEnvRegxp.env_variable_regxp.search(tmp_line)
            key=search.group('key')
            tmp_value = search.group('value')
        else:
            tmp_value = tmp_line
        new_record += tmp_value

    new_env[key] = new_record

    return new_env 
