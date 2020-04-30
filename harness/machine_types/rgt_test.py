"""
.. module:: rgt_test
    :platform: Linux
    :synopsis: Abstracts the rgt_test_input.txt file.

"""
#
# Author: Veronica G. Vergara L.
#


class RgtTest():
    """ This class is the abstraction of rgt_test_input.txt file.

    """

    def __init__(self):
        self.__total_number_nodes = None
        self.__total_processes = None
        self.__processes_per_node = None
        self.__processes_per_socket = None
        self.__total_number_gpus = None
        self.__number_gpus_per_node =None
        self.__jobname = None
        self.__batchqueue = None
        self.__walltime = None
        self.__batchfilename = None
        self.__buildcmd = None
        self.__checkcmd = None
        self.__reportcmd = None
        self.__executablename = None
        self.__replacements = {}
        self.__env_vars = {}
        self.__template_dict = {}
        self.__builtin_dict = {}
        self.__builtin_params = {'total_processes',
                                 'processes_per_node',
                                 'processes_per_socket',
                                 'jobname',
                                 'batchqueue',
                                 'walltime',
                                 'batchfilename',
                                 'buildcmd',
                                 'checkcmd',
                                 'executablename',
                                 'reportcmd'}

    def set_test_parameters(self,
                            total_processes,
                            processes_per_node,
                            processes_per_socket,
                            jobname, batchqueue,
                            walltime,
                            batchfilename,
                            buildcmd,
                            checkcmd,
                            executablename,
                            reportcmd):
        self.__total_processes = total_processes
        self.__processes_per_node = processes_per_node
        self.__processes_per_socket = processes_per_socket
        self.__jobname = jobname
        self.__batchqueue = batchqueue
        self.__walltime = walltime
        self.__batchfilename = batchfilename
        self.__buildcmd = buildcmd
        self.__checkcmd = checkcmd
        self.__reportcmd = reportcmd
        self.__executablename = executablename

    def set_test_config_parameters(self, replacements):
        self.__replacements = replacements
        for k in replacements:
            v = replacements[k]
            print(k, v)
            if k == 'total_processes':
                self.__total_processes = v
            elif k == 'processes_per_node':
                self.__processes_per_node = v
            elif k == 'jobname':
                self.__jobname = v
            elif k == 'batchqueue':
                self.__batchqueue = v
            elif k == 'walltime':
                self.__walltime = v
            elif k == 'batchfilename':
                self.__batchfilename = v
            elif k == 'build_cmd':
                self.__buildcmd = v
            elif k == 'check_cmd':
                self.__checkcmd = v
            elif k == 'report_cmd':
                self.__reportcmd = v
            elif k == 'executablename':
                self.__executablename = v

    def set_test_config_env_vars(self, env_vars):
        self.__env_vars = env_vars
        for e in env_vars:
            v = env_vars[e]
            print(e, v)



    def set_custom_test_parameters(self,template_dict):
        self.__template_dict = template_dict
        for (k,v) in self.__template_dict.items():
            if k == 'total_processes':
                self.__total_processes = v
            elif k == 'processes_per_node':
                self.__processes_per_node = v
            elif k == 'jobname':
                self.__jobname = v
            elif k == 'batchqueue':
                self.__batchqueue = v
            elif k == 'walltime':
                self.__walltime = v
            elif k == 'batchfilename':
                self.__batchfilename = v
            elif k == 'build_cmd':
                self.__buildcmd = v
            elif k == 'check_cmd':
                self.__checkcmd = v
            elif k == 'report_cmd':
                self.__reportcmd = v
            elif k == 'executablename':
                self.__executablename = v

    def append_to_template_dict(self,k,v):
        self.__template_dict[k] = v

    def get_value_from_template_dict(self,k):
        return self.__template_dict[k]

    def check_builtin_parameters(self):
        if (not self.__jobname
           or not self.__batchqueue
           or not self.__walltime
           or not self.__batchfilename
           or not self.__buildcmd
           or not self.__checkcmd
           or not self.__reportcmd
           or not self.__executablename):
            print("")
            print("Required variable(s) missing!")
            print(" jobname = ",self.__jobname)
            print(" batchqueue = ",self.__batchqueue)
            print(" walltime = ",self.__walltime)
            print(" batchfilename = ",self.__batchfilename)
            print(" build_cmd = ",self.__buildcmd)
            print(" check_cmd = ",self.__checkcmd)
            print(" report_cmd = ",self.__reportcmd)
            print(" executablename = ",self.__executablename)

            exit(1)

    def get_replacements(self):
        return self.__replacements

    def get_env_vars(self):
        return self.__env_vars

    def get_template_dict(self):
        return self.__template_dict

    def get_batchfilename(self):
        return self.__batchfilename

    def get_buildcmd(self):
        return self.__buildcmd

    def get_checkcmd(self):
        return self.__checkcmd

    def get_reportcmd(self):
        return self.__reportcmd

    def get_executablename(self):
        return self.__executablename

    def get_jobname(self):
        return self.__jobname

    def get_walltime(self):
        return str(self.__walltime)

    def get_batchqueue(self):
        return self.__batchqueue

    def get_total_processes(self):
        return str(self.__total_processes)

    def get_processes_per_node(self):
        return str(self.__processes_per_node)

    def get_processes_per_socket(self):
        return str(self.__processes_per_socket)

    def print_custom_test_parameters(self):
        print("RGT Test Parameters")
        print("===================")
        for k in self.__template_dict:
            print(k,"=",self.__template_dict[k])

    def print_test_parameters(self):
        print("RGT Test Required Parameters")
        print("===================")
        print("jobname = " + self.__jobname)
        print("batchqueue = " + self.__batchqueue)
        print("walltime = " + str(self.__walltime))
        print("batchfilename = " + self.__batchfilename)
        print("build_cmd = " + self.__buildcmd)
        print("check_cmd = " + self.__checkcmd)
        print("report_cmd = " + self.__reportcmd)
        print("executablename = " + self.__executablename)

if __name__ == "__main__":
    print('This is the RgtTest class')
