import sys


def check_valid_python_version(): 
    minimal_version_for_this_package = (3,5) 
    version_message_frmt = "The current python version needs to be greater than or equal to python {major_version}.{minor_version}"
    if sys.version_info < minimal_version_for_this_package:
        message = version_message_frmt.format(major_version=minimal_version.minimal_version_for_this_package[0],
                                              minor_version=minimal_version.minimal_version_for_this_package[1])
        sys.exit(message)
