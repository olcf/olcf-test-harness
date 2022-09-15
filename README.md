README
=======

```
git clone gitlab@gitlab.ccs.ornl.gov:olcf-system-test/olcf-test-harness.git  
cd olcf-test-harness  
export OLCF_HARNESS_DIR=`pwd`  
module use $OLCF_HARNESS_DIR/modulefiles  
module load olcf_harness
export OLCF_HARNESS_MACHINE=<machine>
```

## How to use the OLCF harness with InfluxDB+Grafana
=================================================

## Outline:
1. Quick start
2. How to turn it on and off in a standard run           (--mode checkout start stop)
3. How to log to influx after a run has already finished (--mode influx_log)
4. Automatically calculated metrics


### 1. Quick start
Influx+Grafana has 2 key functionalities:

1. Harness event reporting (build_start, build_end, etc)
        - You can see a live stream of the harness events for your jobs online in an easy-to-navigate table
2. Metric reporting
        - You can see the resulting metrics from a harness app/test run in a dynamic graph
- To enable harness event reporting:
    - Prior to launch, set `RGT_INFLUX_URI` and `RGT_INFLUX_TOKEN` to the required values for your deployment
- To enable metric reporting:
    - Prior to launch, set `RGT_INFLUX_URI` and `RGT_INFLUX_TOKEN` to the required values for your deployment
    - In your application check/report scripts:
        - Write out a `metrics.txt` file that contains lines with the format outlined in section 2
        - That's it! Check the end of your job's output file to view logs pertaining to influxDB packets


### 2. How to turn it on and off in a standard run (--mode start stop)
- The InfluxDB+Grafana integration is controlled completely by these environment variables:
    - `RGT_DISABLE_INFLUX`
        - when set to 1, InfluxDB is "permanently" disabled for the current tests
            - so, if you run the harness with mode `influx_log` later, your test WONT be sent
    - `RGT_INFLUX_URI`, `RGT_INFLUX_TOKEN`
        - When both `RGT_INFLUX_URI` and `RGT_INFLUX_TOKEN` are specified, the harness will send data to Influx
    - If no environment variables are set, then the harness will behave exactly as pre-InfluxDB


- The harness needs a file named ``metrics.txt`` to parse the metrics from. Without ``metrics.txt``, the harness
  will print a warning to say the file was not found following the report stage
    - Valid lines are of the format:

```    
# This is a comment line
metric_name_1=value_1
# Spaces are valid, but will be replaced by underscores when sending to influx
metric name 2=value_2
# Whitespace before and after the equals signs (and metric names) is okay. Python str.strip() is used
metric_name_3 = value_3
metric_name_4\t=\tvalue_4
```    

### 3. How to log to influx after a run has already finished (--mode influx_log)
- InfluxDB logging also has an explicit harness run mode, ``influx_log``, which finds available (completed) harness
  tests from the rgt.inp and logs them to InfluxDB
    - ex: `runtests.py --mode influx_log -i rgt.inp`
    - The harness will parse rgt.inp as usual, and find all available tests to log. Available tests are those without
      either a `.influx_disabled` (created when test run with `RGT_DISABLE_INFLUX=1`)  or `.influx_logged` file

    - WARNING: By default, this will search through all Job IDs in the directory. There are several warnings with this:
        - If you run a test without logging to or disabling influx on Crusher, but run this mode from Frontier,
          any results from Crusher that hadn't been logged will show up as Frontier results.
        - If you ran tests that you didn't want to log, but didn't specify `RGT_DISABLE_INFLUX`, those tests will
          be picked up as well.

    - If you disabled Influx initially (`RGT_DISABLE_INFLUX`) you can undo that by removing the `.influx_disabled` file


### 4. Automatically calculated metrics
- When you have at least one metric (telling the harness you care about metric reporting for this test), the build
  time and execution time are automatically calculated and sent alongside your provided metrics
    - build_time = build_end - build_start (in seconds)
    - execution_time = executable_end - executable_start (in seconds)

