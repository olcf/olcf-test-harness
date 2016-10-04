#! /usr/bin/env python3

import argparse
import sys
import os
from libraries.application_metric import scalers 

def main():
    
    argv = sys.argv

    #----------------------------------
    # Create a parse for my arguments -
    #----------------------------------
    parser = create_a_parser()

    Vargs = parser.parse_args()

    application = str(Vargs.application[0])
    subtest = str(Vargs.test[0])
    id = str(Vargs.uniqueid[0])
    metric_name = str(Vargs.metric_name[0])
    units = str(Vargs.units[0])
    value =str(Vargs.value[0])

    metric = scalers.scalers(name_of_application = application,
                             name_of_subtest = subtest,
                             unique_id = id,
                             name_of_metric = metric_name,
                             metric_units = units,
                             metric_value = value)

    metric.recordMetric()

def create_a_parser():
    """Parses the arguments.

    Arguments:
    None

    Returns:
    An ArgParser object that contains the information of the 
    arguments.

    """
    parser = argparse.ArgumentParser(description="Records the current metric \
                                                  to a log file.",
                                     add_help=True)
        
    parser.add_argument("--application", nargs=1,required=True,
                        help="The name of the application.")
    
    parser.add_argument("--test", nargs=1,required=True,
                        help="The name of the application test ")

    parser.add_argument("--uniqueid", required=True,nargs=1,
                        help="The unique id of the test instance.")
    
    parser.add_argument("--metric_name", required=True,nargs=1,
                        help="The name of the metric")
    
    parser.add_argument("--value",required=True,nargs=1,
                        help="The actual value of the metric")
   
    parser.add_argument("--units", required=False,nargs=1,default="NO_UNITS",
                        help="The units of the metric")
   
    return parser

if __name__ == '__main__':
    main()
