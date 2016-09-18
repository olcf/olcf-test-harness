#!/usr/bin/env bash

sphinx-apidoc -f -o source ../ ../RETIRED_nccs_test_harness_kepler_upgrade 
make html
