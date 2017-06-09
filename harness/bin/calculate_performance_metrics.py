#! /usr/bin/env python3

import os
import sys
import getopt
import argparse
import re



def main ():
    pass

def get_metric(path_to_correct_results,metric):
    correct_result = None
    filename = os.path.join(path_to_correct_results,metric)
    if os.path.isfile(filename):
        file_obj = open(filename,"r")
        records = file_obj.readlines()
        file_obj.close()

        for tmp_record in records:
            words = tmp_record.split()
            if words[0].strip() == "Metric_value":
                correct_result = words[2]

    return correct_result


if __name__ == "__main__":
    main()
