#! /usr/bin/env python3

# These strings define the tasks that the tests can do.
checkout = "check_out_tests"
starttest = "start_tests"
stoptest = "stop_tests"
displaystatus = "display_status"
summarize_results = "summarize_results"

def reorderTaskList(tasks):
    task_ordering = {
                      checkout: 1,
                      starttest: 2,
                      stoptest: 3,
                      displaystatus: 4,
                      summarize_results: 5
                    }
    result = sorted(tasks, key=lambda x: task_ordering[x])
    return result
