#!/bin/bash

usage() {
    my_program=$1
    echo >&2 "USAGE: $my_program <rgt_test_input.txt> [<rgt_test_input.ini>]"
    echo >&2 "  - if output file (2nd parameter) omitted, contents will be generated to stdout"
    echo >&2 "This script converts legacy rgt_test_input.txt files into the current"
    echo >&2 "rgt_test_input.ini format when adapting legacy tests into a new system. "
}

if [[ $# -lt 1 || $# -gt 2 || $1 == "-h" ]]; then
    usage $(basename $0)
    exit 1
fi

input_file=$1
output_file=$2

#echo >&2 "DEBUG: input_file $input_file"
#echo >&2 "DEBUG: output_file $output_file"

if [[ ! -f $input_file ]]; then
    echo >&2 "ERROR: input file $input_file does not exist"
    exit 2
fi

if [[ -n $output_file ]]; then
    if [[ -f $output_file ]]; then
        echo >&2 "WARNING: output file $output_file exists and will be overwritten (backing up)"
        /bin/mv $output_file ${output_file}.bak
    fi
    exec 1>&$output_file # send stdout to output_file
fi

sed_substitutions='
s|batchfilename *=|batch_filename =|;
s|batchqueue *=|batch_queue =|;
s|buildcmd *=|build_cmd =|;
s|buildscriptname *=|build_cmd =|;
s|checkcmd *=|check_cmd =|;
s|checkscriptname *=|check_cmd =|;
s|executablename *=|executable_path =|;
s|jobname *=|job_name =|;
s|projectid *=|project_id =|;
s|reportcmd *=|report_cmd =|;
s|reportscriptname *=|report_cmd =|;
s|resubmitme *=|resubmit =|'

format_warn=0
if grep -q batchqueue "$input_file"; then
	echo "Specifying the batch queue per-test is no longer recommended."
	format_warn=1
fi
if grep -q projectid "$input_file"; then
	echo "Specifying the project ID per-test is no longer recommended."
	format_warn=1
fi

if [[ $format_warn -ne 0 ]]; then
	echo "These should instead be specified as default per machine or at runtime."
	echo "This allows the user to rely on the default or override per testshot."
	echo
fi
echo "Job script template #BSUB directives updates are needed as appropriate."
echo
echo "[Replacements]"
sed -e "$sed_substitutions" $input_file
